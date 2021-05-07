import subprocess
from projectApp.config import settings
from projectApp.utils import kill_process
import gc
import time
import requests
from projectApp.models import Vulnerability, Task, Crawl
import json
from plugin.crawl_to_xray.crawl import CrawlData
from projectApp import utils
import pathlib
from django.db import close_old_connections
import asyncio

logger = utils.get_logger()


def xray_scan(task_name):
    try:
        if not pathlib.Path(settings.XRAY_REPORT_PATH).exists():
            pathlib.Path(settings.XRAY_REPORT_PATH).mkdir()

        if not pathlib.Path(f'{settings.XRAY_PATH}/ca.crt').exists():
            subprocess.getstatusoutput(f"cd {settings.XRAY_PATH} && {settings.XRAY_EXEC_PATH} genca")

        cmd = [settings.XRAY_EXEC_PATH, "--config", settings.XRAY_CONFIG_PATH, "webscan", "--listen", settings.XRAY_LISTEN, "--json-output", f"{settings.XRAY_REPORT_PATH}/{task_name}.json"]
        with open(f'{settings.XRAY_REPORT_PATH}/xray_stdout.log', 'w') as f:
            process = subprocess.Popen(cmd, stdout=f)
        return process
    except Exception as e:
        logger.exception(e)
        return


def delete_xray_process(process, in_read, last=False):
    fo = open(f'{settings.XRAY_REPORT_PATH}/xray_stdout.log', 'rb')
    if last:
        while True:
            time.sleep(2)
            fo.seek(-800, 2)
            fo_read = fo.read()
            if fo_read != in_read and b"All pending requests have been scanned" in fo_read:
                # 关闭xray被动代理,并删除进程变量，清除僵尸程序
                kill_process(pid=process.pid)
                del process
                gc.collect()
                fo.close()
                return fo_read
    else:
        while True:
            time.sleep(2)
            fo.seek(-800, 2)
            fo_read = fo.read()
            if fo_read != in_read and b"All pending requests have been scanned" in fo_read:
                return fo_read

async def crawl_to_xray(task_id, process, len_target, task_name, q):
    # 等待xray被动扫描进程启动
    run_count = 0
    tell_num = 0
    while True:
        _get = await q.get()
        start_time = time.time()
        run_count += 1
        logger.info(f"xray_scan--[{run_count}/{len_target}] target is {_get[1]}")
        crawl_filter = Crawl.objects.filter(task_id=task_id, url=_get[1])
        crawl_filter_count = crawl_filter.count()
        in_read = None
        num = 0
        fail_num = 0
        for count, crawl_obj in enumerate(crawl_filter.iterator()):
            try:
                if crawl_obj.method == "GET":
                    resp = requests.get(crawl_obj.crawl_url, headers=json.loads(crawl_obj.headers), verify=False, proxies=settings.REQ_PROXIES, timeout=20)
                    resp.close()
                    if resp.status_code == 502:
                        fail_num += 1
                elif crawl_obj.method == "POST":
                    resp = requests.post(crawl_obj.crawl_url, headers=json.loads(crawl_obj.headers), data=crawl_obj.req_data, verify=False, proxies=settings.REQ_PROXIES, timeout=20)
                    resp.close()
                    if resp.status_code == 502:
                        fail_num += 1
                end_time = time.time()
                # 超过30min自动退出
                if end_time - start_time > 1800:
                    logger.info('is timeout xray_scan')
                    # 关闭xray被动代理,并删除进程变量，清除僵尸程序
                    kill_process(pid=process.pid)
                    del process
                    gc.collect()
                    logger.info('finish xray_scan')
                    return
            except requests.exceptions.ReadTimeout:
                logger.warning("CrawlData.crawl_filter function has raised a exception")
                logger.warning(f"error target {crawl_obj.crawl_url}")
                logger.warning('crawl_to_xray ===> requests.exceptions.ReadTimeout')
                fail_num += 1
            except requests.exceptions.ConnectionError:
                logger.warning("CrawlData.crawl_filter function has raised a exception")
                logger.warning(f"error target {crawl_obj.crawl_url}")
                logger.warning('crawl_to_xray ===> requests.exceptions.ConnectionError')
                fail_num += 1
            except requests.exceptions.InvalidSchema:
                logger.warning("CrawlData.crawl_filter function has raised a exception")
                logger.warning(f"error target {crawl_obj.crawl_url}")
                logger.warning('crawl_to_xray ===> requests.exceptions.InvalidSchema')
                fail_num += 1
            # 到爬虫最后一个目标后，将xray被动扫描进程结束
            if count == crawl_filter_count-1 and _get[0] == 1:
                if (count - num) == (fail_num - 1):
                    delete_xray_process(process, in_read=None, last=True)
                else:
                    delete_xray_process(process, in_read, last=True)
            # 一次只发送100个给xray
            elif count % 100 == 0 and count != 0:
                if (count - num) != (fail_num - 1):
                    in_read = delete_xray_process(process, in_read)
                num = count
                fail_num = 0
        tell_num = save_vul(task_name, task_id, tell_num)
        if _get[0] == 1:
            logger.info('finish xray_scan')
            pathlib.Path(f"{settings.XRAY_REPORT_PATH}/{task_name}.json").unlink()
            close_old_connections()
            break


def save_vul(task_name, task_id, tell_num):
    if pathlib.Path(f"{settings.XRAY_REPORT_PATH}/{task_name}.json").exists():
        time.sleep(3)
        fo = open(f"{settings.XRAY_REPORT_PATH}/{task_name}.json", 'r')
        fo.seek(tell_num)
        _read = fo.read().strip('\n')
        tell_num = fo.tell()
        try:
            data = json.loads(_read + ']')
        except Exception:
            data = json.loads('[' + _read.lstrip(',') + ']')

        Vulnerability.objects.bulk_create(map(
            lambda x: Vulnerability(task_id=task_id, url=x['detail']['addr'], payload=x['detail']['payload'],
                                    snapshot_req=x['detail']['snapshot'][0][0], vulntype=x['plugin'],
                                    scan_name="xray"), data), batch_size=1000, ignore_conflicts=True)
        close_old_connections()
    return tell_num


async def monitor(task_id, target_list=None):
    task_name = Task.objects.get(id=task_id).name
    process = xray_scan(task_name)
    time.sleep(3)
    crawldata = CrawlData(task_id)
    queue = asyncio.Queue(maxsize=10)
    asyncio.create_task(crawldata.crawl(target_list, queue))
    proc_xray = asyncio.create_task(crawl_to_xray(task_id, process, len(target_list), task_name, queue))
    await proc_xray


def crawl_to_xray_main(task_id, target_list=None):
    try:
        asyncio.run(monitor(task_id, target_list))
    except (KeyboardInterrupt, RuntimeError):
        for task in asyncio.Task.all_tasks():
            task.cancel()



