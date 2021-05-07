from projectApp.config import settings
from projectApp.models import Fuzz
import pathlib
import json
import time
from projectApp import utils
import collections
import asyncio
from itertools import takewhile, repeat
from django.db import close_old_connections

logger = utils.get_logger()


async def ffuf_run(task_id, target_url, fuzz_file, run_count, len_target, semaphore):
    async with semaphore:
        if not pathlib.Path(settings.FUZZ_RESULT_PATH).exists():
            pathlib.Path(settings.FUZZ_RESULT_PATH).mkdir()

        logger.info(f"fuzz--[{run_count}/{len_target}] target is {target_url}")
        result_file = f"{settings.FUZZ_RESULT_PATH}/{int(time.time()*10000)}.json"
        cmd = f"{settings.FUZZ_FFUF} -w {settings.FUZZ_PATH}/{fuzz_file} -o {result_file} -fc 404 -u {target_url}/FUZZ"
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        buffer = 1024 * 1024
        with open(f"{settings.FUZZ_PATH}/{fuzz_file}") as f:
            buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
            fuzz_num = sum(buf.count('\n') for buf in buf_gen)
        fuzz_timeout = int(fuzz_num/15)
        if fuzz_timeout < 100:
            fuzz_timeout = 100
        try:
            await asyncio.wait_for(proc.communicate(), timeout=fuzz_timeout)
            if pathlib.Path(result_file).exists():
                with open(result_file, 'r') as f:
                    result_json = json.loads(f.read()).get('results')

                result_filter_list = [(x.get('status'), x.get('words'), x.get('lines')) for x in result_json]
                duplicate = collections.Counter(result_filter_list)
                new_result_dict = []
                for result in result_json:
                    for result_filter, count in duplicate.items():
                        if count <= 5 and (result.get('status'), result.get('words'), result.get('lines')) == result_filter:
                            new_result_dict.append(result)

                for result in new_result_dict:
                    Fuzz.objects.create(task_id=task_id, url=target_url, fuzz_url=result['url'], status_code=int(result['status']), lines=int(result['lines']), words=int(result['words']))

                pathlib.Path(result_file).unlink()
        except asyncio.exceptions.TimeoutError:
            logger.warning(f'Error target, is Timeout')
            logger.warning(f'fail_target_url===========>{target_url}')
        finally:
            close_old_connections()


async def monitor(task_id, url_list, fuzz_file):
    to_get = []
    semaphore = asyncio.Semaphore(5)
    len_target = len(url_list)
    for num in range(len(url_list)):
        to_get.append(asyncio.create_task(ffuf_run(task_id, url_list[num], fuzz_file, num + 1, len_target, semaphore)))
    if to_get:
        await asyncio.wait(to_get)


def fuzz_main(task_id, url_list, fuzz_file):
    try:
        asyncio.run(monitor(task_id, url_list, fuzz_file))
    except (KeyboardInterrupt, RuntimeError):
        for task in asyncio.Task.all_tasks():
            task.cancel()