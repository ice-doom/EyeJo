from projectApp.models import Port, Subdomain, IP_domain_relationship, IPAddress, Asset_group, Asset_task_relationship
import requests as req
import base64
from projectApp.utils import TargetHandle
from projectApp import utils
from plugin.OneForAll.common.utils import match_subdomains
from django.db import close_old_connections
from django.db.utils import IntegrityError
from projectApp.utils import port_relation

logger = utils.get_logger()


class ShoDanFoFaSearch:
    def __init__(self, project_id, yaml_config, asset_id, task_id):
        self.project_id = project_id
        self.yaml_config = yaml_config
        self.asset_id = asset_id
        self.task_id = task_id

    def shodan_api(self, domain, run_count, len_domain):
        logger.info(f"shodan--[{run_count}/{len_domain}] target is {domain}")

        url = f'https://api.shodan.io/dns/domain/{domain}?key={self.yaml_config["shodan_api"]["key"]}'
        try:
            resp = req.get(url, verify=False, timeout=40)
            if resp.status_code == 401:
                return

            resp_json = resp.json()
            if resp_json.get('error'):
                logger.warning(f"error domain {domain}")
                logger.warning(f'shodan response error')
                return
            names = resp_json.get('subdomains')
            cname_dict = {x['subdomain']: x['value'] for x in resp_json['data'] if x['type'] == 'CNAME'}
            subdomain_str = str(set(map(lambda name: f'{name}.{domain}', names)))
            subdomains = match_subdomains(domain, subdomain_str)
            subdomains = {TargetHandle.get_target(subdomain).get('new_target') for subdomain in subdomains}
            domain_ip_dict = TargetHandle.iplist_get_a(subdomains)

            for subdomain in subdomains:
                cname = cname_dict.get(subdomain.replace(f'.{domain}', ''))
                if cname:
                    cname = cname.lower()
                subdomain_obj, subdomain_created = Subdomain.objects.get_or_create(project_id=self.project_id, subdomain=subdomain, m_domain=domain, defaults={'cname': cname})
                ip_list = domain_ip_dict.get(subdomain).get('ip') or []
                for ip in ip_list:
                    ipaddress_obj, ipaddress_created = IPAddress.objects.get_or_create(project_id=self.project_id, ip_address=ip)
                    if subdomain_created or ipaddress_created:
                        try:
                            IP_domain_relationship.objects.create(subdomain_id=subdomain_obj.id, ip_id=ipaddress_obj.id)
                        except IntegrityError:
                            continue

                url_list = [port_relation(host, '80', "") for host in [subdomain]+ip_list]
                Asset_group.objects.bulk_create(
                    map(lambda subdomain_url: Asset_group(asset_id=self.asset_id, url=subdomain_url), url_list), ignore_conflicts=True)
                asset_group_queryset = Asset_group.objects.filter(asset_id=self.asset_id).values('id', 'url')
                asset_group_dict = {asset_group_dict['url']: asset_group_dict['id'] for asset_group_dict in asset_group_queryset.iterator()}
                Asset_task_relationship.objects.bulk_create(
                    map(lambda url: Asset_task_relationship(asset_group_id=asset_group_dict.get(url), task_id=self.task_id), url_list), ignore_conflicts=True)

            ip_domain_relationship_filter = IP_domain_relationship.objects.filter(subdomain__project_id=self.project_id,
                                                                                  ip__cdn__isnull=True).values('ip__ip_address', 'ip__asn', 'subdomain__cname')
            ipaddress_filter = IPAddress.objects.filter(project_id=self.project_id, cdn__isnull=True).values('ip_address', 'asn')
            TargetHandle.check_cdn(self.project_id, ip_domain_relationship_filter, ipaddress_filter)

            close_old_connections()
        except req.exceptions.ConnectionError:
            logger.warning(f"error domain {domain}")
            logger.warning(f'requests.exceptions.ConnectionError')
        except req.exceptions.Timeout:
            logger.warning(f"error target {domain}")
            logger.warning(f'requests.exceptions.Timeout')

    def fofa_api(self, fofa_search, run_count, len_domain, sf_info_s=False):
        logger.info(f"fofa--[{run_count}/{len_domain}] target is {fofa_search}")

        # 默认使用搜索IP语法，判断是否使用自定义搜索语法
        if sf_info_s:
            keyword = fofa_search
        else:
            keyword = f'domain="{fofa_search}"'
        # 目前搜索100条数目，最多可以搜索1w条
        page_num = 1
        query_size = 1000
        # query_size = 50
        query = {'email': self.yaml_config['fofa_api']['email'],
                 'key': self.yaml_config['fofa_api']['key'],
                 'qbase64': base64.b64encode(keyword.encode('utf-8')),
                 'page': page_num,
                 'full': 'true',
                 'size': query_size,
                 'fields': 'host,ip,port,protocol'
                 }
        fofa_api_url = "https://fofa.so/api/v1/search/all"
        s = req.session()
        while True:
            resp = s.get(fofa_api_url, params=query, verify=False)
            resp_json = resp.json()
            if resp_json.get('error'):  # API的key错误停止后续操作
                break
            size = resp_json.get('size')
            subdomains = match_subdomains(fofa_search, resp.text)
            if not subdomains:  # 搜索没有发现子域名则停止搜索
                break
            self.fofa_save(resp_json.get("results"), fofa_search)
            if size < query_size:
                break
            page_num += 1

    def fofa_save(self, results, m_domain):
        # 进行排序,有protocol的放在后面,利用下面的更新库操作,来覆盖前面为空的情况
        new_results = sorted(results, key=lambda k: k[-1])

        domain_list = []
        for host, ip, port, protocol in new_results:
            is_valid_d = TargetHandle.is_valid_domain(host)
            if is_valid_d:
                domain_list.append(is_valid_d['new_target'])
        domain_cname_dict = TargetHandle.domain_list_get_cname(domain_list)

        for host, ip, port, protocol in new_results:
            # 获取子域名，入库
            ipaddress_obj, created = IPAddress.objects.get_or_create(project_id=self.project_id, ip_address=ip)
            is_valid_d = TargetHandle.is_valid_domain(host)
            if is_valid_d:
                tsubdomain_obj, subdomain_created = Subdomain.objects.get_or_create(project_id=self.project_id, subdomain=is_valid_d['new_target'], m_domain=m_domain, defaults={'cname': domain_cname_dict.get(is_valid_d['new_target'])})
                if subdomain_created or created:
                    try:
                        IP_domain_relationship.objects.create(subdomain_id=tsubdomain_obj.id, ip_id=ipaddress_obj.id)
                    except IntegrityError:
                        continue
            if protocol:
                Port.objects.update_or_create(port=port, ip_id=ipaddress_obj.id, defaults={'protocol': protocol})
            else:
                try:
                    Port.objects.create(port=port, ip_id=ipaddress_obj.id, protocol=protocol)
                except IntegrityError:
                    continue

            url_list = [port_relation(subdomain, port, protocol) for subdomain in [ip, TargetHandle.get_target(host)['new_target']]]
            Asset_group.objects.bulk_create(map(lambda subdomain_url: Asset_group(asset_id=self.asset_id, url=subdomain_url), url_list), ignore_conflicts=True)
            asset_group_queryset = Asset_group.objects.filter(asset_id=self.asset_id).values('id', 'url')
            asset_group_dict = {asset_group_dict['url']: asset_group_dict['id'] for asset_group_dict in asset_group_queryset.iterator()}
            Asset_task_relationship.objects.bulk_create(map(lambda url: Asset_task_relationship(asset_group_id=asset_group_dict.get(url),
                                                    task_id=self.task_id), url_list), ignore_conflicts=True)

        ip_domain_relationship_filter = IP_domain_relationship.objects.filter(subdomain__project_id=self.project_id,
                                                                              ip__cdn__isnull=True).values('ip__ip_address', 'ip__asn', 'subdomain__cname')
        ipaddress_filter = IPAddress.objects.filter(project_id=self.project_id, cdn__isnull=True).values('ip_address', 'asn')
        TargetHandle.check_cdn(self.project_id, ip_domain_relationship_filter, ipaddress_filter)

        close_old_connections()

