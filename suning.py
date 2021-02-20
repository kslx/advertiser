import hashlib
from urllib.parse import urlparse
import pymysql
from tld import get_tld
from advertiserExtractor.download.spider import Spider
from advertiserExtractor.extractor.parser import Parser
s = Spider()

def get_adbranddetail_data():
    data = None
    try:
        client = pymysql.connect(host='rm-bp1c5x1rhig246p88o.mysql.rds.aliyuncs.com', user='adbug',
                                 passwd='2YeoyszrQoUhzubO', db='adbugnew', port=3306)
        cursor = client.cursor()
        cursor.execute(
            "SELECT id, brand ,cname,ename,icon,identifier,host ,url  from ad_brand_detail WHERE brand is NOT NULL")
        data = cursor.fetchall()
    except Exception as e:
        pass
    return data

def get_adbrand_id(id):
    data = None
    try:
        client = pymysql.connect(host='rm-bp1c5x1rhig246p88o.mysql.rds.aliyuncs.com', user='adbug',
                                 passwd='2YeoyszrQoUhzubO', db='adbugnew', port=3306)
        cursor = client.cursor()
        cursor.execute("SELECT advertiserid  from ad_brand WHERE detailid=%s" % (id))
        data = cursor.fetchall()
    except Exception as e:
        pass
    return data

def get_domains_data(identifier):
    data = None
    try:
        client = pymysql.connect(host='rm-bp1c5x1rhig246p88o.mysql.rds.aliyuncs.com', user='adbug',
                                 passwd='2YeoyszrQoUhzubO', db='adbugnew', port=3306)
        cursor = client.cursor()
        cursor.execute("select  id,cname ,ename from domains  where host= '%s'" % (identifier))
        data = cursor.fetchall()[0]
    except Exception as e:
        pass
    return data

def insert_addatadomains_id(addataid, domainsid):
    try:
        client = pymysql.connect(host='rm-bp1c5x1rhig246p88o.mysql.rds.aliyuncs.com', user='adbug',
                                 passwd='2YeoyszrQoUhzubO', db='adbugnew', port=3306)
        sql = 'insert into addata_domain(addata_id,domain_id) values(%s,%s)'
        cursor = client.cursor()
        cursor.execute(sql, (addataid, domainsid))
        client.commit()
        cursor.close()
        client.close()
    except Exception as e:
        cursor.close()
        client.close()

def data_md5(data):
    m2 = hashlib.md5()
    m2.update(data.encode(encoding='UTF-8'))
    return m2.hexdigest()

def update_domains_brand(item,identifier):
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
                sql = "update domains SET  cname='%s',ename='%s' WHERE identifier ='%s'"%(brand,ename,identifier)
                cursor = client.cursor()
                cursor.execute(sql)
                client.commit()
                cursor.close()
                client.close()
        except Exception as e:
            cursor.close()
            client.close()

def insert_domains_data(host, cname, ename, logo, have_logo, hostmd5):
    try:
        client = pymysql.connect(host='rm-bp1c5x1rhig246p88o.mysql.rds.aliyuncs.com', user='adbug',
                                 passwd='2YeoyszrQoUhzubO', db='adbugnew', port=3306)
        sql = 'insert into domains(host,cname,ename,isbrand,role,logo,have_logo,ispublisher,publisher_ads,tracker_ads,' \
              'publisher_subjects,tracker_subjects,brand_publishers,tracker_publishers,publisher_advertiser,tracker_advertiser,publisher_trackers,md5)' \
              ' values(%s,%s,%s,1,2,%s,%s,0,0,0,0,0,0,0,0,0,0,%s)'
        cursor = client.cursor()
        cursor.execute(sql, (host, cname, ename, logo, have_logo, hostmd5))
        client.commit()
        cursor.close()
        client.close()
    except Exception as e:
        print(e)
        cursor.close()
        client.close()

def get_domain(url):
    domain = None
    try:
        res = get_tld(url, as_object=True)
        domain = res.fld
    except Exception as e:
        pass
    return domain


"""
def run():
    try:
        datas = get_adbranddetail_data()
        for data in datas:
            detail_id = data[0]
            ids = get_adbrand_id(detail_id)
            brand = data[1]
            cname = data[2]
            ename = data[3]
            icon = data[4]
            if icon is not None:
                have_logo = 1
            iden = data[5]
            host = data[6]
            url = data[7]
            identifier = None
            domain = get_domain(url)
            if domain:
                if iden:
                    if host.count('tmall.com') or host.count('jd.com') or host.count('yhd.com') or host.count(
                            'mi.com') or host.count('suningt.com') or host.count('apple.com') or host.count(
                        'myapp.com') or host.count(
                        'zhihu.com'):
                        if brand is not None or cname is not None:
                            if iden.count('apkName'):
                                identifier = iden.replace('apkName=', '')
                            elif iden.count('mi.com'):
                                labels = iden.split('id=')
                                if labels:
                                    identifier = labels[1]
                            else:
                                identifier = iden
                            domains_id = get_domains_id(identifier)
                            if domains_id:
                                for addata_id in ids:
                                    insert_addatadomains_id(addata_id[0], domains_id)
                            else:
                                if cname is not None:
                                    if identifier:
                                        insert_domains_data(identifier, cname, ename, icon, have_logo, data_md5(identifier))
                                else:
                                    if identifier:
                                        insert_domains_data(identifier, brand, ename, icon, have_logo, data_md5(identifier))

                                domains_id = get_domains_id(identifier)
                                if domains_id:
                                    for addata_id in ids:
                                        insert_addatadomains_id(addata_id[0], domains_id)

    except Exception as e:
        print(e)
"""
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

def run():
    try:
        with open('C:/Users/matthrew/Desktop/suning.txt',  encoding='utf-8') as f:

            for line in f:
                line = line.replace('\r', '').replace('\n', '')
                lineList = line.split('	')
                addata_id = lineList[0]
                print(addata_id)
                url = lineList[1]
                html = s.fetch(url)
                item = handle(url,html)
                print(item)
                if item:
                    cname = item['cname']
                    ename = item['ename']
                    brand = item['brand']
                    shop = item['shop']
                    identifier = item['identifier']
                    icon = item['icon']
                    have_logo = None
                    branddata = None
                    if item['cname'] :
                        branddata = item['cname']
                    elif item['shop']:
                        branddata = item['shop']
                    elif item['brand']:
                        branddata = item['brand']
                    if icon:
                        have_logo=1
                    if cname is not  None or brand is not None or shop is not None:
                        data = get_domains_data(identifier)
                        if data:
                            domains_id = data[0]
                            domains_cname = data[1]
                            domains_ename = data[2]
                            if  domains_cname is None or domains_ename is None:
                                update_domains_brand(item,identifier)
                            insert_addatadomains_id(addata_id,domains_id)
                        else:
                            insert_domains_data(identifier,branddata,ename,icon,have_logo,data_md5(identifier))
                            data = get_domains_data(identifier)
                            if data:
                                domains_id = data[0]
                                insert_addatadomains_id(addata_id,domains_id)
    except Exception as e:
            print(e)

run()


"""
用户 ID： epfuser200246
密码： 81e4eef697ba5dd296d84649aca3e897
链接： http://feeds.itunes.apple.com/feeds/
"""