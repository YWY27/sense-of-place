import random
import re
import telnetlib
import time
from msilib.schema import Class
from unittest import result

import requests

class Proxies:
    def __init__(self):
        self.proxy_list = [];


    def get_proxy(self):
        proxy_list = []
        base_url = "http://www.66ip.cn/areaindex_35/1.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/81.0.4044.138 Safari/537.36',
            'Cookie': 'Hm_lvt_1761fabf3c988e7f04bec51acd4073f4=1595389409; '
                    'Hm_lpvt_1761fabf3c988e7f04bec51acd4073f4=1595397559 '
        }
        req1 = requests.get(url=base_url, headers=headers)
        patten = re.findall("<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>", req1.text)
        for index in range(1, len(patten)):
            proxy = patten[index]
            if proxy[0] + ':' + proxy[1] not in proxy_list:
                proxy_list.append(proxy[0] + ':' + proxy[1])
        return proxy_list

    def verify_proxy(self,proxy_list):
        t1 = time.perf_counter()

        for index,proxy in enumerate(proxy_list):
            try:                
                if requests.get('https://www.baidu.com',proxies={'http':proxy},timeout=3).status_code == 200:
                    print('这是第 {} 个代理， '.format(index) + proxy + ' is useful')
                    if proxy not in self.proxy_list:
                        self.proxy_list.append(proxy)       
            except:
                print('正在测试下一个代理，请稍后……')
            # finally:
            #     if proxy not in self.proxy_list:
            #         self.proxy_list.append(proxy)
        
        t2 = time.perf_counter()
        print('测试代理可用性总耗时 %f 秒。'%(t2-t1))

    def save_proxy(self):
        ippool = []
        for proxy in self.proxy_list:
            proxies = {'http':proxy}
            ippool.append(proxies)
        return ippool

def build_ippool():
    p = Proxies()
    results = []
    results = p.get_proxy()


    print('爬取到的代理数量: ',len(results))
    print('-------------------------------------\n开始验证……')

    p.verify_proxy(results)
    print('验证完毕，可用代理数量为: ',len(p.proxy_list))

    ippool = p.save_proxy()

    return ippool
        
if __name__ == '__main__':
    build_ippool()  
