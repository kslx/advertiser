import hashlib
from urllib.parse import urlparse
import pymysql
from tld import get_tld
from advertiserExtractor.download.spider import Spider
from advertiserExtractor.extractor.parser import Parser
s = Spider()

def update_domains_brand(item,id):
        try:
            ename = item['ename']
            brand = None
            if item['cname'] :
                brand = item['cname']
            elif item['shop']:
                brand = item['shop']
            elif item['brand']:
                brand = item['brand']
            if brand:
                client = pymysql.connect(host='rm-bp1c5x1rhig246p88o.mysql.rds.aliyuncs.com', user='adbug',
                                 passwd='2YeoyszrQoUhzubO', db='adbugnew', port=3306)
                sql = "update domains SET  cname='%s',ename='%s' WHERE id =%s"%(brand,ename,id)
                cursor = client.cursor()
                cursor.execute(sql)
                client.commit()
                cursor.close()
                client.close()
        except Exception as e:
            cursor.close()
            client.close()

def handle(url, html):
    item = None
    try:
        parser = urlparse(url)
        hostname = parser.hostname
        extractor = Parser.create(url, html)
        item = extractor.parse(hostname, html)
    except Exception as e:
        print(e)
    return item

# line='172734	jx.tmall.com'
# lineList=line.split('	')
# domain_id = lineList[0]
# print(domain_id)
# host = lineList[1]
# url = 'https://'+host
# print(url)
# html = s.fetch(url)
# item = handle(url,html)
# print(item)

def run():
    try:
        with open('C:/Users/matthrew/Desktop/tmall_domain.txt',  encoding='utf-8') as f:
            for line in f:
                line = line.replace('\r', '').replace('\n', '')
                lineList=line.split('	')
                domain_id = lineList[0]
                print(domain_id)
                host = lineList[1]
                url = 'https://'+host.replace('.m.','.')
                print(url)
                html = s.fetch(url)
                item = handle(url,html)
                if item:
                    cname = item['cname']
                    ename = item['ename']
                    brand = item['brand']
                    shop = item['shop']
                    if cname is not  None or brand is not None or shop is not None:
                         update_domains_brand(item,domain_id)
    except Exception as e:
            print(e)

run()