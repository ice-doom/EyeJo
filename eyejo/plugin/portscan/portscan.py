import nmap3
from projectApp.models import Port, IPAddress, Asset_task_relationship, Asset_group, IP_domain_relationship
from projectApp.utils import port_relation
from projectApp.config import settings
from django.db.utils import IntegrityError
from pandas import DataFrame
import json
from random import shuffle
import asyncio
import pathlib
import xml.etree.ElementTree as ET
import time
from django.db import close_old_connections
from projectApp import utils

logger = utils.get_logger()


class PortScan:
    def __init__(self, ip_set, port, project_id, asset_id, task_id=None):
        self.project_id = project_id
        self.asset_id = asset_id
        self.task_id = task_id
        self.nmap = nmap3.Nmap()
        # 端口类型
        self.gen_port = "21,22,23,80,389,443,512,873,1433,2082,2083,2181,2222,2375,2601,2604,3128,3306,3312,3311,3389,4440,6082,6379,7001,7778,8000,8080,9000,9060,9080,9200,10000,11211,27017,28017,50000,50030,50070"
        self.port = port
        self.web_port = True if ('80' in port.split(',') or '443' in port.split(',')) else False
        # IP列表打乱顺序
        self.ip_list = list(ip_set)
        self.len_target = len(ip_set)
        shuffle(self.ip_list)
        ipaddr_filter = IPAddress.objects.filter(project_id=self.project_id, ip_address__in=self.ip_list).values('id', 'ip_address')
        self.ip_id_dict = {x['ip_address']: x['id'] for x in ipaddr_filter.iterator()}
        ip_domain_rel_queryset = IP_domain_relationship.objects.filter(ip__project_id=self.project_id).values("ip__ip_address", "subdomain__subdomain")
        if ip_domain_rel_queryset.exists():
            ip_domain_rel_queryset_pd = DataFrame(ip_domain_rel_queryset)
            self.ip_domain_rel_dict = ip_domain_rel_queryset_pd.groupby('ip__ip_address')['subdomain__subdomain'].apply(
                lambda x: x.values.tolist()).to_dict()
        else:
            self.ip_domain_rel_dict = {}
        self.asset_group_queryset = Asset_group.objects.filter(asset_id=self.asset_id).values('id', 'url')

    async def naabu_scan(self, host, run_count):
        logger.info(f"naabu_scan--[{run_count}/{self.len_target}] target is {host}")

        result_port_list = []
        cmd = f"{settings.NAABU_PATH} -p {self.port} -s c -json -rate 500 {host}"
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        output, error = await proc.communicate()
        output_str = output.decode().split('\n')
        if output and len(output_str) > 1:
            for output_json in output_str[:-1]:
                port = str(json.loads(output_json)['port'])
                result_port_list.append(port)
                try:
                    Port.objects.create(ip_id=self.ip_id_dict.get(host), port=port)
                except IntegrityError:
                    continue

        if not result_port_list and self.web_port:

            if not self.ip_domain_rel_dict:
                url_list = [f'http://{host}']
            else:
                url_list = [f'http://{subdomain}' for subdomain in self.ip_domain_rel_dict.get(host)]
                url_list.append(f'http://{host}')

            Asset_group.objects.bulk_create(map(lambda subdomain_url: Asset_group(asset_id=self.asset_id, url=subdomain_url, status='inactivation'), url_list), ignore_conflicts=True)
            asset_group_dict = {asset_group_dict['url']: asset_group_dict['id'] for asset_group_dict in self.asset_group_queryset.filter(url__in=url_list).iterator()}
            Asset_task_relationship.objects.bulk_create(map(
                lambda url: Asset_task_relationship(asset_group_id=asset_group_dict.get(url), task_id=self.task_id), url_list), ignore_conflicts=True)
        elif not result_port_list:
            asset_obj = Asset_group.objects.create(asset_id=self.asset_id, url=host, status='unaccess')
            Asset_task_relationship.objects.create(asset_group_id=asset_obj.id, task_id=self.task_id)
        close_old_connections()
        return result_port_list

    def waf_port(self, port_list):
        gen_ports = self.gen_port.split(',')
        new_port_list = []
        for port in gen_ports:
            if port in port_list:
                new_port_list.append(port)
        return new_port_list

    async def nmap_scan(self, host, port_list, run_count):
        logger.info(f"nmap_scan--[{run_count}/{self.len_target}] target is {host}")

        if len(port_list) > 400:
            port_list = self.waf_port(port_list)
        if not pathlib.Path(settings.NMAP_RESULT_PATH).exists():
            pathlib.Path(settings.NMAP_RESULT_PATH).mkdir()

        result_file = f"{settings.NMAP_RESULT_PATH}/{int(time.time()*10000)}.xml"
        cmd = f"nmap {host} -p{','.join(port_list)} -sV -sT --open -Pn -oX {result_file}"
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        try:
            await proc.communicate()
            if pathlib.Path(result_file).exists():
                tree = ET.parse(result_file)

                for result in tree.iter('port'):
                    port = result.attrib.get('portid')
                    if list(result)[-1].tag == 'service' and list(result)[0].attrib.get('state') in ['open', 'filtered']:
                        protocol = list(result)[-1].attrib.get('name')
                        product = list(result)[-1].attrib.get('product')
                        version = list(result)[-1].attrib.get('version')
                        extrainfo = list(result)[-1].attrib.get('extrainfo')
                        tunnel = list(result)[-1].attrib.get('tunnel')
                        if tunnel:
                            protocol = f'{tunnel}/{protocol}'
                        Port.objects.update_or_create(ip_id=self.ip_id_dict.get(host), port=port, defaults={
                            'protocol': protocol,
                            'product': product,
                            'version': version,
                            'extrainfo': extrainfo})
                        if self.ip_domain_rel_dict == {}:
                            url_list = []
                        else:
                            url_list = [port_relation(subdomain, port, protocol) for subdomain in self.ip_domain_rel_dict.get(host)]
                        url_list.append(port_relation(host, str(port), protocol))
                        Asset_group.objects.bulk_create(map(lambda subdomain_url: Asset_group(asset_id=self.asset_id, url=subdomain_url), url_list), ignore_conflicts=True)
                        asset_group_dict = {asset_group_dict['url']: asset_group_dict['id'] for asset_group_dict in self.asset_group_queryset.iterator()}
                        Asset_task_relationship.objects.bulk_create(map(
                            lambda url: Asset_task_relationship(asset_group_id=asset_group_dict.get(url), task_id=self.task_id), url_list), ignore_conflicts=True)
                        port_list.remove(port)
                pathlib.Path(result_file).unlink()
        except asyncio.exceptions.TimeoutError:
            logger.warning(f'Error target, is Timeout')
            logger.warning(f'fail_target_host===========>{host}')
        finally:
            close_old_connections()
        # 将nmap没有扫描到的端口也更新到资产组中
        if len(port_list) <= 400:
            for port in port_list:
                if self.ip_domain_rel_dict == {}:
                    url_list = []
                else:
                    url_list = [port_relation(subdomain, port, "") for subdomain in self.ip_domain_rel_dict.get(host)]
                url_list.append(port_relation(host, str(port), ""))
                Asset_group.objects.bulk_create(
                    map(lambda subdomain_url: Asset_group(asset_id=self.asset_id, url=subdomain_url), url_list), ignore_conflicts=True)
                asset_group_dict = {asset_group_dict['url']: asset_group_dict['id'] for asset_group_dict in self.asset_group_queryset.iterator()}
                Asset_task_relationship.objects.bulk_create(map(
                    lambda url: Asset_task_relationship(asset_group_id=asset_group_dict.get(url), task_id=self.task_id), url_list), ignore_conflicts=True)

    async def port_scan(self, host, run_count, semaphore):
        async with semaphore:
            port_list = await self.naabu_scan(host, run_count)
            if port_list:
                await self.nmap_scan(host, port_list, run_count)

    async def monitor(self):
        to_get = []
        semaphore = asyncio.Semaphore(5)
        run_count = 0
        for ip in self.ip_list:
            run_count += 1
            to_get.append(asyncio.create_task(self.port_scan(ip, run_count, semaphore)))
        if to_get:
            await asyncio.wait(to_get)

    def run(self):
        try:
            asyncio.run(self.monitor())
        except (KeyboardInterrupt, RuntimeError):
            for task in asyncio.Task.all_tasks():
                task.cancel()
