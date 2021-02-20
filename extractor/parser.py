# -*- coding: utf-8 -*-
import hashlib
import json
import urllib
import re
import requests
import time
import traceback

from lxml import etree
from tld import get_tld
from html import unescape
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from advertiserExtractor_time_new.extractor.extractor import Extractor


def write_info(path=None, text=None):
    with open(path + '.txt', 'a+', encoding="utf-8") as f:
        f.write(text + " " + "\n")


class Parser(object):

    def __init__(self, url, html):
        self.extractor = Extractor.create(url, html)
        self._title = self.extractor.title()
        self._content = self.extractor.content()
        self._url = self.extractor.url()
        self._encoding = self.extractor.encoding()
        self._kd = self.extractor.kd()
        self._description = self.extractor.description()
        self._icon = None
        self._brand = None
        self._category = None
        self._company = None
        self._iconmd5 = None
        self._cname = None
        self._ename = None
        self._host = None
        self._shop = None
        self._shopid = None
        self._advertiser = None
        self._identifier = None
        self._developer = None
        self.item = {}

    def get_url_parameter(self, url=None):
        """将链接转换成json格式"""
        return {i.split('=')[0]: i.split('=')[1] for i in urlparse(url).query.split('&')}

    def items(self):
        self.item['brand'] = self._brand
        self.item['kd'] = self._kd
        self.item['description'] = self._description
        self.item['icon'] = self._icon
        self.item['iconmd5'] = self._iconmd5
        self.item['shop'] = self._shop
        self.item['host'] = self._host
        self.item['company'] = self._company
        self.item['title'] = self._title
        self.item['category'] = self._category
        self.item['url'] = self._url
        self.item['cname'] = self._cname
        self.item['ename'] = self._ename
        self.item['content'] = self._content
        self.item['advertiser'] = self._advertiser
        self.item['identifier'] = self._identifier
        self.item['developer'] = self._developer
        return self.item

    def download(self, url):
        return self.extractor.download(url)

    def download_pic(self, url, filename):
        self.extractor.download_pic(url, filename)

    def data_md5(self, data):
        m2 = hashlib.md5()
        m2.update(data)
        return m2.hexdigest()

    def get_domain(self, url):
        domain = None
        try:
            res = get_tld(url, as_object=True)
            domain = res.fld
        except:
            pass
        return domain

    def getSoup(self, html):
        return BeautifulSoup(html, "lxml")

    def getHtml(self, text):
        return unescape(text)

    def is_alphabet(self, uchar):
        self.extractor.is_alphabet(uchar)

    def findElement(self, text, xpath):
        tree = etree.HTML(text)
        datas = tree.xpath(xpath)
        data = datas[0] if datas else ""
        return data

    def findElements(self, text, xpath):
        tree = etree.HTML(text)
        datas = tree.xpath(xpath)
        if datas:
            return datas

    def fetch(self, url, id, retries=3):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'accept': '*/*',
            'Host': 'tmallequity.taobao.com',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        time.sleep(1)
        headers['referer'] = f'https://equity-vip.tmall.com/agent/mobile.htm?tbpm=3&agentId={id}&_bind=true&ali_trackid=63_0bb48dc700007a215c426c6c007e4715'
        content = None
        try:
            request = requests.get(url, headers=headers, timeout=10)
            content = request.text
        except:
            if retries > 0:
                return self.fetch(url, id, retries - 1)
        return content

    @staticmethod
    def create(url, html):
        parser = urlparse(url)
        host = parser.hostname
        domain = get_tld(url, as_object=True).fld
        if host == 'detail.m.tmall.com' or host == 'detail.tmall.com' or host == 'content.tmall.com' or host == 'equity-vip.tmall.com' or url.count(
                'tmall.com') > 0:
            extractor = TMallExtractor(url, html)
        elif host == 'item.jd.com' or host == 'm.jd.com' or host == 'mall.jd.com' or host == 'item.jd.hk' or url.count(
                'jd.com'):
            extractor = JDExtractor(url, html)
        elif host == 'shop.suning.com' or host == 'product.suning.com' or host == 'shop.m.suning.com' or host == 'm.suning.com':
            extractor = SuNingExtractor(url, html)
        elif host == 'apps.apple.com' or host == 'itunes.apple.com':
            extractor = AppleExtractor(url, html)
        elif host == 'android.myapp.com':
            extractor = MyAppExtractor(url, html)
        elif host == 'item.yhd.com' or host == 'mall.yhd.com':
            extractor = YHDExtractor(url, html)
        elif host == 'app.mi.com':
            extractor = MiExtractor(url, html)
        elif host == "haohuo.jinritemai.com" or host == "www.jinritemai.com" or host == "clue.jinritemai.com":
            extractor = JinRiTeMaiExtractor(url, html)
        elif domain in ["fyeds0.com", "fyeds1.com", "fyeds2.com", "fyeds3.com", "fyeds4.com", "fyeds5.com",
                        "fyeds6.com", "fyeds7.com", "fyeds8.com", "fyeds9.com"]:
            extractor = FYEDSExtractor(url, html)
        elif "qq.com" in url:
            extractor = QQExtractor(url, html)
        elif host == "haohuo.jinritemai.com" or host == "www.jinritemai.com" or host == "clue.jinritemai.com":
            extractor = JinRiTeMaiExtractor(url, html)
        else:
            extractor = OtherExtractor(url, html)
        return extractor


