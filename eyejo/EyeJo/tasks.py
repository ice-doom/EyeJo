import django
django.setup()
from EyeJo.celery import app
from projectApp.utils import TargetHandle
from projectApp.utils import kill_process
from projectApp.models import  Url_info, IP_domain_relationship, IPAddress, Asset_group, Project, Asset_task_relationship, Task, Asset
from plugin import subdomain_collect
from plugin.shodan_fofa import ShoDanFoFaSearch
from collections import defaultdict
from plugin.poc_verify import poc_files, poc_main
from plugin.portscan import portscan as pscan
from plugin.fuzz import fuzz_main
from plugin.requestsite.request_site_main import RequestSiteMain
from projectApp.config import settings
import requests
import signal
from plugin.crawl_to_xray.vul_xray import crawl_to_xray_main, CrawlData
import itertools
from plugin.brute_service.brute import brute_main
import time
from django.utils import timezone
from projectApp import utils
from django.db import connections
from django.db import close_old_connections
from django.db.utils import IntegrityError

logger = utils.get_logger()


class AllTask:
    def __init__(self, task_opts):
        self.request_form = task_opts['data']
        self.yaml_config = task_opts['yaml_config']
        self.scheme_target_dict = task_opts['scheme_target_dict']
        self.target_dict = task_opts['target_dict']
        self.project_id = task_opts['project_id']
        self.task_id = task_opts['task_id']
        self.project_name = Project.objects.get(id=self.project_id).name

        self.asset_name = task_opts.get('asset_name')
        self.asset_id = Asset.objects.get(project_id=self.project_id, name=self.asset_name or f'{self.project_name}-默认资产组').id

    # IP的城市信息
    def run_get_ip_country(self):
        logger.info('run ip_country')
        Task.objects.filter(id=self.task_id).update(status='ip_info_collect')
        start_time = time.time()

        if not self.asset_name:
            TargetHandle.GetIpInfo(self.scheme_target_dict, self.project_id, self.asset_id, self.yaml_config, self.task_id, self.request_form.get('option_port_scan')).main()
            if not self.request_form.get('option_port_scan'):
                for url in self.scheme_target_dict.get('domain')+self.scheme_target_dict.get('ip'):
                    try:
                        asset_group_obj = Asset_group.objects.create(asset_id=self.asset_id, url=url)
                        Asset_task_relationship.objects.create(asset_group_id=asset_group_obj.id, task_id=self.task_id)
                    except IntegrityError:
                        continue
        if not self.request_form.get('option_subdomain_collect'):
            ip_domain_relationship_filter = IP_domain_relationship.objects.filter(subdomain__project_id=self.project_id, ip__cdn__isnull=True).values('ip__ip_address', 'ip__asn', 'subdomain__cname')
            ipaddress_filter = IPAddress.objects.filter(project_id=self.project_id).values('ip_address', 'asn')
            TargetHandle.check_cdn(self.project_id, ip_domain_relationship_filter, ipaddress_filter)
        self.asset_group_filter_url = Asset_group.objects.filter(asset_id=self.asset_id).values_list('url', flat=True)
        close_old_connections()
        end_time = time.time() - start_time
        logger.info(f"finish ip_country_task time: {end_time}")

    def run_subdomain_collect(self):
        if self.request_form.get('option_subdomain_collect'):
            logger.info('run subdomain_collect')
            start_time = time.time()
            Task.objects.filter(id=self.task_id).update(status='subdomain_collect')
            subdomain_collect.main(self.target_dict.get('domain'), self.project_id, self.asset_id, self.task_id, self.yaml_config)

            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            ip_domain_relationship_filter = IP_domain_relationship.objects.filter(subdomain__project_id=self.project_id, ip__cdn__isnull=True).values('ip__ip_address', 'ip__asn', 'subdomain__cname')
            ipaddress_filter = IPAddress.objects.filter(project_id=self.project_id, cdn__isnull=True).values('ip_address', 'asn')
            TargetHandle.check_cdn(self.project_id, ip_domain_relationship_filter, ipaddress_filter)
            self.asset_group_filter_url = Asset_group.objects.filter(asset_id=self.asset_id).values_list('url', flat=True)

            end_time = time.time() - start_time
            logger.info(f"finish subdomain_collect_task time: {end_time}")

    def run_port_scan(self):
        if self.request_form.get('option_port_scan'):
            logger.info('run portscan')
            start_time = time.time()
            Task.objects.filter(id=self.task_id).update(status='port_scan')
            ip_all_list = IPAddress.objects.filter(project_id=self.project_id, ip_address__in=self.target_dict['ip'], cdn=0).values_list('ip_address', flat=True)
            if self.request_form.get('option_subdomain_collect'):
                m_domain_set = set()
                for domain in self.target_dict['domain']:
                    m_domain_set.add(TargetHandle.get_main_domain(domain))
                ip_domain_relationship_filter = IP_domain_relationship.objects.filter(
                        subdomain__project_id=self.project_id, subdomain__m_domain__in=m_domain_set,
                        ip__cdn=0).values_list('ip__ip_address', flat=True)
            else:
                ip_domain_relationship_filter = IP_domain_relationship.objects.filter(subdomain__project_id=self.project_id, subdomain__subdomain__in=self.target_dict['domain'], ip__cdn=0).values_list('ip__ip_address', flat=True)
            ip_all_set = set(itertools.chain(ip_all_list, ip_domain_relationship_filter))
            port = self.request_form.get('option_ports')
            pscan.PortScan(ip_all_set, port, self.project_id, self.asset_id, self.task_id).run()
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            asset_group_filter = Asset_group.objects.filter(asset_id=self.asset_id, status='inactivation')
            asset_group_filter_url = [x.url for x in asset_group_filter.iterator()]
            requestsitemain = RequestSiteMain(asset_group_filter_url, self.project_id, self.yaml_config, self.task_id, self.asset_name or f'{self.project_name}-默认资产组', self.asset_id, check_port=True)
            requestsitemain.main()
            self.asset_group_filter_url = Asset_group.objects.filter(asset_id=self.asset_id, asset_task_relationship__task_id=self.task_id, status__in=['uncheck', 'access']).values_list('url', flat=True)

            end_time = time.time() - start_time
            logger.info(f"finish portscan time: {end_time}")

    def run_shodan_fofa(self):
        if self.request_form.get('option_sf_info'):
            logger.info('run shodan_fofo')
            Task.objects.filter(id=self.task_id).update(status='shodan_fofa_collect')
            start_time = time.time()
            if self.yaml_config['fofa_api']['key']:
                url = f'https://fofa.so/api/v1/info/my?email={self.yaml_config["fofa_api"]["email"]}&key={self.yaml_config["fofa_api"]["key"]}'
                resp = requests.get(url, verify=False)
                if resp.json().get('error'):
                    end_time = time.time() - start_time
                    logger.warning(f"FOFA API密钥错误")
                    logger.info(f"finish shodan_fofo time: {end_time}")
                    return
            elif self.yaml_config['shodan_api']['key']:
                url = f'https://api.shodan.io/api-info?key={self.yaml_config["shodan_api"]["key"]}'
                resp = requests.get(url, verify=False)
                if resp.status_code == 401:
                    end_time = time.time() - start_time
                    logger.warning(f"Shodan API密钥错误")
                    logger.info(f"finish shodan_fofo time: {end_time}")
                    return
            else:
                end_time = time.time() - start_time
                logger.warning(f"Shodan、FOFA API为空")
                logger.info(f"finish shodan_fofo time: {end_time}")
                return
            sfs = ShoDanFoFaSearch(self.project_id, self.yaml_config, self.asset_id, self.task_id)
            if self.request_form.get('option_fofa_search'):
                sfs.fofa_api(self.request_form.get('option_fofa_search'), 1, 1, sf_info_s=True)
            else:
                m_domain_set = {TargetHandle.get_main_domain(x) for x in self.target_dict['domain']}
                len_domain = len(m_domain_set)
                run_count = 0
                for domain in m_domain_set:
                    run_count += 1
                    sfs.shodan_api(domain, run_count, len_domain)
                    sfs.fofa_api(domain, run_count, len_domain)
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            end_time = time.time() - start_time
            logger.info(f"finish shodan_fofo time: {end_time}")

    # 请求站点信息
    def run_requestsite(self):
        flag = 0
        # 判断未勾选截图
        if self.request_form.get('option_screen_info'):
            logger.info('run screen')
            Task.objects.filter(id=self.task_id).update(status='screen_info')
            start_time = time.time()
            asset_group_filter = Asset_group.objects.filter(asset__id=self.asset_id, url__startswith='http', asset_task_relationship__task_id=self.task_id, status__in=['uncheck', 'access'])
            if not self.asset_name and not self.request_form.get('option_port_scan'):
                asset_group_filter = Asset_group.objects.filter(asset__id=self.asset_id, url__in=self.scheme_target_dict['domain']+self.scheme_target_dict['ip'],
                                                                asset_task_relationship__task_id=self.task_id,
                                                                status__in=['uncheck', 'access'])
            asset_group_filter_url = [x.url for x in asset_group_filter]
            requestsitemain = RequestSiteMain(asset_group_filter_url, self.project_id, self.yaml_config, self.task_id, self.asset_name or f'{self.project_name}-默认资产组')
            requestsitemain.screen_main()
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()

            fail_all = Url_info.objects.filter(project_id=self.project_id, screen_status__in=['ScreenAsyncioTimeoutError', 'ScreenPageError']).values_list('url', flat=True)
            if fail_all.exists():
                logger.warning(f'Error screen target!')
                logger.warning(f'fail_screen_url===========>{fail_all}')
                fail_scheme_target_dict = TargetHandle.get_schema_target_dict(fail_all)
                fail_scheme_target_list = fail_scheme_target_dict['domain'] + fail_scheme_target_dict['ip']
                requestsitemain = RequestSiteMain(fail_scheme_target_list, self.project_id, self.yaml_config, self.task_id, self.asset_name or f'{self.project_name}-默认资产组')
                requestsitemain.main()
            flag = 1
            end_time = time.time() - start_time
            logger.info(f"finish screen time: {end_time}")

        # 判断未勾选请求站点
        elif self.request_form.get('option_request_site'):
            logger.info('run request_site')
            Task.objects.filter(id=self.task_id).update(status='request_site')

            start_time = time.time()
            asset_group_filter = Asset_group.objects.filter(asset__id=self.asset_id, url__startswith='http', asset_task_relationship__task_id=self.task_id)
            if not self.asset_name and not self.request_form.get('option_port_scan'):
                asset_group_filter = Asset_group.objects.filter(asset__id=self.asset_id, url__in=self.scheme_target_dict['domain']+self.scheme_target_dict['ip'],
                                                                asset_task_relationship__task_id=self.task_id,
                                                                status__in=['uncheck', 'access'])

            asset_group_filter_url = [x.url for x in asset_group_filter]
            requestsitemain = RequestSiteMain(asset_group_filter_url, self.project_id, self.yaml_config, self.task_id, self.asset_name or f'{self.project_name}-默认资产组')
            requestsitemain.main()
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            flag = 1
            end_time = time.time() - start_time
            logger.info(f"finish request_site time: {end_time}")

        if flag == 1:
            url_info_filter_status = Url_info.objects.filter(project_id=self.project_id).values('url', 'screen_status')
            url_info_filter_status_dict = {x['url']: x['screen_status'] for x in url_info_filter_status.iterator()}
            for assets_url in asset_group_filter:
                screen_status = url_info_filter_status_dict.get(assets_url.url)
                if screen_status:
                    if screen_status == 'success' or screen_status == 'false':
                        assets_url.status = 'access'
                    elif screen_status == 'ClientResponseError':
                        assets_url.url = assets_url.url.split('://')[-1]
                    else:
                        assets_url.status = 'unaccess'
            Asset_group.objects.bulk_update(asset_group_filter, ['status', 'url'], batch_size=1000)
            self.asset_group_filter_url = Asset_group.objects.filter(asset_id=self.asset_id,
                                                                     asset_task_relationship__task_id=self.task_id,
                                                                     status='access').values_list('url', flat=True)

    def poc_run(self):
        if self.request_form.get('option_poc_scan'):
            logger.info('run poc_scan')
            Task.objects.filter(id=self.task_id).update(status='poc_scan')

            start_time = time.time()
            pocs_list = self.request_form['option_pocss']
            url_poc_dict = defaultdict(list)
            verify_num = 0
            exists_poc_with_ext, dir_name = poc_files()
            url_info_filter = Url_info.objects.filter(project_id=self.project_id).values('url', 'finger')
            asset_group_filter_url = [url for url in self.asset_group_filter_url if url.startswith('http')]
            for url in asset_group_filter_url:
                url_finger = [x for x in url_info_filter.iterator() if url == x['url']]
                if url_finger and url_finger[0]['finger']:
                    for _path, _file_list in dir_name.items():
                        import itertools
                        out = list(itertools.chain.from_iterable(eval(url_finger[0]['finger']).values()))
                        if _path.lower() in map(str.lower, out):
                            verify_num = 1
                            for _file in _file_list:
                                poc_file = _path + '/' + _file
                                url_poc_dict[poc_file].append(url)
                            break
                if verify_num == 0:
                    for poc in pocs_list:
                        url_poc_dict[poc].append(url)
                else:
                    verify_num = 0
            poc_main(url_poc_dict, self.task_id)
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            end_time = time.time() - start_time
            logger.info(f"finish poc_scan time: {end_time}")

    def fuzz_run(self):
        if self.request_form.get('option_fuzz'):
            logger.info('start fuzz')
            Task.objects.filter(id=self.task_id).update(status='fuzz')
            start_time = time.time()
            asset_group_filter_url = [url for url in self.asset_group_filter_url if url.startswith('http')]
            fuzz_main(self.task_id, asset_group_filter_url, self.request_form.get('option_fuzz_file'))
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            end_time = time.time() - start_time
            logger.info(f"finish fuzz time: {end_time}")

    def identify_login(self):
        if self.request_form.get('option_identify_login'):
            logger.info('run identify_login')
            Task.objects.filter(id=self.task_id).update(status='identify_login')
            start_time = time.time()

            asset_group_filter_url = [url for url in self.asset_group_filter_url if url.startswith('http')]
            # http、https去重
            asset_group_filter_url = TargetHandle.crawl_remove_repeat(asset_group_filter_url)
            CrawlData(self.task_id).crawl(asset_group_filter_url)
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            end_time = time.time() - start_time
            logger.info(f"finish identify_login time: {end_time}")

    def vul_scan(self):
        if self.request_form.get('option_vul'):
            logger.info('run vul')
            Task.objects.filter(id=self.task_id).update(status='vul')
            start_time = time.time()

            asset_group_filter_url = [url for url in self.asset_group_filter_url if url.startswith('http')]
            # http、https去重
            asset_group_filter_url = TargetHandle.crawl_remove_repeat(asset_group_filter_url)
            crawl_to_xray_main(self.task_id, asset_group_filter_url)
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            end_time = time.time() - start_time
            logger.info(f"finish vul time: {end_time}")

    def brute_run(self):
        if self.request_form.get('option_brute'):
            logger.info('start brute')
            Task.objects.filter(id=self.task_id).update(status='brute')
            start_time = time.time()
            ip_set = set()
            for url in self.asset_group_filter_url:
                check_ip = TargetHandle.is_valid_ip(url)
                if check_ip:
                    ip_set.add(check_ip.get('new_target'))
            brute_service_list = self.request_form.get('option_brute_type').split(',')
            ipaddress_queryset = IPAddress.objects.filter(project_id=self.project_id, ip_address__in=ip_set, port__protocol__in=brute_service_list).values('ip_address', 'port__port', 'port__protocol')
            brute_main(ipaddress_queryset, self.task_id)
            # 检测数据库连接超时
            for conn in connections.all():
                try:
                    conn.is_usable()
                    close_old_connections()
                except AttributeError:
                    conn.connect()
            end_time = time.time() - start_time
            logger.info(f"finish brute time: {end_time}")

    def run(self):
        self.run_get_ip_country()
        self.run_subdomain_collect()
        self.run_shodan_fofa()
        self.run_port_scan()
        self.run_requestsite()
        self.poc_run()
        self.fuzz_run()
        self.identify_login()
        self.vul_scan()
        self.brute_run()


@app.task(name="EyeJoTask")
def task_func(task_opts):
    for conn in connections.all():
        conn.close()  # 关闭连接
        conn.connect()  # 重新建立
    signal.signal(signal.SIGTERM, kill_process)
    alltask = AllTask(task_opts)
    alltask.run()
    Task.objects.filter(id=task_opts.get('task_id')).update(status=settings.TaskStatus.DONE, end_time=timezone.now())

