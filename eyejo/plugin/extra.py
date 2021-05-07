import base64
import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
import yaml
from projectApp.models import C_net, Side_station
from projectApp import utils
from projectApp.utils import TargetHandle
from projectApp.config import settings
from projectApp.utils import get_random_headers
from django.db import close_old_connections

logger = utils.get_logger()


async def request(target_url):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as req_session:
        try:
            async with req_session.get(target_url, timeout=15, headers=get_random_headers()) as response:
                resp_text = await response.text(errors='replace')
                status_code = response.status
                soup = BeautifulSoup(resp_text, 'lxml')
                if soup.find('title'):
                    title = soup.find('title').text
                else:
                    title = "Title为空"
                return {'status_code': status_code, 'title': title}
        except aiohttp.client_exceptions.ClientConnectorSSLError:
            logger.warning(f"error target {target_url}")
            logger.warning(f'aiohttp ClientConnectorSSLError')
            return {False: 'ClientConnectorSSLError'}
        except aiohttp.client_exceptions.ClientConnectorError:
            logger.warning(f"error target {target_url}")
            logger.warning(f'aiohttp ClientConnectorError')
            return {False: 'ClientConnectorError'}
        except aiohttp.client_exceptions.ServerDisconnectedError:
            logger.warning(f"error target {target_url}")
            logger.warning(f'aiohttp ServerDisconnectedError')
            return {False: 'ServerDisconnectedError'}
        except aiohttp.client_exceptions.ClientResponseError:
            logger.warning(f"error target {target_url}")
            logger.warning(f'aiohttp ClientResponseError')
            return {False: 'ClientResponseError'}
        except aiohttp.client_exceptions.ClientOSError:
            logger.warning(f"error target {target_url}")
            logger.warning(f'aiohttp ClientOSError')
            return {False: 'ClientOSError'}
        except asyncio.exceptions.TimeoutError:
            logger.warning(f"error target {target_url}")
            logger.warning(f'aiohttp TimeoutError')
            return {False: 'TimeoutError'}


class SideStationInfo:
    """获取旁站信息"""
    def __init__(self, ip):
        self.ip = ip

    def info(self):
        # 默认使用搜索IP语法，判断是否使用自定义搜索语法
        keyword = f'ip="{self.ip}" && is_domain=true'
        # 目前搜索100条数目，最多可以搜索1w条
        page_num = 1
        query_size = 1000
        # query_size = 50

        with open(settings.SETTING_FILE) as f:
            yaml_configuration = yaml.safe_load(f)

        query = {'email': yaml_configuration['fofa_api']['email'],
                 'key': yaml_configuration['fofa_api']['key'],
                 'qbase64': base64.b64encode(keyword.encode('utf-8')),
                 'page': page_num,
                 'full': 'true',
                 'size': query_size,
                 'fields': 'host,ip,port,protocol'}
        fofa_api_url = "https://fofa.so/api/v1/search/all"
        s = requests.session()
        while True:
            resp = s.get(fofa_api_url, params=query, verify=False)
            resp_json = resp.json()
            size = resp_json.get('size')

            url_set = set()
            for host, ip, port, protocol in resp_json.get("results"):
                is_valid_d = TargetHandle.is_valid_domain(host)
                if is_valid_d:
                    domain = TargetHandle.match_target(host)
                    url_set.add(utils.port_relation(domain, port, protocol))
            self.main(url_set)
            if size < query_size:
                break
            page_num += 1

    async def request(self, url, semaphore):
        async with semaphore:
            resp_dict = await request(url)
            if resp_dict.get(False):
                Side_station.objects.update_or_create(ip_address=self.ip, subdomain=url, defaults={'title': "无法访问"})
            else:
                Side_station.objects.update_or_create(ip_address=self.ip, subdomain=url, defaults={'title': resp_dict.get('title')})
            close_old_connections()

    async def monitor(self, url_set):
        semaphore = asyncio.Semaphore(30)  # 限制并发量为5
        to_get = []
        for url in url_set:
            to_get.append(asyncio.create_task(self.request(url, semaphore)))
        if to_get:
            await asyncio.wait(to_get)

    def main(self, url_set):
        try:
            asyncio.run(self.monitor(url_set))
        except (KeyboardInterrupt, RuntimeError):
            for task in asyncio.Task.all_tasks():
                task.cancel()
        close_old_connections()


class CNetInfo:
    """获取C段信息"""
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.ip_c = f"{'.'.join(ip_address.split('.')[:3])}.0/24"

    async def request(self, ip_address, semaphore):
        async with semaphore:
            url = f'http://{ip_address}'
            resp_dict = await request(url)
            if resp_dict.get(False):
                C_net.objects.update_or_create(ip_address=ip_address, ip_c=self.ip_c, defaults={'title': "无法访问"})
            else:
                C_net.objects.update_or_create(ip_address=ip_address, ip_c=self.ip_c, defaults={'title': resp_dict.get('title')})
            close_old_connections()

    async def monitor(self):
        semaphore = asyncio.Semaphore(50)  # 限制并发量为5
        to_get = []
        for num in range(1, 255):
            ip_address = f"{'.'.join(self.ip_address.split('.')[:3])}.{num}"
            to_get.append(asyncio.create_task(self.request(ip_address, semaphore)))
        if to_get is not None:
            await asyncio.wait(to_get)

    def main(self):
        try:
            asyncio.run(self.monitor())
        except (KeyboardInterrupt, RuntimeError):
            for task in asyncio.Task.all_tasks():
                task.cancel()