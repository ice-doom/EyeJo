from projectApp.models import Subdomain, IPAddress, IP_domain_relationship, Asset_group, Asset_task_relationship
import sqlite3
from projectApp.utils import TargetHandle
from projectApp.config import settings
from plugin.OneForAll.oneforall import OneForAll
from projectApp.utils import check_black_ip
from projectApp import utils
from django.db import close_old_connections
from django.db.utils import IntegrityError

logger = utils.get_logger()


def main(domain_l, project_id, asset_id, task_id, yaml_config):
    for domain in domain_l:
        m_domain = TargetHandle.get_main_domain(domain)
        oneforall = OneForAll(target=m_domain)
        oneforall.req = False
        oneforall.run()
        try:
            conn = sqlite3.connect(f'{settings.basedir}/plugin/OneForAll/results/result.sqlite3')
            cur = conn.cursor()
            ip_list = []
            cur.execute(f"select subdomain,ip,cname,url from \"{m_domain.replace('.', '_')}\"")
            for row in cur:
                if row[2]:
                    cname = row[2].split(',')[0]
                else:
                    cname = ''
                new_target = TargetHandle.get_target(row[0]).get('new_target')
                if row[1]:
                    ipdict = {new_target: {'ip': [row[1]]}}
                else:
                    ipdict = TargetHandle.get_ipdict(row[0])
                    if ipdict == {}:
                        ipdict = {new_target: {'ip': []}}

                for ips in ipdict[new_target]['ip']:
                    subdomain = row[0]
                    subdomain = TargetHandle.get_www_domain(subdomain)
                    tsubdomain_obj, created = Subdomain.objects.update_or_create(project_id=project_id,
                                                                                 subdomain=subdomain, m_domain=m_domain,
                                                                                 defaults={"cname": cname})
                    for ip in ips.split(','):
                        if not check_black_ip(ip) and TargetHandle.is_valid_ip(ip):
                            url_dict = TargetHandle.get_target(row[3])
                            url = url_dict['scheme'] + url_dict['new_target']
                            if created:
                                try:
                                    asset_group_obj = Asset_group.objects.create(asset_id=asset_id, url=url)
                                    Asset_task_relationship.objects.create(asset_group_id=asset_group_obj.id, task_id=task_id)
                                except IntegrityError:
                                    continue

                            tipaddress_obj, created = IPAddress.objects.get_or_create(project_id=project_id, ip_address=ip)
                            IP_domain_relationship.objects.get_or_create(ip_id=tipaddress_obj.id, subdomain_id=tsubdomain_obj.id)
                            ip_list.append(ip)
            close_old_connections()
            cur.close()

            schema_target_dict = TargetHandle.get_schema_target_dict(ip_list, _input=False)
            TargetHandle.GetIpInfo(schema_target_dict, project_id, asset_id, yaml_config, task_id).main()
        except sqlite3.OperationalError as e:
            logger.warning(f"error target {domain}")
            logger.exception(e)

