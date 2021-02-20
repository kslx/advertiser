from urllib.parse import urlparse
import chardet
import re
import requests

# from advertiserExtractor.db.mysql import Mysql
# from advertiserExtractor.download.spider import Spider
# from advertiserExtractor.extractor.parser import Parser

# def writeFile(filename, data):
#     f = open(filename, 'a',encoding='utf-8')
#     # data = json.dumps(data, ensure_ascii=False)
#     f.write(data)
#     f.write('\n')
#     f.close()
#
# def handle(url, html):
#     parser = urlparse(url)
#     hostname = parser.hostname
#     extractor = Parser.create(url, html)
#     item = extractor.parse(hostname, html)
#     return item


#
#
# s = Spider()
# url='http://hqyj.tmall.com/shop/view_shop.htm?mytmenu=mdianpu&utkn=g,xpr4p7wrzs7n7v5i2ovll2q1425437528664&user_number_id=2209354205&scm=1028.1.2.20001&v=1&ali_trackid=17_0eb1b3f4e09b9cc00f9701fe85501313'
# # r = requests.get(url,allow_redirects=True)
# # print(r.headers)
# # print(r.status_code)
# # html = str(r.content, encoding='gbk')
# html= s.fetch(url)
# # print(html)
# # writeFile('C:/Users/matthrew/Desktop/html.txt',html)
# item = handle(url,html)
# print(item)
# # m = Mysql()


# '''
# datas = m.get_urls(60)
# for data in datas:
#     aid = data[0]
#     url = data[1]
#     advertiser = data[2]
#     html = s.fetch(url)
#     detail_item = handle(url, html)
#     # print(detail_item)
#     m.process(detail_item)
#     identifier = detail_item['identifier']
#     print(identifier)
#     if identifier:
#         id = m.get_id(identifier)
#         print(id)
#         m.insert({'advertiserid': aid, 'detailid': id, 'advertiser': advertiser})
# '''

# advertiser = 'baidu.com'
# aid='1111'
# url='http://cover.baidu.com/cover/page/shoubai/shoubaiVideo?sign=QShj8Nnr0M0=&plan_id=99801677&unit_id=3780164347&idea_id=112815775294&cm_id=628&user_id=25998656&search_id=05015567352325ec&place_id=%7B%7BPLACE_ID%7D'
# html = s.fetch(url)
# detail_item = handle(url, html)
# print(detail_item)
# m.process(detail_item)
# identifier = detail_item['identifier']
# print('identifier: %s'%(identifier))
# if identifier:
#     id = m.get_id(identifier)
#     print(id)
#     m.insert({'advertiserid': aid, 'detailid': id, 'advertiser': advertiser})

# shopid_item = {}
# shopid=detail_item['shopid']
# if shopid:
#         shopid_item['shopid'] = detail_item['shopid']
# else:
#         shopid_item['shopid'] = advertiser
#         detail_item['shopid'] = advertiser
# detail_item['advertiser'] = advertiser
# print(detail_item['shopid'])
# shopid_item['aid'] = aid
# shopid_item['advertiser'] = advertiser


# s = Spider()
# m = Mysql()
#
# datas = m.get_urls(0)
# print(datas)
# for data in datas:
#     aid = data[0]
#     url = data[1]
#     advertiser = data[2]
#     html = s.fetch(url)
#     print(html)
#     detail_item = handle(url, html)
#     m.process(detail_item)
#     identifier = detail_item['identifier']
#     if identifier:
#         id = m.get_id(identifier)
#         m.insert({'advertiserid': aid, 'detailid': id, 'advertiser': advertiser})

# ss = 'text/html;charset=GBK'
# print(ss.lower())
# # enc = re.compile('charset=(.*?)$').findall(ss)
# enc = re.findall('charset=(.*?)$', ss, re.I)
# print(enc)
# url = "https://www.runoob.com/regexp/regexp-syntax.html"
# response = requests.get(url)
# res = re.findall('charset=(.*?)"', response.text, re.I)[0]
# print(res)
userAgentList = [
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)",
    "Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
]
user_agent = [
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)",
    "Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
]
print(len(userAgentList))
for ua in user_agent:
    if ua not in userAgentList:
        userAgentList.append(ua)
print(len(userAgentList), userAgentList)
