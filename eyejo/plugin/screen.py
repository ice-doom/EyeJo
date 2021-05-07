import asyncio, time, aiofiles
from pyppeteer import launch
import pyppeteer
from projectApp.models import Url_info, Tags
from projectApp.utils import TargetHandle
from projectApp.utils.get_certificate import get_https_cert
import hashlib
from plugin.requestsite.request_site import requestSite
from projectApp.utils import get_random_headers
from projectApp.config import settings
import json
from plugin.finger import FingerMap
from pyppeteer import launcher
# hook  禁用 防止监测webdriver
launcher.DEFAULT_ARGS.remove("--enable-automation")
from projectApp import utils
from django.db import close_old_connections

logger = utils.get_logger()


class newpage(object):
    def __init__(self, screen_opts):
        self.url = screen_opts['target_url']
        self.browser = screen_opts['chrome_browser']
        self.semaphore = screen_opts['semaphore']
        self.runtime_name = screen_opts['runtime_name']
        self.project_id = screen_opts['project_id']
        self.task_id = screen_opts['task_id']
        self.count = screen_opts['count']
        self.len_target = screen_opts['len_target']
        self.requestSite = requestSite({'runtime_name': self.runtime_name})
        self.max_tries = screen_opts['yaml_config']['screen']['max_tries']
        self.speed_type = screen_opts['yaml_config']['screen']['speed_type']
        self.file_name = self.url.strip('/').replace('://', '__').split('/')[0]
        self.tags = screen_opts['asset_name']
        self.base_url_info_dict = {
            'status_code': '',
            'icons': '',
            'icons_hash': '',
            'pic': f"plugin/screen_data/{self.runtime_name}/pic/{self.file_name}.png",
            'pic_hash': '',
            'title': '',
            'headers': '',
            'html': f"plugin/screen_data/{self.runtime_name}/html/{self.file_name}.html",
            'html_copyright': '',
            'ssl_Organization': '',
            'screen_status': 'success',
            'tags': self.tags
        }
        self.fingermap = FingerMap(self.project_id, self.task_id)

    async def run(self):
        async with self.semaphore:
            self.count += 1
            logger.info(f"screen--[{self.count}/{self.len_target}] target is {self.url}")
            page = await self.browser.newPage()
            page.setDefaultNavigationTimeout(15 * 1000)

            await page.setViewport({
                "width": 1920,
                "height": 1080
            })
            await page.setUserAgent(userAgent=get_random_headers()['User-Agent'])
            t1 = time.time()
            await page.evaluateOnNewDocument('''() => {
                Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
                })
                }
            ''')

            try:
                if self.speed_type == 'fast':
                    res = await asyncio.wait_for(page.goto(self.url, waitUntil=['networkidle2', 'load']), timeout=15)
                else:
                    res = await asyncio.wait_for(page.goto(self.url, waitUntil=['networkidle2'], timeout=1000 * 30), timeout=30)
                    await asyncio.wait([page.waitForNavigation({'timeout': 1000 * 10})])
                response_url = str(page.url)
                page_content = await page.content()

                self.base_url_info_dict['icons'], self.base_url_info_dict['icons_hash'] = await self.requestSite.get_icons(self.url, page_content, response_url)
                self.base_url_info_dict['html_copyright'] = await self.requestSite.get_copyright(page_content)
                await page.screenshot({'path': self.base_url_info_dict['pic']})
                self.base_url_info_dict['title'] = await page.title()
                try:
                    async with aiofiles.open(self.base_url_info_dict['html'], 'w') as f:
                        await f.write(page_content)
                    self.base_url_info_dict['status_code'] = str(res.status)

                    if res.headers.get('status'):
                        res.headers.pop('status')
                    self.base_url_info_dict['headers'] = json.dumps(res.headers)

                    logger.info(f'{self.url} status: {res.status}, time: {time.time() - t1}')
                except Exception as e:
                    logger.warning(f"error target {self.url}")
                    logger.exception(e)

                    request_dict = await self.requestSite.request(self.url)
                    if request_dict.get('resp_content'):
                        self.base_url_info_dict['headers'] = request_dict['headers']
                        self.base_url_info_dict['status_code'] = request_dict['status_code']

                async with aiofiles.open(self.base_url_info_dict['pic'], 'rb') as f:
                    _read = await f.read()
                m = hashlib.md5()
                m.update(_read)
                self.base_url_info_dict['pic_hash'] = m.hexdigest()

                # 截图空白则重新进行截图，等待时间会加上
                if self.base_url_info_dict['pic_hash'] == 'a0b905fc4cb1c6774e5727370e91ac2a' and self.max_tries > 0:
                    self.speed_type = 'normal'
                    self.max_tries -= 1
                    await self.run()
                hostname = TargetHandle.get_target(self.url).get('new_target')
                port = TargetHandle.get_target(self.url).get('port')
                if self.url.startswith('https'):
                    self.base_url_info_dict['ssl_Organization'] = get_https_cert(hostname, port)

                self.base_url_info_dict['pic'] = self.base_url_info_dict['pic'].replace('plugin/', '')
                self.base_url_info_dict['icons'] = self.base_url_info_dict['icons'].replace('plugin/', '')
                self.base_url_info_dict['finger'] = self.fingermap.finger_run(self.url, self.base_url_info_dict['html'], self.base_url_info_dict['headers'])
                url_info_obj, create = Url_info.objects.update_or_create(project_id=self.project_id, url=self.url, defaults={**self.base_url_info_dict})

            except asyncio.TimeoutError:
                logger.warning(f"error target {self.url}")
                logger.warning("asyncio.TimeoutError")
                url_info_obj, create = Url_info.objects.get_or_create(project_id=self.project_id, url=self.url, defaults={'screen_status': 'ScreenAsyncioTimeoutError', 'tags': self.tags})

            except pyppeteer.errors.PageError:
                logger.warning(f"error target {self.url}")
                logger.warning('pyppeteer.errors.PageError')
                url_info_obj, create = Url_info.objects.get_or_create(project_id=self.project_id, url=self.url, defaults={'screen_status': 'ScreenPageError', 'tags': self.tags})
            except pyppeteer.errors.TimeoutError:
                logger.warning(f"error target {self.url}")
                logger.warning('pyppeteer.errors.TimeoutError')
                url_info_obj, create = Url_info.objects.get_or_create(project_id=self.project_id, url=self.url, defaults={'screen_status': 'ScreenTimeoutError', 'tags': self.tags})
            except Exception as e:
                logger.warning(f"error target {self.url}")
                logger.exception(e)
            finally:
                try:
                    if create:
                        Tags.objects.create(name=self.tags, url_info_id=url_info_obj.id, project_id=self.project_id)
                    close_old_connections()
                    await page.close()
                except Exception as e:
                    logger.warning(f"error target {self.url}------------> close page")
                    logger.exception(e)


class Browser:
    async def kill(self):
        await self.browser.close()

    # 打开浏览器
    async def newbrowser(self):
        try:
            self.browser = await launch({
                'headless': True,             # 关闭无头模式
                'devtools': False,
                # 'timeout': 1000 * 5,
                'dumpio': True,               # 解决浏览器多开卡死
                'autoClose': True,
                'ignoreDefaultArgs': ['--enable-automation'],
                # 'userDataDir': './userdata',
                'handleSIGINT': False,
                'handleSIGTERM': False,
                'handleSIGHUP': False,
                'ignoreHTTPSErrors': True,
                'executablePath': settings.CHROME_PATH,
                'args': [
                    '--no-sandbox',  # --no-sandbox 在 docker 里使用时需要加入的参数，不然会报错
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-infobars',
                    '--ignore-certificate-errors',
                    '--ignore-ssl-errors',
                    '--hide-scrollbars',
                    '--disable-bundled-ppapi-flash',
                    '--mute-audio',
                    '--disable-setuid-sandbox',
                    '--disable-xss-auditor',
                    # '--proxy-server=127.0.0.1:8080'
                ]
            })
            return self.browser
        except BaseException as err:
            logger.exception(err)





