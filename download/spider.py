# -*- encoding: utf-8 -*-
import requests
from tld import get_tld
import re
from config.config import Config


class Spider(object):
    def __init__(self):
        self.config = Config()

    def get_charset(self, response=None):
        try:
            if not response:
                encoding = "utf-8"
            else:
                header = response.headers
                contentType = header['Content-Type']
                if contentType:
                    if "charset=utf-8" in contentType.lower():
                        encoding = "utf-8"
                    elif "charset=gbk" in contentType.lower():
                        encoding = "gbk"
                    else:
                        enc = re.findall('charset=(.*?)$', contentType, re.I)
                        encoding = enc[0] if enc else ""
                    if not encoding:
                        charset = re.findall('charset="(.*?)"', response.text, re.I)
                        encoding = charset[0] if charset else "utf-8"
                    else:
                        encoding = encoding
                else:
                    charset = re.findall('charset=(.*?)"', response.text, re.I)
                    encoding = charset[0] if charset else "utf-8"
            encoding = encoding if encoding else "utf-8"
        except Exception as e:
            encoding = 'utf-8'
        return encoding

    def get_domain(self, url=None, domain=None):
        flag = False
        if not [i for i in ['.apk', '.mp4', '.flv', '.swf', '.pnf', '.jpeg', '.jpg'] if url.count(i) != 0]:
            if domain in ['tmall.com', 'jd.com', 'suning.com', 'yhd.com', 'apple.com', 'myapp.com', 'mi.com',
                          'jinritemai.com', "fyeds0.com", "fyeds1.com", "fyeds2.com", "fyeds3.com", "fyeds4.com",
                          "fyeds5.com", "fyeds6.com", "fyeds7.com", "fyeds8.com", "fyeds9.com", "qq.com"]:
                flag = True
        return flag

    def fetch(self, url, retries=2):
        try:
            domain = get_tld(url, as_object=True).fld
            if self.get_domain(url=url, domain=domain):
                headers = {'user-agent': self.config.getUA()}
                if domain == "jd.com":
                    headers['cookie'] = "pinId=Nr0M8RGDKbA; pin=adbugjd"
                response = requests.get(url, headers={'user-agent': self.config.getUA()}, timeout=2)
                enc = self.get_charset(response=response)
                content = str(response.content, encoding=enc)
                return content
        except:
            if retries > 0:
                return self.fetch(url, retries - 1)
            return
