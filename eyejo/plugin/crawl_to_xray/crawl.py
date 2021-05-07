from projectApp.config import settings
from projectApp.utils import get_random_headers
import json
from projectApp.models import Login_site, Crawl
import re
from projectApp import utils
from django.db.utils import DataError
import asyncio
from django.db import close_old_connections
from django.db.utils import IntegrityError

logger = utils.get_logger()


class CrawlData:

    def __init__(self, task_id):
        self.task_id = task_id

    async def crawl(self, target_list, q=None):
        crawl_queryset = Crawl.objects.filter(task_id=self.task_id, url__in=target_list).values_list("url", flat=True).distinct()
        run_count = 0
        for target in target_list:
            run_count += 1
            logger.info(f"crawl--[{run_count}/{len(target_list)}] target is {target}")

            if target not in crawl_queryset:
                cmd = f"{settings.CRAWLERGO_PATH} -c {settings.CHROME_PATH} -t 10 --custom-headers '{json.dumps(get_random_headers())}' -o json {target}"
                proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                output, error = await proc.communicate()
                result = json.loads(output.decode().split("--[Mission Complete]--")[1])
                req_list = result["req_list"]
                # 去重
                new_req_list = []
                sorted_req_list = sorted(req_list, key=lambda x: x['data'], reverse=True)
                for x in sorted_req_list:
                    flag = 0
                    for y in new_req_list:
                        if x['url'] == y['url'] and x['method'] == y['method']:
                            if x['data'] in y['data']:
                                flag = 1
                            break
                        elif x['method'] == "POST" and x['data'] == "":
                            flag = 1
                    if flag == 0:
                        new_req_list.append(x)
                for x in new_req_list:
                    url = x['url']
                    method = x['method']
                    headers = json.dumps(x['headers'])
                    data = x['data']
                    try:
                        crawl_obj = Crawl.objects.create(task_id=self.task_id, url=target, crawl_url=url, method=method, headers=headers, req_data=data)
                        self.crawl_check_login(url, data, crawl_obj)
                    except DataError as e:
                        logger.warning("CrawlData.crawl function has raised a exception")
                        logger.exception(e)
            if q:
                if target == target_list[-1]:
                    await q.put([1, target, 'break'])
                else:
                    await q.put([0, target])
        close_old_connections()

    def crawl_check_login(self, url, data, crawl_obj):
        url_re_match = re.search(r'(/(\w+|)(admin|login|adm)(\w+|)\.(asp|aspx|php|php3|php4|php5|shtm|shtml|pht|phtm|phtml|asmx|asp|aspx|cgi|do|htm|html|jhtml|jsp|jspx|shtml))', url)
        data_re_match = re.search(r'(login|admin|user|passwd|password)', data)
        if data_re_match and any(x in data for x in ["register", "create"]):
            data_re_match = None

        if url_re_match or data_re_match:
            try:
                Login_site.objects.create(task_id=self.task_id, crawl_id=crawl_obj.id)
            except IntegrityError:
                pass
            crawl_obj.is_login = 1
            crawl_obj.save()
        close_old_connections()