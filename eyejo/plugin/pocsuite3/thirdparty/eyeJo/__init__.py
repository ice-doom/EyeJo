from urllib.parse import urlparse
import os


def parse_ip_port(url, default_port=0):
    '''将url格式数据转化成ip&port数据
    @param url string: URL
        url = https://x.x.x.x:8443
        url = https://x.x.x.x
        url = x.x.x.x
        url = x.x.x.x:80
    @return: (IP,Port)
    '''
    host, path = '', ''
    if '/' not in url:
        host = url
    else:
        if '://' not in url:
            host = url[:url.find('/')]
            path = url[url.find('/'):]
        else:
            host = urlparse(url).netloc
            path = url[url.find(host) + len(host):]

    if len(host) == 0:
        host = url

    if ":" in host:
        ip, port = host.split(":")
    else:
        ip = host
        # 预定义默认端口
        if 'https://' in url:
            port = 443
        elif 'http://' in url or host + '/' in url:
            port = 80
        else:
            port = default_port

    if '://' not in url:
        scheme = 'https' if default_port == 443 else 'http'
        url = '{}://{}:{}{}'.format(scheme, ip, port, path)

    return url, ip, int(port)


def make_verify_url(url, payload, mod=1):
    '''
    payload 样例：/index.php?id=xxxx

    构造固定uri漏洞url
    1，默认mod = 1返回根路径。
    2，当mod = 0 返回当前url路径。
    '''

    if payload and payload[0] != '/':
        payload = '/' + payload

    verify_url = ''
    url_obj = urlparse(url)
    if url_obj.scheme and url_obj.netloc:
        # URL当前路径处理
        if mod == 1:
            dir_path = os.path.dirname(url_obj.path)
            if dir_path == '/':
                dir_path = ''
            verify_url = url_obj.scheme + '://' + url_obj.netloc + dir_path + payload
        # URL根路径处理
        if mod == 0:
            verify_url = url_obj.scheme + '://' + url_obj.netloc + payload

    return verify_url
