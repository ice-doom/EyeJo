import aiohttp, aiofiles, asyncio
import re, hashlib
from projectApp.utils import get_random_headers
from projectApp.utils import TargetHandle
from projectApp.config import settings
from bs4 import BeautifulSoup
import base64
from projectApp.models import Url_info, Asset_group, Tags
from projectApp.utils.get_certificate import get_https_cert
import json
from projectApp import utils
from plugin.finger import FingerMap
from django.db import close_old_connections

logger = utils.get_logger()


class requestSite():
    def __init__(self, request_site_opts):
        self.runtime_name = request_site_opts['runtime_name']
        self.project_id = request_site_opts.get('project_id')
        self.target_url = request_site_opts.get('target_url')
        self.count = request_site_opts.get('count')
        self.len_target = request_site_opts.get('len_target')
        self.semaphore = request_site_opts.get('semaphore')
        self.yaml_config = request_site_opts.get('yaml_config')
        self.task_id = request_site_opts.get('task_id')
        self.tags = request_site_opts.get('asset_name')
        self.fingermap = FingerMap(self.project_id, self.task_id)

    async def get_icons(self, target_url, page_content, response_url):
        m = hashlib.md5()
        match_icon_list = []
        request_dict = await self.request(response_url + "/favicon.ico")
        if request_dict.get('resp_content') and isinstance(request_dict.get('resp_content'), bytes):
            response_content = request_dict['resp_content']
            pic_type = response_content[:16].hex()
            ico_type = response_content[:4].hex()
            pic_type_lib = {
                'ffd8ffe000104a464946000101010060': '.jpg',
                '89504e470d0a1a0a0000000d49484452': '.png',
                '424d6a74000000000000360000002800': '.bmp'
            }
            ico_type_lib = {
                '00000100': '.ico'
            }
            if pic_type_lib.get(pic_type) or ico_type_lib.get(ico_type):
                m.update(response_content)
                icons_hash = m.hexdigest()
                icons = f"plugin/screen_data/{self.runtime_name}/icons/{target_url.replace('://', '__').strip('/').split('/')[0]}.ico"
                async with aiofiles.open(icons, 'wb') as f:
                    await f.write(response_content)
                return icons.split(settings.SCREEN_PATH)[-1], icons_hash

        soup = BeautifulSoup(page_content, 'lxml')
        find_icon_list = [soup.find_all(name='link', attrs={"rel": re.compile(r'[\s\w]*icon[\s\w]*')}),
                          soup.find_all(name='meta'),
                          soup.find_all(name='img', attrs={"src": re.compile(r'[\s\w]*logo[\s\w]*')})]
        imgdata = ""
        for find_icons in find_icon_list:
            for find_icon in set(find_icons):
                find_icon_href = find_icon.get('href')
                find_icon_content = find_icon.get('content')
                find_icon_src = find_icon.get('src')
                # 判断是否包含base64编码的图标
                if find_icon_href and ';base64,' in find_icon_href:
                    imgdata = base64.b64decode(find_icon_href.split(';base64,')[-1])
                # 判断 content 是否包含图片后缀的路径,尝试访问是否可以获取到图标
                for find_icon_index in [find_icon_content, find_icon_href, find_icon_src]:
                    if find_icon_index and any(
                            suffix in find_icon_index.lower() for suffix in ['.png', '.jpg', '.jpeg', '.bmp', '.ico']):
                        icons_url = find_icon_index.strip('/')
                        new_icons_url = TargetHandle.get_target(icons_url)
                        match_icon_list.append(
                            new_icons_url.get('scheme') + new_icons_url.get('new_target') + ':' + new_icons_url.get(
                                'port') + '/' + new_icons_url.get('path'))
                        response_url_s = response_url
                        icons_url_s = icons_url

                        re_match = re.findall('\.[a-zA-Z]+$', response_url)
                        if re_match:
                            response_url_s = response_url[:response_url.rindex('/')]
                        elif response_url.endswith('/#/'):
                            response_url_s = response_url.rstrip('/#/')
                        elif response_url.endswith('/'):
                            response_url_s = response_url.rstrip('/')
                        elif response_url.endswith('#'):
                            response_url_s = response_url.rstrip('/#')
                        if icons_url.startswith('/'):
                            icons_url_s = icons_url.lstrip('/')
                        match_icon_list.append(f"{response_url_s}/{icons_url_s.lstrip('/')}")
        if match_icon_list:
            for match_icon_url in match_icon_list:
                if imgdata:
                    break
                else:
                    request_dict = await self.request(match_icon_url)
                    if request_dict.get('resp_content') and isinstance(request_dict.get('resp_content'), bytes):
                        pic_type = request_dict.get('resp_content')[:16].hex()
                        ico_type = request_dict.get('resp_content')[:4].hex()
                        pic_type_lib = {
                            'ffd8ffe000104a464946000101010060': '.jpg',
                            '89504e470d0a1a0a0000000d49484452': '.png',
                            '424d6a74000000000000360000002800': '.bmp'
                        }
                        ico_type_lib = {
                            '00000100': '.ico'
                        }
                        if pic_type_lib.get(pic_type) or ico_type_lib.get(ico_type):
                            imgdata = request_dict['resp_content']
                            break
        if imgdata == "":
            return "", ""
        m.update(imgdata)
        icons_hash = m.hexdigest()
        icons = f"plugin/screen_data/{self.runtime_name}/icons/{target_url.replace('://', '__').strip('/').split('/')[0]}.ico"

        async with aiofiles.open(icons, 'wb') as f:
            await f.write(imgdata)
        return icons.split(settings.SCREEN_PATH)[-1], icons_hash

    async def get_copyright(self, resp):
        # 获取copyright
        # restr = '(©.*?)<'
        if isinstance(resp, bytes):
            resp = resp.decode()
        resp_content = re.sub(r"</?(.+?)>", "", resp)

        key_str_l = ["版权所有", "Copyright", "\d\d\d\d-\d\d\d\d"]
        sup_find_lst = ""
        for key_str in key_str_l:
            len_key_str = len(key_str)
            find_str_index = [i.start() for i in re.finditer(key_str, resp_content)]
            find_n_index = [i.start() for i in re.finditer("\n", resp_content)]
            if len(find_str_index) != 0 and len(find_n_index) != 0:
                right_find_n_index = [x for x in find_n_index if find_str_index[-1] < x]
                if right_find_n_index:
                    right_n_index = min(right_find_n_index, key=lambda x: abs(x - find_str_index[-1] - len_key_str))
                    abs_right_n_index = abs(right_n_index - find_str_index[-1] - len_key_str)
                    left_find_n_index = [x for x in find_n_index if find_str_index[-1] > x]
                    if left_find_n_index:
                        left_n_index = min(left_find_n_index, key=lambda x: abs(x - find_str_index[-1]))
                        abs_left_n_index = abs(left_n_index - find_str_index[-1])
                        if abs_right_n_index < 100:
                            right_len = abs_right_n_index - 1
                        elif abs_right_n_index >= 100 and len(resp_content) - find_str_index[-1] < 100:
                            right_len = len(resp_content) - find_str_index[-1]
                        else:
                            right_len = 100
                        if abs_left_n_index < 100:
                            left_len = abs_left_n_index - 1
                        elif abs_left_n_index >= 100 and find_str_index[-1] < 100:
                            left_len = len(resp_content) - find_str_index[-1]
                        else:
                            left_len = 100

                        find_lst = re.findall('.{%d}%s.{%d}' % (left_len, key_str, right_len), resp_content)
                        if len(find_lst) != 0:
                            sup_find_lst = re.findall(".*>(.*%s.*)<.*" % key_str, find_lst[-1])
                            if len(sup_find_lst) != 0:
                                break
                            sup_find_lst = re.findall(".*(.*%s.*)<.*" % key_str, find_lst[-1])
                            if len(sup_find_lst) != 0:
                                break
                            sup_find_lst = re.findall(".*>(.*%s.*).*" % key_str, find_lst[-1])
                            if len(sup_find_lst) != 0:
                                break
                            sup_find_lst = re.findall(".*(.*%s.*).*" % key_str, find_lst[-1])
                            if len(sup_find_lst) != 0:
                                break
        if sup_find_lst != "":
            return sup_find_lst[0]
        else:
            return ""

    async def request(self, target_url, max_tries=0):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as req_session:
            try:
                async with req_session.get(target_url, timeout=30, headers=get_random_headers()) as response:
                    resp_content = await response.read()
                    status_code = response.status
                    headers = json.dumps(dict(response.headers))
                    if response.headers.get('Content-Type') and 'image' not in response.headers.get('Content-Type'):
                        resp_content = await response.text(errors='replace')
                    return {'resp_content': resp_content, 'status_code': status_code, 'headers': headers,
                            'response_url': response.url}
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
                if max_tries > 0:
                    return await self.request(target_url, max_tries - 1)
                return {False: 'TimeoutError'}

    async def requestsite(self, asset_id, check_port):
        async with self.semaphore:
            self.count += 1
            logger.info(f"request_site--[{self.count}/{self.len_target}] target is {self.target_url}")

            request_dict = await self.request(self.target_url, self.yaml_config['request_site']['max_tries'])

            if request_dict.get('resp_content') is not None:
                title = ""
                ssl_Organization = ""
                html_file = f"plugin/screen_data/{self.runtime_name}/html/{self.target_url.replace('://', '__').strip('/').split('/')[0]}.html"

                async with aiofiles.open(html_file, 'w') as f:
                    if isinstance(request_dict['resp_content'], str):
                        await f.write(request_dict['resp_content'])

                soup = BeautifulSoup(request_dict['resp_content'], 'lxml')
                if soup.find('title'):
                    title = soup.find('title').text

                port = TargetHandle.get_target(self.target_url).get('port')
                icons, icons_hash = await self.get_icons(self.target_url, request_dict['resp_content'],
                                                         str(request_dict['response_url']))
                html_copyright = await self.get_copyright(request_dict['resp_content'])
                hostname = TargetHandle.get_target(self.target_url).get('new_target')

                if self.target_url.startswith('https'):
                    ssl_Organization = get_https_cert(hostname, port)

                icons = icons.replace('plugin/', '')
                finger_result = self.fingermap.finger_run(self.target_url, html_file, request_dict['headers'])
                url_info_obj, create = Url_info.objects.update_or_create(project_id=self.project_id,
                                                                         url=self.target_url,
                                                                         defaults={
                                                                             'status_code': request_dict['status_code'],
                                                                             'html': html_file,
                                                                             'icons': icons,
                                                                             'icons_hash': icons_hash,
                                                                             'title': title,
                                                                             'headers': request_dict['headers'],
                                                                             'html_copyright': html_copyright,
                                                                             'ssl_Organization': ssl_Organization,
                                                                             'screen_status': 'false',
                                                                             'finger': finger_result})
                if create:
                    Tags.objects.create(name=self.tags, url_info_id=url_info_obj.id, project_id=self.project_id)
                asset_group_status = 'access'
            else:
                url_info_obj, create = Url_info.objects.update_or_create(project_id=self.project_id,
                                                                         url=self.target_url,
                                                                         defaults={'screen_status': request_dict[False],
                                                                                   'tags': self.tags})

                if create:
                    Tags.objects.create(name=self.tags, url_info_id=url_info_obj.id, project_id=self.project_id)

                asset_group_status = 'comfirm_inactivation'

            if check_port:
                asset_group = Asset_group.objects.get(asset_id=asset_id, url=self.target_url)
                asset_group.status = asset_group_status
                asset_group.save()

            close_old_connections()

