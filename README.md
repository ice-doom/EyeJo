# EyeJo
渗透自动化平台


### Shodan && FOFA

默认通过主域名去找相关资产，找到的域名不会进行存入该域名解析的IP，只会存入搜索得到的内容。
Shodan会通过主域名获取到相关子域名，存入库中
FOFA会通过主域名获取到相关子域名、IP、端口，存入库中


### 资产组

根据域名、IP、端口进行归入资产组

### POC

poc目录为 **plugin/pocsuite3/pocs**，存放方式为：**应用名字目录/poc名.py**

### 配置

```py
## 默认允许2个worker同时运行任务
censys_api_id = ''
censys_api_secret = ''

shodan_api_key = ''
fofa_api_email = ''
fofa_api_key = ''

'''爬取的路径会发送给POC进行扫描'''
crawl_to_poc = True

'''截图重试次数'''
screen_speed_type = 'fast'  # normal 正常/fast 快速
screen_max_tries = 1
request_site_max_tries = 0


'''获取IP信息'''
get_ip_info_action = 'getlite2'  # getlite2 使用getlite2库/ip-api 调用在线ip-api获取数据，消耗时间

```