class WebsiteExtractor(Parser):

    def __init__(self, url, html):

        Parser.__init__(self, url, html)


class TMallExtractor(WebsiteExtractor):

    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        crawlUrl = ''
        redirect_url = ''
        if html is None:
            r = requests.get(self._url, allow_redirects=True)
            html = str(r.content, encoding='gbk')
        try:
            if html.count('您查看的商品找不到了') == 0 and html.count('没有找到相应的店铺信息') == 0:
                if host == 'equity-vip.tmall.com':
                    if self._url.count('&_bind=true') > 0:
                        id = re.findall('agentId=(.*?)&_bind', self._url, re.I)[0]
                    else:
                        id = re.findall('agentId=(.*?)', self._url, re.I)[0]
                    url_ = f'https://tmallequity.taobao.com/agent/linkAnalysis.do?tbpm=3&agentId={id}&_bind=true&ali_trackid=63_0bb48dc700007a215c426c6c007e4715&callback=jsonp_34326624'
                    content = self.fetch(url_, id).replace('jsonp_34326624(', '').replace(');', '')
                    if json.loads(content)['status'] == 200:
                        redirect_url = json.loads(content)['data']['normalLink']
                if redirect_url:
                    parser = urlparse(redirect_url)
                    host = parser.hostname
                else:
                    redirect_url = self._url
                    parser = urlparse(redirect_url)
                    host = parser.hostname
                if host == 'detail.tmall.com' or host.count('detail.m.tmall.com'):
                    if host.count('detail.m.tmall.com'):
                        crawlUrl = redirect_url.replace('detail.m.tmall.com', 'detail.tmall.com')
                    else:
                        crawlUrl = self._url
                elif host == 'content.tmall.com':
                    info_urls = self.findElements(html, '//a/@href')
                    for i_url in info_urls:
                        if i_url.count('detail.tmall.com'):
                            crawlUrl = 'https:' + i_url
                            break
                else:
                    if host.count('.m.tmall.com'):
                        redirect_url = redirect_url.replace('.m.tmall.com', '.tmall.com')
                        text = self.download(redirect_url)
                        info_urls = self.findElements(text, '//a/@href')
                        for i_url in info_urls:
                            if i_url.count('detail.tmall.com'):
                                crawlUrl = 'https:' + i_url
                                break
                    else:
                        info_urls = self.findElements(html, '//a/@href')

                        for i_url in info_urls:
                            if i_url.count('detail.tmall.com'):
                                crawlUrl = 'https:' + i_url
                                break

                if not crawlUrl:
                    info_urls = self.findElements(html, '//area/@href')
                    for i_url in info_urls:
                        if i_url.count('detail.tmall.com'):
                            crawlUrl = i_url
                            break
                if not crawlUrl.startswith('http'):
                    crawlUrl = 'https:' + crawlUrl

                text = self.download(crawlUrl)

                self._shop = self.findElement(text, '//a[@class="slogo-shopname"]/strong/text()')
                if text.count('id="J_attrBrandName"'):
                    self._brand = self.findElement(text, '//li[@id="J_attrBrandName"]/text()').replace('品牌: ', '')
                else:
                    brand = re.findall('品牌</th><td>(.*?)</td>', text, re.I)
                    if brand:
                        self._brand = brand[0].replace('&nbsp;', '')

                self._identifier = self.findElement(text, '//a[@class="slogo-shopname"]/@href').replace('//', '')
                if self._brand:
                    if self._brand.count('/') > 0:
                        self._ename = self._brand.split('/')[0]
                        self._cname = self._brand.split('/')[1]
                    else:
                        if self.is_alphabet(self._brand.encode('unicode_escape').decode()):
                            self._ename = self._brand
                        else:
                            self._cname = self._brand
                if self._identifier:
                    item['identifier'] = self._identifier
                    item['host'] = self._identifier
                else:
                    item['identifier'] = host
                    item['host'] = self._identifier

                item['shop'] = self._shop
                item['brand'] = self._brand
                item['url'] = self._url
                item['cname'] = self._cname
                item['ename'] = self._ename
            else:
                item['identifier'] = self.get_domain(self._url)
                item['host'] = host
        except:
            item['identifier'] = self.get_domain(self._url)
            item['host'] = host
        return item


class SuNingExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'shop.suning.com' or host == 'shop.m.suning.com':
                if host == 'shop.m.suning.com':
                    crawlUrl = self._url.split('.html')[0].replace('shop.m.suning.com',
                                                                   'shop.suning.com') + '/index.html'
                    html = self.download(crawlUrl)
                detail_url = ''
                urls = self.findElements(html, '//area/@href')
                for url in urls:
                    if url.count('product.suning.com/'):
                        if not url.startswith('http'):
                            url = 'https:' + url
                        detail_url = url
                        break
                text = self.download(detail_url)
                self._brand = re.findall('"brandName":"(.*?)", "newResServer"', text, re.I)[0]
                self._shop = re.findall('"flagshipName":"(.*?)", "tuijianCatenIds"', text, re.I)[0]
                self._category = re.findall('"categoryName1":"(.*?)","category2"', text, re.I)[0]
                self._identifier = re.findall('shopContext : "(.*?)",', text, re.I)[0].replace('//', '')

            elif host == 'product.suning.com':
                self._brand = re.findall('"brandName":"(.*?)",', html, re.I)[0]
                shops = re.findall('"flagshipName":"(.*?)",', html, re.I)
                if not shops:
                    pass
                else:
                    self._shop = shops[0]
                self._category = re.findall('"categoryName1":"(.*?)",', html, re.I)[0]
                hosts = re.findall('shopContext : "(.*?)",', html, re.I)
                if hosts:
                    self._identifier = hosts[0].replace('//', '')
                else:
                    self._identifier = re.findall('<a title="头图" href="(.*?)" target="_blank">', html, re.I)
                    if hosts:
                        self._identifier = hosts[0].replace('http://', '').replace('index.html', '')
                    else:
                        self._identifier = self.findElement(html, '//div[@class="fix-store-name"]/h3/a/@href')

            elif host == 'm.suning.com' and self._url.count('m.suning.com/product'):
                crawlUrl = self._url.replace('m.suning.com', 'product.suning.com').replace('/product/', '/')
                text = self.download(crawlUrl)
                self._brand = re.findall('"brandName":"(.*?)",', text, re.I)[0]
                shops = re.findall('"flagshipName":"(.*?)",', text, re.I)
                if not shops:
                    pass
                else:
                    self._shop = shops[0]
                self._category = re.findall('"categoryName1":"(.*?)",', text, re.I)[0]
                hosts = re.findall('shopContext : "(.*?)",', text, re.I)

                if hosts:
                    self._identifier = hosts[0].replace('//', '')
                else:
                    self._identifier = re.findall('<a title="头图" href="(.*?)" target="_blank">', text, re.I)
                    if hosts:
                        self._identifier = hosts[0].replace('http://', '').replace('index.html', '')
                    else:
                        self._identifier = self.findElement(text, '//div[@class="fix-store-name"]/h3/a/@href')

            if self._brand:
                if self._brand.count('('):
                    self._cname = self._brand.split('(')[0]
                    self._ename = self._brand.split('(')[1].replace(')', '')
                else:
                    if self.is_alphabet(self._brand.encode('unicode_escape').decode()):
                        self._ename = self._brand
                    else:
                        self._cname = self._brand

            if self._identifier:
                item['identifier'] = self._identifier
            else:
                item['identifier'] = self.get_domain(self._url)
            item['shop'] = self._shop
            item['brand'] = self._brand
            item['url'] = self._url
            item['cname'] = self._cname
            item['ename'] = self._ename
            item['host'] = host
        except:
            item['identifier'] = self.get_domain(self._url)
            item['host'] = host
        return item


class MiExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'app.mi.com':
                self._company = self.findElement(html, '//div[@class="intro-titles"]/p[1]/text()')
                self._brand = self.findElement(html, '//div[@class="intro-titles"]/h3/text()')
                self._category = self.findElement(html, '//p[@class="special-font action"]/text()')
                self._icon = self.findElement(html, '//img[@class="yellow-flower"]/@src')
                self._identifier = self.findElement(html, '//li[@class="special-li"][1]/text()')
                if self._icon:
                    self._iconmd5 = self.data_md5(self._icon.encode('utf-8'))
                    self.download_pic(self._icon, self._iconmd5)
            if self._identifier:
                item['company'] = self._company
                item['category'] = self._category
                item['brand'] = self._brand
                item['identifier'] = self._identifier
                item['host'] = host
                item['url'] = self._url
                item['icon'] = self._icon
                item['iconmd5'] = self._iconmd5
        except:
            item['identifier'] = self.get_domain(self._url)
            item['host'] = host
        return item


class AppleExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            self._brand = self.findElement(html,
                                           '//h1[@class="product-header__title app-header__title"]/text()').replace(
                '\r', '').replace('\n', '').replace(' ', '')
            self._category = self.findElement(html,
                                              '//dd[@class="information-list__item__definition l-column medium-9 large-6"]/a/text()')
            self._company = self.findElement(html,
                                             '//h2[@class="product-header__identity app-header__identity"]/a/text()')
            icons = self.findElement(html, '//source[@class="we-artwork__source"][1]/@srcset')
            if icons:
                self._icon = icons.split(' 1x,')[0]
                self._iconmd5 = self.data_md5(self._icon.encode('utf-8'))
                self.download_pic(self._icon, self._iconmd5)
            self._identifier = 'apps.apple.com/cn/app/id' + self._url.split('?')[0].split('id')[1]
            item['company'] = self._company
            item['category'] = self._category
            item['brand'] = self._brand
            item['host'] = host
            item['url'] = self._url
            item['icon'] = self._icon
            item['iconmd5'] = self._iconmd5
            item['identifier'] = self._identifier.replace('http://', '').replace('https://', '')
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class JDExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        crawlUrl = ''
        item = self.items()
        try:
            if host == 'item.jd.com' or host == 'item.jd.hk':
                pass
            elif self._url.count('m.jd.com/product'):
                crawlUrl = self._url.replace('m.jd.com/product', 'item.jd.com')
                html = self.download(crawlUrl)
            elif host == 'mall.jd.com':
                links = re.findall('"linkInfo":(.*?),"target"', html, re.I)
                for link in links:
                    if link.count('link') and link.count('item.jd.com'):
                        crawlUrl = 'https:' + json.loads(link)['link']
                        break
                if not crawlUrl:
                    id = re.findall('(.*?)item.jd.com/(.*?).html', html, re.I)[0][1]
                    if id:
                        crawlUrl = 'https://item.jd.com/{}.html'.format(id)
                html = self.download(crawlUrl)
            else:
                links = re.findall('"linkInfo":(.*?),"target"', html, re.I)
                for link in links:
                    if link.count('link') and link.count('item.jd.com'):
                        crawlUrl = 'https:' + json.loads(link)['link']
                        break
                html = self.download(crawlUrl)
            shop = self.findElements(html, '//div[@class="name"]/a/text()')
            if shop:
                self._shop = shop[0]
            else:
                shop = self.findElements(html, '//h3[@class="short-shopname"]/a/text()')
                if shop:
                    self._shop = shop[0]
            hosts = self.findElements(html, '//div[@class="name"]/a/@href')
            if hosts:
                self._identifier = hosts[0].replace('//', '').replace('.html', '').replace('https:', '')
            else:
                hosts = self.findElements(html, '//h3[@class="short-shopname"]/a/@href')
                if hosts:
                    self._identifier = hosts[0].replace('//', '').replace('.html', '').replace('https:', '')

            brands = self.findElements(html, '//ul[@class="p-parameter-list"]/li/a/text()')
            if brands:
                self._brand = brands[0]
            else:
                brands = self.findElements(html, '//ul[@class="parameter2"]/li/a/text()')
                if brands:
                    self._brand = brands[0]

            category = self.findElements(html, '//div[@class="item first"]/a/text()')
            if category:
                self._category = category[0]
            if self._brand:
                if self._brand.count('（'):
                    self._cname = self._brand.split('（')[0]
                    self._ename = self._brand.split('（')[1].replace('）', '')
                else:
                    if self.is_alphabet(self._brand.encode('unicode_escape').decode()):
                        self._ename = self._brand
                    else:
                        self._cname = self._brand
            if self._identifier:
                item['identifier'] = self._identifier
                item['host'] = self._identifier
            else:
                item['identifier'] = host
                item['host'] = host
            item['shop'] = self._shop
            item['brand'] = self._brand
            item['category'] = self._category
            item['url'] = self._url
            item['cname'] = self._cname
            item['identifier'] = self._identifier
            item['ename'] = self._ename
            item['company'] = self._shop
            item['developer'] = self._shop
        except:
            item['identifier'] = self.get_domain(self._url)
            item['host'] = host
        return item


class MyAppExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            # self._company = self.findElement(html, '//div[@class="det-othinfo-data"][2]/text()')
            self._icon = self.findElement(html, '//div[@class="det-ins-btn-box"]/a/@appicon')
            self._brand = self.findElement(html, '//div[@class="det-name-int"]/text()')
            self._category = self.findElement(html, '//div[@class="det-type-box"]/a/text()')
            self._iconmd5 = self.data_md5(self._icon.encode('utf-8'))
            self.download_pic(self._icon, self._iconmd5)
            self._identifier = self._url.split('?')[1].replace('apkName=', '')
            item['company'] = self._company
            item['category'] = self._category
            item['brand'] = self._brand
            item['host'] = host
            item['url'] = self._url
            item['icon'] = self._icon
            item['iconmd5'] = self._iconmd5
            item['identifier'] = self._identifier
        except:
            item['identifier'] = self.get_domain(self._url)
            item['host'] = host
        return item


class YHDExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'item.yhd.com':
                pass
            elif host == 'mall.yhd.com':
                info_urls = self.findElements(html, '//a/@href')
                for i_url in info_urls:
                    if i_url.count('item.yhd.com'):
                        self._url = 'https:' + i_url
                        break
                html = self.download(self._url)
            brand = re.findall('title="品牌：(.*?)">品牌：', html, re.I)
            if brand:
                self._brand = brand[0]
            category = self.findElements(html, '//div[@class="crumb clearfix"]/a[1]/em/text()')
            if category:
                self._category = category[0]
            id = self._url.split('.html')[0].replace('http://item.yhd.com/', '').replace('https://item.yhd.com/', '')
            shop_url = 'http://c0.3.cn/stock?extraParam=%7B%22originid%22:%221%22%7D&ch=9&callback=jQuery111309148088241674284_1548748930203&skuId={}&area=2_2817_51973_0&cat=9987%2C653%2C655&buyNum=1&venderId=1000004259&fqsp=0&coord=&_=1548748930204'.format(
                id)
            text = requests.get(shop_url).text
            jsoninfo = json.loads(text.replace('jQuery111309148088241674284_1548748930203(', '').replace('})', '}'))
            self._shop = jsoninfo['stock']['self_D']['vender']
            identifier = re.findall("venderId: '(.*?)',", html, re.I)
            if identifier:
                self._identifier = 'mall.yhd.com/index-' + identifier[0]
            else:
                self._identifier = host
            if self._brand:
                if self._brand.count('（'):
                    self._cname = self._brand.split('（')[0]
                    self._ename = self._brand.split('（')[1].replace('）', '')
                else:
                    if self.is_alphabet(self._brand.encode('unicode_escape').decode()):
                        self._ename = self._brand
                    else:
                        self._cname = self._brand
            item['shop'] = self._shop
            item['brand'] = self._brand
            item['category'] = self._category
            item['url'] = self._url
            item['cname'] = self._cname
            item['identifier'] = self._identifier
            item['ename'] = self._ename
        except:
            item['identifier'] = self.get_domain(self._url)
            item['host'] = host
        return item


class ZhiHuExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'promotion.zhihu.com':
                self._brand = self.findElement(html, '//span[@class="PostIndex-authorName"]/text()')
                self._icon = self.findElement(html,
                                              '//img[@class="Avatar-madara PostIndex-authorAvatar Avatar--xs"]/@srcset')
            elif host == 'zhuanlan.zhihu.com':
                self._brand = re.findall('"name":"(.*?)","headline"', html, re.I)[0]
                self._icon = re.findall('"avatarUrl":"(.*?)","isFollowing', html, re.I)[0]
            self._icon = re.sub('\u002F', '/', self._icon)
            self._iconmd5 = self.data_md5(self._icon.encode('utf-8'))
            self.download_pic(self._icon, self._iconmd5)
            item['brand'] = self._brand
            item['host'] = host
            item['url'] = self._url
            item['icon'] = self._icon
            item['iconmd5'] = self._iconmd5
            item['identifier'] = self._identifier
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class BaiDuExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'm.baidu.com' or self._url.count('ada.baidu.com/ecom?cp'):
                redirect_url = re.findall("link href='(.*?)' rel='dns-prefetch'", html, re.I)[0]
                r = requests.get(redirect_url)
                content = str(r.content, encoding='utf-8')
                self._brand = self.findElement(content, '//title/text()')
            elif host == 'appin.baidu.com':
                self._brand = self.findElement(html, '//div[@class="title"]/text()')
                self._icon = \
                    re.findall('<div class="app-image" style="background-image: url((.*?))"></div>', html, re.I)[0][
                        0].replace('(', '').replace(')', '')
                self._iconmd5 = self.data_md5(self._icon.encode('utf-8'))
                self.download_pic(self._icon, self._iconmd5)
                self._category = self.findElement(html, '//div[@class="desc"]/text()').replace('\n', '').replace(' ',
                                                                                                                 '')
            elif self._url.count('baidu.com/site'):
                redirect_url = self.findElement(html, '//div[@class="y-wrap"]/iframe/@src')
                r = requests.get(redirect_url)
                content = str(r.content, encoding='utf-8')
                self._brand = self.findElement(content, '//p[@class="shop-header-text-p"]/text()')
                if not self._brand:
                    self._brand = self.findElement(content, '//title/text()')
            item['brand'] = self._brand
            item['iconmd5'] = self._iconmd5
            item['category'] = self._category
            item['identifier'] = self._url.split('&')[0].replace('https://', '')
            item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class SouGouExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'wap.sogou.com':
                label = self.findElement(html, '//div[@class="box-translation"]')
                datas = str(etree.tostring(label, encoding="utf-8", method="xml"), encoding='utf-8')
                if datas.count('<strong>'):
                    data = re.findall('<div class="citeurl"><strong>(.*?)</strong>(.*?)</div>', datas, re.I)
                    self._brand = data[0][0] + data[0][1]
                else:
                    data = re.findall('<div class="citeurl">(.*?)</div>', datas, re.I)
                    self._brand = data[0]
                item['brand'] = self._brand
                item['identifier'] = self._url.split('&')[0].replace('https://', '')
                item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class QQExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):

        item = self.items()
        try:
            newAppData = re.findall('var newAppData = viewerUtils.replaceApkUrl\(mediaName, (.*?)\);', html, re.I)
            if newAppData:
                newAppData = json.loads(newAppData[0])
                self._brand = newAppData["name"]
                self._icon = newAppData["logoUrl"]
                self._company = newAppData["authorName"]
                self._identifier = newAppData["packageName"]
                self._iconmd5 = self.data_md5(self._icon.encode('utf-8'))
            elif re.findall('"appId":"(.*?)', html, re.I):
                appId = re.findall('"appId":"(.*?)"', html, re.I)[0]
                url = "https://amp-api.apps.apple.com/v1/catalog/CN/apps/{0}?platform=web&additionalPlatforms=appletv%2Cipad%2Ciphone%2Cmac&extend=description%2CdeveloperInfo%2CeditorialVideo%2CfileSizeByDevice%2CmessagesScreenshots%2CprivacyPolicyUrl%2CprivacyPolicyText%2CpromotionalText%2CscreenshotsByType%2CsupportURLForLanguage%2CversionHistory%2CvideoPreviewsByType%2CwebsiteUrl&include=genres%2Cdeveloper%2Creviews%2Cmerchandised-in-apps%2Ccustomers-also-bought-apps%2Cdeveloper-other-apps%2Capp-bundles%2Ctop-in-apps&l=zh-cn".format(
                    appId)
                self._identifier = re.findall('"packageName":"(.*?)"', html, re.I)[0]
                self._brand = re.findall('"packageName":"(.*?)"', html, re.I)[0]
                self._icon = re.findall('"logoUrl":"(.*?)"', html, re.I)[0]
                self._iconmd5 = self.data_md5(self._icon.encode('utf-8'))
                resp = requests.get(url, headers={
                    "Authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNSRjVITkJHUFEifQ.eyJpc3MiOiI4Q1UyN"})
                appInfo = json.loads(resp.text)['data'][0]
                self._company = appInfo['relationships']['developer']['data'][0]['attributes']['name']
                self._category = appInfo['attributes']['genreDisplayName']
            elif "dstlink" in html:
                appInfo = json.loads(html)
                packageName = self.get_url_parameter(appInfo['data']['dstlink']["url"])["fsname"].split("_")[0]
                url = "https://android.myapp.com/myapp/detail.htm?apkName=" + packageName
                resp = requests.get(url)
                soup = BeautifulSoup(resp.text, 'lxml')
                tits = soup.find_all("div", class_="det-othinfo-tit")
                self._company = [tit.find_next_sibling().text for tit in tits if tit.text.count("开发商") > 0][0]
                self._brand = soup.select_one("a.det-ins-btn")["appname"]
                self._category = soup.select_one("a.det-type-link").text
                self._icon = soup.select_one("div.det-icon img")['src']
            # elif host == 'sdk.e.qq.com':
            #     self._brand = re.findall('<h3 class="name">(.*?)</h3>', html, re.I)[0]
            #     self._icon = re.findall('<img class="logo" src="(.*?)" width', html, re.I)[0]
            #     self._iconmd5 = self.data_md5(self._icon.encode('utf-8'))
            #     self.download_pic(self._icon, self._iconmd5)
            #     self._identifier = self._url.split('&')[0].replace('https://', '')
            else:
                item['identifier'] = host
                item['host'] = host

            item['brand'] = self._brand
            item['icon'] = self._icon
            item['iconmd5'] = self._iconmd5
            item['identifier'] = self._identifier
            item['host'] = host
            item["company"] = self._company
            item['developer'] = self._company
            item['category'] = self._category
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class TouTiaoExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if self._url.count('toutiao.com/item'):
                self._brand = re.findall("title: '(.*?)',", html, re.I)[0]
                self._identifier = self._url.replace('https://www.', '').replace('https://', '')
            item['brand'] = self._brand
            item['identifier'] = self._identifier
            item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class FlZhanExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'flzhan.cn':
                redirect_url = self.findElement(html, '//a[@class="data-report"]/@href')
                res = get_tld(redirect_url, as_object=True)
                domain = res.fld
                redirect_url = 'http://www.' + domain
                r = requests.get(redirect_url)
                content = str(r.content, encoding='utf-8')
                self._brand = self.findElement(content, '//title/text()')
                self._identifier = self._url.split('&')[0].replace('https://', '').replace('http://', '')
            item['brand'] = self._brand
            item['host'] = host
            item['identifier'] = self._identifier
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class WeiBoExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = item = self.items()
        try:
            if host == 'apps.weibo.com':
                pass
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class FYEDSExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            self._company = re.findall('此页面商品或服务由(.*?)提供', str(html), re.I)[0]
            self._identifier = urlparse(self._url).hostname
            item['brand'] = self._brand
            item['shop'] = self._shop
            item['cname'] = self._company
            item['company'] = self._company
            item["developer"] = self._company
            item['identifier'] = self._identifier
            item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class JinRiTeMaiExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'haohuo.jinritemai.com':
                query_info = self.get_url_parameter(self._url)
                id = query_info["id"]
                redirect_url = 'https://ec.snssdk.com/product/lubanajaxstaticitem?id={0}&token=a9c852a1f41d10b2e51ffd7aa65aed8a&scope_type=5&b_type_new=0'.format(
                    id)
                res = requests.get(redirect_url)
                ad_info = json.loads(res.text)
                self._shop = ad_info["data"]["shop_name"]
                self._company = ad_info["data"]["company_name"]
                self._identifier = ad_info["data"]["shop_id"] + ".jinritemai.com"
            elif host == "clue.jinritemai.com":
                ad_id = self.get_url_parameter(self._url)["ad_id"]
                url = self._url.split("?")[0] + "?tag=pc_iframe&ad_id=" + str(ad_id)
                resp = requests.get(url)
                shopinfo = re.findall('JSON.parse\(\"(.*?)\"\)', resp.text, re.I)[0].replace("\\\"", "\"")
                shopInfo = json.loads(shopinfo)["meta"]["customization"]["shopInfo"]
                self._company = shopInfo["name"]
                self._identifier = self.get_url_parameter(shopInfo["url"])["shopId"] + ".jinritemai.com"
            else:
                pass
                # soup = BeautifulSoup(html, "lxml")
                # self._developer = soup.select_one('div.xj-text div.xj-basic-text')['data-value']
            item['brand'] = self._brand
            item['shop'] = self._shop
            item['cname'] = self._company
            item['company'] = self._company
            item["developer"] = self._company
            item['identifier'] = self._identifier
            item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class BliBliExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            item["developer"] = self._developer
            item["category"] = self._category
            if host == 'cm.bilibili.com':
                self._brand = re.findall('"props":{"title":"(.*?)","icon"', html, re.I)[0]
                self._identifier = self._url.split('?')[0].replace('https://', '').replace('http://', '')
            item['brand'] = self._brand
            item['identifier'] = self._identifier
            item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class AutohomeExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:

            if self._url.count('autohome.com.cn/drive') or self._url.count('autohome.com.cn/advice'):
                r = requests.get(self._url, allow_redirects=True)
                text = str(r.content, encoding='gbk')
                self._company = self.findElement(text, '//div[@class="athm-sub-nav__car__name"]/a/text()').split('-')[0]
                self._brand = self.findElement(text, '//div[@class="athm-sub-nav__car__name"]/a/text()')
                self._identifier = self._url.split('?')[0].replace('https://www.', '').replace('http://www.',
                                                                                               '').replace('.html', '')
            elif host == 'club.autohome.com.cn':
                r = requests.get(self._url, allow_redirects=True)
                text = str(r.content, encoding='gbk')
                self._brand = self.findElement(text, '//div[@class="brand-name"]/a/text()')
                self._identifier = self._url.replace('https://', '').replace('http://', '').replace('.html', '')

            elif host == 'car.autohome.com.cn':
                r = requests.get(self._url, allow_redirects=True)
                text = r.text
                self._company = self.findElement(text, '//div[@class="breadnav"]/a[3]/text()')
                self._brand = self.findElement(text, '//div[@class="breadnav"]/a[4]/text()')
                self._identifier = self._url.replace('https://', '').replace('http://', '').replace('.html', '')
            elif host == 'v.autohome.com.cn':
                r = requests.get(self._url, allow_redirects=True)
                text = r.text
                self._brand = self.findElement(text, '//li[@class="activate"]/a/text()')
                self._identifier = self._url.replace('https://', '').replace('http://', '').replace('.html', '')
            item['company'] = self._company
            item['brand'] = self._brand
            item['identifier'] = self._identifier
            item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class JiaExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'm.jia.com':
                self._company = self.findElement(html, '//p[@class="cr_sm_sec"]/text()')
                self._brand = self.findElement(html, '//p[@class="cr_sm"]/text()').replace('copyright © 2005-2018',
                                                                                           '').replace('Jia.com版权所有',
                                                                                                       '')
                self._identifier = self._url.split('?')[0].replace('https://', '').replace('http://',
                                                                                           '').replace('.html', '')
            item['company'] = self._company
            item['brand'] = self._brand
            item['identifier'] = self._identifier
            item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class TongChengExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if self._url.count('ershouche'):
                if host == 'm.58.com':
                    redirect_url = self.findElement(html, '//a[@tongji_tag="esc_m_model_other"]/@href')
                    r = requests.get(redirect_url, allow_redirects=True)
                    text = r.text
                    self._brand = re.findall('"name":"(.*?)","listname"', text, re.I)[3]
                else:
                    redirect_url = self.findElement(html, '//p[@class="tuijian_tishi"]/a[1]/@href')
                    r = requests.get(redirect_url, allow_redirects=True)
                    text = str(r.content, encoding='utf-8')
                    self._brand = re.findall('var selectBrandtextTKBf = "(.*?)";', text, re.I)[0]
            elif self._url.count('xcarlist'):
                self._brand = re.findall('"name":"(.*?)","listname"', html, re.I)[3]
            elif self._url.count('luna.58.com/list'):
                self._company = re.findall('"company":"(.*?)","credit"', html, re.I)[0]

            self._identifier = self._url.split('?')[0].replace('https://', '').replace('http://',
                                                                                       '').replace('.shtml', '')
            item['brand'] = self._brand
            item['company'] = self._company
            item['identifier'] = self._identifier
            item['host'] = host
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class SoHuExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if self._url.count('sohu.com/') and self._url.count('img'):
                self._brand = self._url.replace('http://', '').split('/')[1]
                self._identifier = self._url.replace('http://', '').replace('index.html', '')
            elif self._url.count('auto.sohu.com/'):
                if html.count('"brandName"'):
                    self._brand = re.findall('"brandName":"(.*?)","subbrand"', html, re.I)[0]
                    self._identifier = self._url.replace('http://', '').replace('index.shtml', '')
                elif html.count('class="tit"'):
                    self._brand = self.findElement(html, '//div[@class="tit"]/a/span/text()')
                    self._identifier = self._url.split('?')[0].replace('http://', '')
            item['brand'] = self._brand
            item['host'] = host
            item['identifier'] = self._identifier
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class SinaCnExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'auto.sina.cn':
                r = requests.get(self._url, allow_redirects=True)
                text = str(r.content, encoding='utf-8')
                self._brand = self.findElement(text, '//div[@class="title"]/text()')
                self._identifier = self._url.replace('http://', '').replace('index.html', '')

            item['brand'] = self._brand
            item['host'] = host
            item['identifier'] = self._identifier
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class SinaComCnExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'auto.sina.com.cn':
                self._company = self.findElement(html, '//a[@class="fL logo"]/img/@alt')
                self._brand = self.findElement(html, '//span[@class="fL name"]/a/text()')

            elif host == 'tech.sina.com.cn':
                self._brand = self.findElement(html, '//meta[@name="tags"]/@content')
                if self._brand.count(','):
                    self._brand = self._brand.split(',')[0]

            self._identifier = self._url.replace('http://', '').replace('.shtml', '')
            item['company'] = self._company
            item['brand'] = self._brand
            item['host'] = host
            item['identifier'] = self._identifier
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class WangYiExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 's.auto.163.com' or host == 'go.163.com':
                url = self._url.split('?')[0]
                if url.count('_') >= 2:
                    self._ename = re.findall('/(.*?)_(.*?)_(.*?)/', url, re.I)[0][1]
                else:
                    self._ename = re.findall('/(.*?)_(.*?)/', url, re.I)[0][1]
            self._identifier = self._url.split('?')[0].replace('http://', '').replace('index.html', '')
            item['ename'] = self._ename
            item['brand'] = self._brand
            item['host'] = host
            item['identifier'] = self._identifier
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class IFengExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'auto.ifeng.com':
                if html.count('class="vdo"'):
                    self._brand = self.findElement(html, '//div[@class="vdo"]/p/text()')
                else:
                    self._brand = self.findElement(html, '//div[@id="serialInfo"]/h2/a[1]/text()')
            elif self._url.count('ifeng.com/auto'):
                self._brand = self.findElement(html, '//div[@class="logo ov pa"]/a[1]/@title').replace('官网', '')
            self._identifier = self._url.split('?')[0].replace('http://', '').replace('.shtml', '')
            item['ename'] = self._ename
            item['brand'] = self._brand
            item['host'] = host
            item['identifier'] = self._identifier
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class LianWangTechExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        try:
            if host == 'c1wx.lianwangtech.com':
                if html.count('id="appname"'):
                    self._brand = self.findElement(html, '//div[@id="appname"]/text()')
                    self._company = self.findElement(html, '//section[@class="dev-card"]/p/span/text()')
                elif html.count('class="product-attr-item"'):
                    self._brand = self.findElement(html, '//tr[@class="product-attr-item"][1]/td[2]/text()')
                    self._shop = self.findElement(html, '//input[@id="J-wxs-brandname"]/@value')
            self._identifier = host + '/' + self._brand
            item['company'] = self._company
            item['brand'] = self._brand
            item['shop'] = self._shop
            item['host'] = host
            item['identifier'] = self._identifier
        except:
            item['identifier'] = host
            item['host'] = host
        return item


class OtherExtractor(WebsiteExtractor):
    def __init__(self, url, html):
        WebsiteExtractor.__init__(self, url, html)

    def parse(self, host, html):
        item = self.items()
        item['kd'] = None
        item['description'] = None
        item['title'] = None
        item['content'] = None
        item['encoding'] = None
        item['identifier'] = self.get_domain(self._url)
        item['host'] = host
        return item
