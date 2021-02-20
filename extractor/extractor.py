# -*- coding: utf-8 -*-
import hashlib
from goose3 import Goose
from goose3.text import StopWordsChinese
import requests

from lxml.etree import HTML
from advertiserExtractor_time_new.download.spider import Spider


class Extractor(object):
    def __init__(self, url, html):
        self.html = html

    @staticmethod
    def create(url, html):
        return GooseExtractor(url, html)


class GooseExtractor(Extractor):
    def __init__(self, url, html):
        Extractor.__init__(self, url, html)
        self._kd = ''
        self._description = ''
        self._title = ''
        self._content = ''
        self._encoding = ''
        self._url = url
        parser = self.gooseParse()
        if parser:
            self._kd = parser.meta_keywords
            self._description = parser.meta_description
            self._title = parser.title
            self._content = parser.cleaned_text
            self._encoding = parser.meta_encoding
        self.spider = Spider()

    def kd(self):
        return self._kd

    def description(self):
        return self._description

    def title(self):
        return self._title

    def content(self):
        return self._content

    def encoding(self):
        return self._encoding

    def url(self):
        return self._url

    def treeElement(self, text=None):
        return HTML(text)

    def get_element(self, xpath):
        return self.treeElement(self.html).xpath(xpath)[0]

    def get_elements(self, xpath):
        return self.treeElement(self.html).xpath(xpath)

    def findElement(self, text, xpath):
        element = HTML(text).xpath(xpath)
        return element[0] if element else ""

    def findElements(self, text, xpath):
        elements = HTML(text).tree.xpath(xpath)
        return elements if elements else ""

    def gooseParse(self):
        if self.html:
            try:
                g = Goose({'stopwords_class': StopWordsChinese})
                return g.extract(raw_html=self.html)
            except:
                return

    def download(self, url):
        return self.spider.fetch(url)

    def download_pic(self, url, filename, retries=3):
        try:
            r = requests.get(url, stream=True, verify=False)
            with open('./icon/{}.png'.format(filename), 'wb') as f:
                for chunk in r.iter_content(chunk_size=32):
                    f.write(chunk)
        except:
            if retries > 0:
                return self.download_pic(url, filename, retries - 1)

    def data_md5(self, data):
        m2 = hashlib.md5()
        m2.update(data)
        return m2.hexdigest()

    def is_alphabet(self, uchar):
        if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
            return True
        else:
            return False
