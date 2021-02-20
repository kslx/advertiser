# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
# file: common_util.py
# @author: dkk
# @Software:PyCharm
# @time: 2020/8/27 17:54
# @desc: 公共类
"""
import datetime
import json
import random
import re
import requests
import time
import urllib3

from hashlib import md5
from os.path import abspath, dirname
from urllib3.exceptions import InsecureRequestWarning
from urllib.parse import quote, urlparse, urlencode, unquote


# 屏蔽ssl验证警告
urllib3.disable_warnings(InsecureRequestWarning)


class common_util(object):
    """公共工具类"""
    current_path = abspath(dirname(__file__))

    def send_get(self, url=None, headers=None, params=None, proxies=None, enc="utf-8", m=0, times=10):
        while times != 0:
            try:
                response = requests.get(url=url, headers=headers, params=params, proxies=proxies, timeout=10)
                response.encoding = enc
                if m == 0:
                    return response.text
                return json.loads(response.text)
            except:
                times -= 1

    def send_post(self, url=None, headers=None, data=None, proxies=None):
        try:
            response = requests.post(url=url, headers=headers, data=data, proxies=proxies, timeout=10)
            response.encoding = "utf-8"
            cont_html = response.text
            return cont_html
        except:
            return

    def get_ua(self):
        f = open(self.current_path + r"/conf/ua.json", encoding="utf-8")
        uas = json.load(f)["ua"]
        ua = random.choice(uas)
        return ua

    def get_proxy_ip(self):
        proxy_info = json.loads(requests.get("http://121.199.76.66:5010/get/").text)
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % proxy_info
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        proxy_info["proxies"] = proxies
        return proxy_info

    def get_url_site(self, url=None):
        """
        获取当前 url 的站点前缀
        如: https://www.baidu.com/dad/sda/das/da/ds
        [out] => https://www.baidu.com
        """
        rule = re.compile("(https?://.*?)/")
        res = rule.findall(url)
        return res[0] if res else None

    def get_domain_name(self, url=None):
        """
        获取当前 url 的站点域名
        如: https://www.baidu.com/dad/sda/das/da/ds
        [out] => https://www.baidu.com
        """
        # domain = urlparse(url).netloc
        # domain = tldextract.extract(url=url).domain
        domain = urlparse(url).hostname
        print(domain)

    def get_md5(self, text=None, case=0):
        """
        :param text: 待 加密 文本
        :param case: 0：原文；1：小写；2：大写
        :return:
        """
        if case == 0:
            res = md5(str(text).encode("utf-8")).hexdigest()
        elif case == 1:
            res = md5(str(text).lower().encode("utf-8")).hexdigest()
        else:
            res = md5(str(text).upper().encode("utf-8")).hexdigest()
        return res

    def get_current_time(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_mow_time(self):
        """获取当前系统时间，年月日 时分秒"""
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_now_timestamp(self, num=10):
        """
        :param num: 10、13、15
        :return: 返回当前时间10位、13位、15位时间戳
        """
        res = time.time()
        if num == 10:
            return int(res)
        if num == 13:
            return int(res*1000)
        if num == 15:
            return '%.5f' % res

    def get_timestamp_10(self):
        """返回10位时间戳"""
        return str(time.time()).split(".")[0]

    def get_timestamp_13(self):
        """返回13位当前时间的时间戳"""
        res = str(time.time()).split(".")
        return res[0] + res[1][:3]

    def get_timestamp_15(self):
        """返回13位当前时间的时间戳"""
        return '%.5f' % time.time()

    def get_url_json(self, url=None):
        query = urlparse(url).query
        path = urlparse(url).path + '?'
        return {i.split('=')[0]: i.split('=')[1] for i in query.split('&')}


if __name__ == '__main__':
    util = common_util()
