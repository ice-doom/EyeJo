from IPy import IP
import tld
import requests
from projectApp.models import Subdomain, IPAddress, IP_domain_relationship, Asset_group, Asset_task_relationship
from projectApp.utils import get_random_headers
from collections import defaultdict
import tldextract
import re
import geoip2.database
from projectApp.config import settings
from dns.resolver import Resolver
from plugin.OneForAll.modules.iscdn import do_check
import concurrent.futures
from urllib.parse import urlparse
from projectApp.utils import check_private_ip
from projectApp import utils
import copy
from netaddr import IPNetwork

logger = utils.get_logger()


class GetIpInfo:
    def __init__(self, schema_target_dict, project_id, asset_id, yaml_config, task_id=None, option_port_scan=None):
        self.c_schema_target_dict = copy.deepcopy(schema_target_dict)
        self.project_id = project_id
        self.asset_id = asset_id
        self.task_id = task_id
        self.option_port_scan = option_port_scan
        self.get_ip_info_action = yaml_config['get_ip_info']['action']

    def ip_api_ipinfo(self, target_ip_nested_list):
        fail_ip_list = []
        for ip_list in target_ip_nested_list:
            data = str(ip_list).replace("'", '"')
            headers = get_random_headers()
            try:
                resp = requests.post(
                    "http://ip-api.com/batch?fields=city,country,query,regionName,status,isp,as&lang=zh-CN", timeout=15,
                    data=data, headers=headers)
                for resp_t in eval(resp.text):
                    if resp_t['status'] == 'success':
                        IPAddress.objects.update_or_create(project_id=self.project_id, ip_address=resp_t['query'],
                                                                                    defaults={'country': resp_t['country'],
                                                                                        'regionName': resp_t['regionName'],
                                                                                        'city': resp_t['city'],
                                                                                        'isp': resp_t['isp'],
                                                                                        'asn': resp_t['as'].split(' ')[0],
                                                                                        'flag': 1})
            except Exception:
                fail_ip_list.append(ip_list)
        return fail_ip_list

    def geoip2_ipinfo(self, target_ip_nested_list):
        for ip_list in target_ip_nested_list:
            try:
                for ip in ip_list:
                    # 当上面不可用时,使用 geoip2 获取IP城市相关信息
                    reader_city = geoip2.database.Reader(settings.GEOIP_CITY_PATH)
                    response_city = reader_city.city(ip)
                    resp_t = {
                        "city": response_city.city.name or "",
                        "regionName": response_city.subdivisions.most_specific.name or "",
                    }
                    # 获取IP ASN信息
                    try:
                        reader_asn = geoip2.database.Reader(settings.GEOIP_ASN_PATH)
                        response_asn = reader_asn.asn(ip)
                        resp_t["asn"] = f'AS{response_asn.autonomous_system_number}'
                        resp_t["isp"] = response_asn.autonomous_system_organization or ""
                    except geoip2.errors.AddressNotFoundError as e:
                        logger.warning(e)
                        resp_t["asn"] = ""
                        resp_t["isp"] = ""
                    # 获取IP国家信息
                    reader_country = geoip2.database.Reader(settings.GEOIP_COUNTRY_PATH)
                    response_country = reader_country.country(ip)
                    resp_t["country"] = response_country.country.names.get('zh-CN') or ""
                    IPAddress.objects.update_or_create(project_id=self.project_id, ip_address=ip, defaults={
                            'country': resp_t['country'], 'regionName': resp_t['regionName'],
                            'city': resp_t['city'],
                            'isp': resp_t['isp'], 'asn': resp_t['asn'], 'flag': 1})
            except geoip2.errors.AddressNotFoundError as e:
                logger.warning(e)

    def main(self):
        target_ip_set = set()
        step = 100
        if self.c_schema_target_dict.get('domain'):
            domain_ip_dict = iplist_get_a(self.c_schema_target_dict.get('domain'))
            domain_cname_dict = domain_list_get_cname(list(domain_ip_dict.keys()))

            for domain_ip_key, domain_ip_value in domain_ip_dict.items():
                target_ip_set.update(domain_ip_value.get('ip'))  # 解析的IP列表添加进target_ip_set
                m_domain = get_main_domain(domain_ip_key)
                tsubdomain_obj, created = Subdomain.objects.get_or_create(project_id=self.project_id,
                                                                          subdomain=domain_ip_key,
                                                                          m_domain=m_domain, defaults={'cname': domain_cname_dict.get(domain_ip_key)})
                for ip in domain_ip_value.get('ip'):
                    '''
                    处理IP和域名数据关系
                    '''
                    # if created:
                    if self.option_port_scan is None:
                        asset_group_obj, created = Asset_group.objects.get_or_create(asset_id=self.asset_id,
                                                                                     url=domain_ip_value.get('schema_target').replace(domain_ip_key, ip))
                        if self.task_id and created:
                            Asset_task_relationship.objects.create(asset_group_id=asset_group_obj.id, task_id=self.task_id)
                    ipaddress_obj, created = IPAddress.objects.get_or_create(project_id=self.project_id, ip_address=ip)
                    IP_domain_relationship.objects.get_or_create(ip_id=ipaddress_obj.id, subdomain_id=tsubdomain_obj.id)
        # 添加公网IP
        target_ip_set.update({get_target(self.c_schema_target_dict['ip'].pop(x)).get('new_target') for x in range(len(self.c_schema_target_dict['ip']) - 1, -1, -1) if not check_private_ip(get_target(self.c_schema_target_dict['ip'][x]).get('new_target'))})

        private_ip_list = [get_target(x).get('new_target') for x in self.c_schema_target_dict['ip']]
        IPAddress.objects.bulk_create(map(lambda private_ip: IPAddress(project_id=self.project_id, ip_address=private_ip), private_ip_list), batch_size=1000, ignore_conflicts=True)

        flag_ip_list = IPAddress.objects.filter(project_id=self.project_id, flag__gt=0).values_list('ip_address', flat=True)
        target_ip_list = [x for x in target_ip_set if x not in flag_ip_list.iterator()]
        target_ip_nested_list = [target_ip_list[i:i + step] for i in range(0, len(target_ip_list), step)]
        # 将目标分割100一个列表，通过api批量查询
        if self.get_ip_info_action == 'getlite2':
            self.geoip2_ipinfo(target_ip_nested_list)
        else:
            fail_ip_list = self.ip_api_ipinfo(target_ip_nested_list)
            if fail_ip_list:
                self.geoip2_ipinfo(fail_ip_list)


