from plugin.OneForAll.common.search import Search


class Sogou(Search):
    def __init__(self, domain):
        Search.__init__(self)
        self.domain = domain
        self.module = 'Search'
        self.source = 'SogouSearch'
        self.addr = 'https://www.sogou.com/web'
        self.limit_num = 1000  # 限制搜索条数

    def search(self, domain, filtered_subdomain=''):
        """
        发送搜索请求并做子域匹配

        :param str domain: 域名
        :param str filtered_subdomain: 过滤的子域
        """
        self.page_num = 1
        while True:
            self.header = self.get_header()
            self.proxy = self.get_proxy(self.source)
            word = 'site:.' + domain + filtered_subdomain
            payload = {'query': word, 'page': self.page_num,
                       "num": self.per_page_num}
            resp = self.get(self.addr, payload)
            subdomains = self.match_subdomains(resp, fuzzy=False)
            if not self.check_subdomains(subdomains):
                break
            self.subdomains.update(subdomains)
            self.page_num += 1
            # 搜索页面没有出现下一页时停止搜索
            if '<a id="sogou_next"' not in resp.text:
                break
            # 搜索条数限制
            if self.page_num * self.per_page_num >= self.limit_num:
                break

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.search(self.domain)

        # 排除同一子域搜索结果过多的子域以发现新的子域
        for statement in self.filter(self.domain, self.subdomains):
            self.search(self.domain, filtered_subdomain=statement)

        # 递归搜索下一层的子域
        if self.recursive_search:
            for subdomain in self.recursive_subdomain():
                self.search(subdomain)
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def run(domain):
    """
    类统一调用入口

    :param str domain: 域名
    """
    search = Sogou(domain)
    search.run()


if __name__ == '__main__':
    run('example.com')
