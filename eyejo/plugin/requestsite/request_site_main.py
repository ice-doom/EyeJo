import asyncio
from plugin.screen import newpage, Browser
import time
from plugin.requestsite.request_site import requestSite
import os
from projectApp.config import settings
from projectApp import utils

logger = utils.get_logger()


class RequestSiteMain:

    def __init__(self, scheme_target_list, project_id, yaml_config, task_id, asset_name, asset_id=0, check_port=False):
        self.scheme_target_list = scheme_target_list
        self.request_site_opts = {
            'runtime_name': int(round(time.time() * 1000)),
            'project_id': project_id,
            'len_target': len(self.scheme_target_list),
            'yaml_config': yaml_config
        }
        self.task_id = task_id
        self.asset_name = asset_name
        self.asset_id = asset_id
        self.check_port = check_port

    async def monitor(self):
        to_get = []
        self.request_site_opts['semaphore'] = asyncio.Semaphore(self.request_site_opts['yaml_config']['request_site']['concurrent'])  # 限制并发量
        for count, target_url in enumerate(self.scheme_target_list):
            self.request_site_opts['target_url'] = target_url
            self.request_site_opts['count'] = count
            self.request_site_opts['task_id'] = self.task_id
            self.request_site_opts['asset_name'] = self.asset_name
            to_get.append(asyncio.create_task(requestSite(self.request_site_opts).requestsite(self.asset_id, self.check_port)))
        if to_get:
            await asyncio.wait(to_get)

    def main(self):
        os.makedirs("{}/{}/html".format(settings.SCREEN_PATH, self.request_site_opts['runtime_name']))
        os.makedirs("{}/{}/icons".format(settings.SCREEN_PATH, self.request_site_opts['runtime_name']))
        try:
            asyncio.run(self.monitor())
        except (KeyboardInterrupt, RuntimeError):
            for task in asyncio.Task.all_tasks():
                task.cancel()

    async def screen_monitor(self, browser):
        to_get = []
        chrome_browser = await browser.newbrowser()
        self.request_site_opts['semaphore'] = asyncio.Semaphore(self.request_site_opts['yaml_config']['screen']['concurrent'])  # 限制并发量
        self.request_site_opts['chrome_browser'] = chrome_browser
        self.request_site_opts['task_id'] = self.task_id
        self.request_site_opts['asset_name'] = self.asset_name

        for count, target_url in enumerate(self.scheme_target_list):
            self.request_site_opts['count'] = count
            self.request_site_opts['target_url'] = target_url
            to_get.append(asyncio.create_task(newpage(self.request_site_opts).run()))
        if to_get:
            await asyncio.wait(to_get)
            await chrome_browser.close()

    def screen_main(self):
        os.makedirs("{}/{}/html".format(settings.SCREEN_PATH, self.request_site_opts['runtime_name']))
        os.makedirs("{}/{}/pic".format(settings.SCREEN_PATH, self.request_site_opts['runtime_name']))
        os.makedirs("{}/{}/icons".format(settings.SCREEN_PATH, self.request_site_opts['runtime_name']))

        browser = Browser()
        try:
            asyncio.run(self.screen_monitor(browser))
        except (KeyboardInterrupt, RuntimeError):
            for task in asyncio.Task.all_tasks():
                task.cancel()
        logger.info('----关闭浏览器----')
        browser.kill()