def get_ipdict(target):
    # 域名解析IP
    domain_ip_dict = defaultdict(dict)
    ip_dict = defaultdict(list)
    new_target = get_target(target)
    try:
        A = get_a(new_target.get('new_target'))
        if A is None:
            return {}
    except Exception:
        return {}
    for i in A.response.answer:
        for j in i.items:
            try:
                IP(str(j))
                ip_dict['ip'].append(str(j))
            except Exception:
                pass
    domain_ip_dict[new_target.get('new_target')].update(ip_dict)
    domain_ip_dict[new_target.get('new_target')].update({'schema_target': target})
    return domain_ip_dict


def iplist_get_a(target_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_ipdict, target) for target in target_list]
        domain_ip_dict = defaultdict(list)
        for future in concurrent.futures.as_completed(futures):
            domain_ip_dict.update(future.result())
            future.exception()
    return domain_ip_dict

def get_cnamedict(target):
    # 域名解析IP
    cname_dict = {}
    target_cname = get_cname(target)
    if target_cname:
        cname_dict[target] = target_cname
    else:
        cname_dict[target] = ''
    return cname_dict


def domain_list_get_cname(target_list):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_cnamedict, target) for target in target_list]
        domain_ip_dict = defaultdict(list)
        for future in concurrent.futures.as_completed(futures):
            domain_ip_dict.update(future.result())
            future.exception()
    return domain_ip_dict



def dns_resolver():
    """
    dns解析器
    """
    resolver = Resolver()
    resolver.nameservers = settings.resolver_nameservers
    resolver.timeout = settings.resolver_timeout
    resolver.lifetime = settings.resolver_lifetime
    return resolver


def get_cname(subdomain):
    resolver = dns_resolver()
    try:
        answers = resolver.query(subdomain, 'CNAME')
    except Exception:
        return None
    for answer in answers:
        return answer.to_text()  # 一个子域只有一个CNAME记录


