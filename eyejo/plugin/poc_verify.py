import os
from collections import defaultdict
from plugin.pocsuite3.api import init_pocsuite
from plugin.pocsuite3.api import start_pocsuite
from plugin.pocsuite3.api import get_results
from projectApp.models import Poc_check
import json
from django.db import close_old_connections
import asyncio
from projectApp import utils

logger = utils.get_logger()


def poc_files():
    POCS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pocsuite3/pocs')
    dir_name = defaultdict(list)
    exists_poc_with_ext = list(filter(lambda x: x not in ['__init__.py', '__init__.pyc'], os.listdir(POCS_PATH)))
    for root, dirs, files in os.walk(POCS_PATH):
        for _dir in dirs:
            for x in os.listdir(POCS_PATH + '/' + _dir):
                if x not in ['__init__.py', '__init__.pyc']:
                    dir_name[_dir].append(x)
    return exists_poc_with_ext, dir_name


async def run_pocsuite(poc, url, task_id, run_count, len_target, semaphore):
    async with semaphore:
        logger.info(f"run_pocsuite--[{run_count}/{len_target}] target is {url[0]}--{url[-1]}")
        config = {
            'url': url,
            'poc': poc,
            'threads': 5
        }
        init_pocsuite(config)
        start_pocsuite()
        results = get_results()
        new_results = []
        for result in results:
            if result['status'] == 'success':
                new_results.append(result)
        Poc_check.objects.bulk_create(
            map(lambda x: Poc_check(task_id=task_id, result_code=x['status'], poc_name=x['poc_name'], poc_url=x['url'], verifyinfo=json.dumps(x['result']['VerifyInfo'])), new_results), batch_size=1000, ignore_conflicts=True)
        close_old_connections()


async def monitor(url_poc_dict, task_id):
    to_get = []
    semaphore = asyncio.Semaphore(5)
    len_target = len(url_poc_dict)
    run_count = 0
    for poc, url in url_poc_dict.items():
        run_count += 1
        to_get.append(asyncio.create_task(run_pocsuite(poc, url, task_id, run_count, len_target, semaphore)))
    if to_get:
        await asyncio.wait(to_get)


def poc_main(url_poc_dict, task_id):
    try:
        asyncio.run(monitor(url_poc_dict, task_id))
    except (KeyboardInterrupt, RuntimeError):
        for task in asyncio.Task.all_tasks():
            task.cancel()


