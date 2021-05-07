import os
import psutil
from projectApp.config import settings
import ipaddress
from fake_useragent import UserAgent
import random
from celery.utils.log import get_task_logger


ua = UserAgent()
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/68.0',
    'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0']


def kill_process(signum='', frame='', pid=0):
    pid = pid or os.getpid()
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()


def check_black_ip(target):
    for ipc in settings.BLACK_IPS:
        if ipaddress.ip_address(target) in ipaddress.ip_network(ipc):
            return True
    return False


def check_private_ip(target):
    for ipc in settings.PRIVATE_IPS:
        if ipaddress.ip_address(target) in ipaddress.ip_network(ipc):
            return True
    return False


def get_random_headers():
    try:
        headers = {'User-Agent': ua.random}
    except Exception:
        headers = {'User-Agent': random.choice(user_agents)}
        headers['Accept-Encoding'] = 'gzip, deflate'
    return headers


def port_relation(target, port, protocol):
    if protocol == "https" or "ssl" in protocol:
        if port == '443':
            return "https://" + target
        return "https://" + target + ":" + port
    elif protocol not in ['', 'ftp', 'ssh', 'telnet', 'smtp', 'pop3', 'imap', 'microsoft-ds', 'ms-sql-s', 'oracle',
                          'mysql', 'ms-wbt-server', 'postgresql', 'vnc']:
        if port == '80':
            return "http://" + target
        return "http://" + target + ":" + port

    elif protocol == "" and port == '80':
        return "http://" + target
    elif protocol == "" and port == '443':
        return "https://" + target
    else:
        if port != '80' or port != '443':
            return target + ":" + port
        return target


def get_logger():
    task_logger = get_task_logger(__name__)
    return task_logger