def get_a(subdomain):
    resolver = dns_resolver()
    try:
        answers = resolver.query(subdomain, 'A')
        return answers
    except Exception:
        return None


def check_cdn(project_id, ip_domain_relationship_filter, ipaddress_filter):
    cdn_data_list = []
    for x in ip_domain_relationship_filter.iterator():
        cdn_data = {'cname': x['subdomain__cname'], 'header': {}, 'ip': x['ip__ip_address'], 'asn': x['ip__asn']}
        cdn_data_list.append(cdn_data)

    for x in ipaddress_filter.iterator():
        cdn_data = {'cname': "", 'header': {}, 'ip': x['ip_address'], 'asn': x['asn']}
        cdn_data_list.append(cdn_data)

    data = do_check(cdn_data_list)
    ip_list = [x.get('ip') for x in data]
    ipaddr_filter = IPAddress.objects.filter(project_id=project_id, ip_address__in=ip_list)
    for ip in ipaddr_filter:
        d = [y for y in data if y.get('ip') == ip and y.get('cdn') == 1]
        if d:
            ip.cdn = 1
        else:
            ip.cdn = 0

    IPAddress.objects.bulk_update(ipaddr_filter, ['cdn'], batch_size=1000)


def match_domain(target):
    ext = tldextract.extract(target.strip())
    m_domain = ext.registered_domain
    new_target = '.'.join(part for part in ext if part)
    if m_domain:
        return new_target
    return None


def match_target(target):
    ext = tldextract.extract(target.strip())
    m_domain = ext.registered_domain
    new_target = '.'.join(part for part in ext if part)
    if new_target == m_domain:
        return 'www.' + new_target
    else:
        return new_target


def get_main_domain(domain):
    # 以输入的当前域名作为主域名，wwww除外
    domain_parts, non_zero_i, _ = tld.utils.process_url(domain.strip(), fix_protocol=True, fail_silently=True)
    if domain_parts[0] == 'www':
        return ".".join(domain_parts[1:])
    return ".".join(domain_parts)


def get_www_domain(subdomain):
    m_domain = get_main_domain(subdomain)
    ext = tldextract.extract(subdomain.strip())
    registered_domain = ext.registered_domain
    if registered_domain == m_domain:
        subdomain = 'www.' + m_domain
    return subdomain


def get_target(target):
    get_target_dict = {}
    target_split = target.rsplit('/', 1)
    if target_split[0].find('://') != -1:
        match_t = target_split[0]
    else:
        match_t = target
    new_target = match_target(match_t)
    if new_target:
        if not target.startswith('http'):
            target_parse = urlparse(f'http://{target}')
        else:
            target_parse = urlparse(target)
            get_target_dict['scheme'] = f'{target_parse.scheme}://'
        get_target_dict['new_target'] = new_target
        port = target_parse.netloc.split(':')
        path = target_parse.path.lstrip('/')
        if path.isnumeric() and not target.startswith('http'):
            if int(path) > 32 or int(path) < 8:
                return {}

        get_target_dict['path'] = target_parse.path.rstrip('/')
        if len(port) > 1:
            get_target_dict['port'] = port[-1]
        else:
            if get_target_dict.get('scheme') == 'https://':
                get_target_dict['port'] = '443'
            else:
                get_target_dict['port'] = '80'

        if target_parse.scheme == '':
            if get_target_dict.get('port') == '443':
                get_target_dict['scheme'] = 'https://'
            else:
                get_target_dict['scheme'] = 'http://'
        elif get_target_dict.get('scheme') is None:
            get_target_dict['scheme'] = 'http://'
    return get_target_dict


def is_valid_ip(target, is_long=True):
    # 检验是否为IP
    re_target = target
    if is_long:
        target = get_target(target)
        if not target.get('new_target'):
            return False
        re_target = target.get('new_target')
    re_ip = re.compile('(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-4]|2[0-4]\d|[01]?\d?\d)$').match(re_target)
    if re_ip:
        return target
    return False


def is_valid_domain(target):
    # 检验是否为域名
    new_target = get_target(target)
    if new_target.get('new_target'):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
        )
        return new_target if pattern.match(new_target.get('new_target')) else False
    else:
        return False


