from projectApp.config import settings
from projectApp.models import Brute
import json
import pathlib
import asyncio
from django.db import close_old_connections
from projectApp import utils

logger = utils.get_logger()


async def brute_force_run(data, task_id, run_count, len_target, semaphore):
    async with semaphore:
        logger.info(
            f"brute_force--[{run_count}/{len_target}] target is {data.get('ip_address')}:{data.get('port__port')}")
        modules = [
            ('ftp', 'ftp'),
            ('ssh', 'ssh'),
            ('telnet', 'telnet'),
            ('smtp', 'smtp'),
            ('pop3', 'pop3'),
            ('imap', 'imap'),
            ('microsoft-ds', 'smb'),
            ('ms-sql-s', 'mssql'),
            ('oracle', 'oracle'),
            ('mysql', 'mysql'),
            ('ms-wbt-server', 'rdp'),
            ('postgresql', 'postgresql'),
            ('vnc', 'vnc')
        ]
        available = dict(modules)
        service = available.get(data.get('port__protocol'))

        if not pathlib.Path(settings.BRUTE_RESULT).exists():
            pathlib.Path(settings.BRUTE_RESULT).mkdir()

        if service:
            cmd = f"hydra -C {settings.BRUTE_DICT}/{service}/{service}.txt -t 10 -s {data.get('port__port')} -o {settings.BRUTE_RESULT}/{data.get('ip_address')}_{service}.json -b json {data.get('ip_address')} {service}"
            proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE,
                                                         stderr=asyncio.subprocess.PIPE)
            result_file = f'{settings.BRUTE_RESULT}/{data.get("ip_address")}_{service}.json'
            try:
                output, error = await asyncio.wait_for(proc.communicate(), timeout=30 * 60)
                if output:
                    with open(result_file, 'r') as f:
                        results = json.load(f)
                    for result in results.get('results'):
                        Brute.objects.update_or_create(task_id=task_id, ip_address=result.get('host'),
                                                       port=result.get('port'),
                                                       defaults={'service': result.get('service'),
                                                                 'username': result.get('login'),
                                                                 'password': result.get('password')})
                    pathlib.Path(result_file).unlink()
            except asyncio.exceptions.TimeoutError:
                logger.warning(f'Error target, is Timeout')
                logger.warning(f"fail_target===========>{data.get('ip_address')}")
            finally:
                close_old_connections()
                if pathlib.Path(result_file).exists():
                    pathlib.Path(result_file).unlink()


async def monitor(ipaddress_queryset, task_id):
    to_get = []
    semaphore = asyncio.Semaphore(5)
    len_target = ipaddress_queryset.count()
    run_count = 0
    for data in ipaddress_queryset.iterator():
        run_count += 1
        to_get.append(asyncio.create_task(brute_force_run(data, task_id, run_count, len_target, semaphore)))
    if to_get:
        await asyncio.wait(to_get)


def brute_main(ipaddress_queryset, task_id):
    try:
        asyncio.run(monitor(ipaddress_queryset, task_id))
    except (KeyboardInterrupt, RuntimeError):
        for task in asyncio.Task.all_tasks():
            task.cancel()
