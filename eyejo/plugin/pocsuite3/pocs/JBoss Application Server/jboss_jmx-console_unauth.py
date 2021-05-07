#!/usr/bin/env python
# coding: utf-8
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
    name = '''jboss jmx-console 未授权访问'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''unauthorized-access'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''Jboss'''
    appVersion = '''all'''
    appPowerLink = '''jboss.org'''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 8080)
        result = {}
        vulurl = make_verify_url(self.url, '/jmx-console/', mod=0)
        resp = requests.get(vulurl, verify=False, timeout=15)
        if resp.status_code == 200 and b'JBoss JMX Management Console' in resp.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo']['port'] = port
        return self.parse_output(result)

    _attack = _verify

    def parse_output(self, result):
        #parse output
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet nothing returned')
        return output


register_poc(TestPOC)