def is_valid_ipc(target):
    # 检验是否为IP范围、并返回有效IP列表
    re_ips = re.compile('((?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-4]|2[0-4]\d|[01]?\d?\d)/(?:3[0-2]|[1-2][0-9]|[0-9]))$').match(target)

    if re_ips:
        target_ip_list = []
        for ip in IPNetwork(re_ips.group()):
            if str(ip).endswith('.0') or str(ip).endswith('.255'):
                continue
            target_ip_list.append(str(ip))
        return target_ip_list

    re_ipf = re.compile('((?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3})((?:25[0-4]|2[0-4]\d|[01]?\d?\d))-((?:25[0-4]|2[0-4]\d|[01]?\d?\d))$').match(target)
    if re_ipf:
        target_ip_list = []
        for ip_num in range(int(re_ipf.group(2)), int(re_ipf.group(3)) + 1):
            if ip_num == 0:
                continue
            target_ip_list.append(re_ipf.group(1) + str(ip_num))
        return target_ip_list
    return False


def get_schema_target_dict(target_list, _input=True):
    scheme_target_dict = defaultdict(set)
    scheme_target_dict.setdefault('domain', set())
    scheme_target_dict.setdefault('ip', set())
    for target in target_list:
        new_target_domain = []
        new_target_ip = []
        new_target_ip_list = []
        if _input:
            if is_valid_ip(target, is_long=False):
                new_target_ip = is_valid_ip(target)
            elif target.startswith('http'):
                new_target_domain = is_valid_domain(target)
                new_target_ip = is_valid_ip(target)
            else:
                new_target_ip_list = is_valid_ipc(target)
        else:
            new_target_domain = is_valid_domain(target)
            new_target_ip = is_valid_ip(target)
            new_target_ip_list = is_valid_ipc(target)
        if new_target_ip_list:
            for ip in new_target_ip_list:
                schema_domain = 'http://' + ip
                scheme_target_dict['ip'].add(schema_domain)
        elif new_target_domain:
            if new_target_domain['port'] == '443' or new_target_domain['port'] == '80':
                schema_domain = new_target_domain['scheme'] + new_target_domain['new_target'] + new_target_domain['path']
                scheme_target_dict['domain'].add(schema_domain.rstrip('/'))
            else:
                schema_domain = new_target_domain['scheme'] + new_target_domain['new_target'] + ':' + new_target_domain['port'] + new_target_domain['path']
                scheme_target_dict['domain'].add(schema_domain.rstrip('/'))
        elif new_target_ip:
            if new_target_ip['port'] == '443' or new_target_ip['port'] == '80':
                schema_ip = new_target_ip['scheme'] + new_target_ip['new_target'] + new_target_ip['path']
                scheme_target_dict['ip'].add(schema_ip.rstrip('/'))
            else:
                schema_ip = new_target_ip['scheme'] + new_target_ip['new_target'] + ':' + new_target_ip['port'] + new_target_ip['path']
                scheme_target_dict['ip'].add(schema_ip.rstrip('/'))
        elif target == "":
            continue
        else:
            return {False: target}

    scheme_target_dict['domain'] = list(scheme_target_dict['domain'])
    scheme_target_dict['ip'] = list(scheme_target_dict['ip'])

    return scheme_target_dict


def get_target_dict(target_list):
    target_dict = defaultdict(set)
    target_dict.setdefault('domain', set())
    target_dict.setdefault('ip', set())

    for target in target_list:
        new_target_domain = is_valid_domain(target)
        new_target_ip = is_valid_ip(target)
        new_target_ip_list = is_valid_ipc(target)

        if new_target_ip_list:
            for ip in new_target_ip_list:
                target_dict['ip'].add(ip)
        if new_target_domain:
            target_dict['domain'].add(new_target_domain['new_target'])
        elif new_target_ip:
            target_dict['ip'].add(new_target_ip['new_target'])
        elif target == "":
            continue
        else:
            return {False: target}
    target_dict['domain'] = list(target_dict['domain'])
    target_dict['ip'] = list(target_dict['ip'])
    return target_dict


def crawl_remove_repeat(url_list):
    for url in url_list:
        new_target = get_target(url)['new_target']
        if 'http://' + new_target in url_list and 'https://' + new_target in url_list:
            url_list.remove('https://' + new_target)
    return url_list

