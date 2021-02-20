# -*- encoding: utf-8 -*-
import json
import pymysql
import queue
import requests
import time
import traceback
import urllib3
import sys
sys.path.append('../')
from advertiserExtractor_time_new.log.log import logger
from advertiserExtractor_time_new.config.config import Config
from advertiserExtractor_time_new.download.spider import Spider
from advertiserExtractor_time_new.extractor.parser import Parser
from tool_utils.db import MySQLData
from tool_utils.common_util import common_util

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from urllib.parse import urlparse, urlencode
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

comm = common_util()
mydb = MySQLData(keys="adbug1_test")


def handle(url, html):
    try:
        hostname = urlparse(url).hostname
        extractor = Parser.create(url, html)
        item = extractor.parse(hostname, html)
        return item
    except:
        print(traceback.format_exc())
        return


def get_domains_data(host=None):
    """通过host 查询 domains 表"""
    try:
        sql = "select id,cname,ename,developer from domains where host= '%s'" % host
        data = mydb.fetch_one(sql=sql, form="tuple")
        return data
    except:
        print(traceback.format_exc())
        return


def insert_domains_data(host=None, cname=None, ename=None, logo=None, have_logo=None, hostmd5=None, developer=None, category=None):
    """没有该 host 则插入该广告信息"""
    try:
        sql = 'insert into domains(host,cname,ename,isbrand,role,logo,have_logo,ispublisher,publisher_ads,tracker_ads,' \
              'publisher_subjects,tracker_subjects,brand_publishers,tracker_publishers,publisher_advertiser,tracker_advertiser,publisher_trackers,md5,developer,category)' \
              ' values(%s,%s,%s,1,2,%s,%s,0,0,0,0,0,0,0,0,0,0,%s,%s,%s)'
        mydb.execute(sql, param=(exist(host), exist(cname), exist(ename), exist(logo), have_logo, hostmd5, exist(developer), exist(category)))
    except:
        print(traceback.format_exc())
        return


def insert_addata_domain(addata_id=None, domains_id=None):
    try:
        sql = 'insert into addata_domain(addata_id,domain_id) values("%s","%s")' % (addata_id, domains_id)
        mydb.execute(sql=sql)
    except:
        sql = 'update addata_domain SET domain_id =%s where addata_id =%s' % (domains_id, addata_id)
        mydb.execute(sql=sql)


def insert_es_domains(addata_id=None, domains_id=None, developer=None):
    return
    try:
        es = Elasticsearch('http://es-cn-v0h1lr99d000aq8u0.public.elasticsearch.aliyuncs.com:9200/',
                           http_auth=('elastic', 'Password002'), timeout=1000)
        sql1 = 'select host,cname from domains where id = %s' % (str(domains_id))
        ad_info = mydb.fetch_one(sql=sql1, form="tuple")
        host = ad_info[0]
        cname = ad_info[1]
        advertiser_full = host + " " + cname if cname else host
        try:
            if not cname and not developer:
                return
            es.update(index='addata_v29', doc_type='addata_index', id=str(addata_id), body={
                'doc': {
                    'advertiser_id': domains_id,
                    'sub_domain': {
                        'sub_host': host,
                        'sub_cname': exist(cname),
                    },
                    'advertiser_na': host,
                    'domain_host': host,
                    'advertiser': host,
                    'domain': host,
                    'advertiser_name': host,
                    # 'tracker_name':host,
                    'advertiser_name_title': exist(cname),
                    'advertiser_full': advertiser_full,
                    # 'tracker_full':host+" "+cname,
                    'developer': exist(developer)
                }
            })
        except:
            print('error in update es')
        return (0)
    except:
        raise Exception('es错误')


def update_domains_brand(host=None, developer=None, cname=None, ename=None, category=None):
    try:
        if cname or developer:
            sql = "update domains SET cname='%s',ename='%s',developer='%s',category='%s' WHERE host='%s'" % (
                exist(cname), exist(ename), exist(developer), exist(category), exist(host))
            mydb.execute(sql=sql)
    except:
        print(traceback.format_exc())
        return


def get_urls(aid=None):
    try:
        sql = 'select id,target_url,advertiser from addata_2018 where id>{0} order by id ASC limit 200'.format(aid)
        data = mydb.fetch_all(sql=sql, form="tuple")
        return data
    except:
        print(traceback.format_exc())
        return


def start():
    with open('id.txt', 'r') as f:
        last_id = int(f.read())
    ids = [last_id]
    aid = ids.pop(0)
    datas = get_urls(aid)
    if len(datas) == 200:
        aid = datas[199][0]
        for data in datas:
            q.put(data)
    else:
        time.sleep(10 * 60)
    ids.append(aid)


def run():
    while True:
        try:
            if q.qsize() < 50:
                start()
            else:
                data = q.get()
                run_task(data)
                with open('id.txt', 'w') as f:
                    f.write(str(data[0]))
        except:
            print(traceback.format_exc())
            break


def log(aid=None):
    logger.info({'id': aid})


def get_developer_mi(package=None):
    """小米应用市场 根据包名获取 app 的开发商"""
    app_data = {}
    try:
        url = "https://app.market.xiaomi.com/apm/app/package/{0}?ad=1&connId=0f607264fc6318a92b9e13c65db7cd3c&co=CN&densityScaleFactor=2.75&deviceType=0&h5=1&imei=8c166c2f00dca085a18e0c37c3c8fb8d&la=zh&lo=CN&mac=0f607264fc6318a92b9e13c65db7cd3c&marketVersion=1914106&miuiBigVersionCode=5&miuiBigVersionName=V7-dev&model=MI%2BNOTE%2BLTE&os=6.3.24&pageConfigVersion=118&pageRef=market_default&pos=app0&positionType=-1&ref=featured&refPosition=0&refs=index-detail%252Fcom.ss.android.ugc.aweme&resolution=1080%2A1920&ro=unknown&sdk=23&webResVersion=0&signature=XTPP0Xe%252F2AoIh78LErUjURlmx2E%253D".format(package)
        response = requests.get(url)
        response.encoding = "utf-8"
        if response.status_code != 200:
            return app_data
        app_info = json.loads(response.text)
        if 'app' not in list(app_info.keys()) or "packageName" not in app_info['app']:
            return
        app_info = app_info['app']
        if app_info["packageName"] == package:
            app_data['advertiser'] = package
            app_data['cname'] = app_info["displayName"]
            app_data['developer'] = app_info["publisherName"]
            app_data['category'] = app_info["level1CategoryName"]
            return app_data
    except:
        print(traceback.format_exc())
        return {}


def get_developer_myapp(package=None):
    """小米应用市场 根据包名获取 app 的开发商"""
    app_data = {}
    try:
        url = "https://android.myapp.com/myapp/detail.htm?apkName={0}".format(package)
        response = requests.get(url)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, 'lxml')
        tits = soup.find_all("div", class_="det-othinfo-tit")
        if not tits:
            return app_data
        app_data['advertiser'] = package
        app_data['category'] = soup.select_one("a.det-type-link").text
        app_data['cname'] = soup.select_one("a.det-ins-btn")["appname"]
        app_data['developer'] = [tit.find_next_sibling().text for tit in tits if tit.text.count("开发商") > 0][0]
        return app_data
    except:
        print(traceback.format_exc())
        return {}


def exist(text=None):
    return text if text else ""


def run_task(data):
    addata_id = data[0]
    target_url = data[1]
    advertiser = data[2]
    print('id', addata_id)
    if target_url:
        headers = {'User-Agent': Config().getUA()}
        try:
            is_url_ok = 'text/html' in requests.get(url=target_url, headers=headers, timeout=10, verify=False).headers['Content-Type']
        except:
            is_url_ok = 0
        if is_url_ok != 0:
            # 判断 domains 表中 是否存在 该 host
            domain_data = get_domains_data(host=advertiser)
            if domain_data:
                domains_id = domain_data[0]
                domains_cname = domain_data[1]
                domains_ename = domain_data[2]
                domains_developer = domain_data[3]
                if domains_developer:
                    # insert_es_domains(addata_id=addata_id, domains_id=domain_data[0], developer=domain_data[3])
                    return
                # 以 addata_2018 的 advertiser 为包名获取开发商名称
                app_data = get_developer(package=advertiser)
                if app_data:
                    developer = app_data["developer"]
                    if developer:
                        category = app_data["category"]
                        update_domains_brand(host=advertiser, developer=developer, cname=domains_cname, ename=domains_ename, category=category)
                        # insert_es_domains(addata_id=addata_id, domains_id=domains_id, developer=developer)
                        return
            update_ad_info(target_url=target_url, addata_id=addata_id)


def get_developer(package=None):
    appInfoMi = get_developer_mi(package=package)
    appInfoMyApp = get_developer_myapp(package=package)
    return appInfoMi if appInfoMi else appInfoMyApp


def update_ad_info(target_url=None, addata_id=None):
    ad = get_ad_info(target_url=target_url)
    if not ad:
        return
    if ad["developer"]:
        developer = pymysql.escape_string(ad["developer"]) if ad["developer"] else ad["developer"]
        if ad['category']:
            category = ad['category']
        else:
            app_data = get_developer(package=ad["host"])
            category = app_data['category'] if app_data else ""
        update(addata_id=addata_id, ad=ad, developer=developer, category=category)
        return
    # 以 addata_2018 的 target_url 为基准 获取广告信息，
    app_data = get_developer(package=ad["host"])
    category = app_data["category"] if app_data else ""
    developer = app_data["developer"] if app_data else ""
    developer = pymysql.escape_string(developer) if developer else developer
    update(addata_id=addata_id, ad=ad, developer=developer, category=category)


def update(addata_id=None, ad=None, developer=None, category=None):
    domains_data = get_domains_data(host=ad["host"])
    if not domains_data:
        update_info(developer=developer, host=ad["host"], ad=ad, addata_id=addata_id, category=category)
        return
    # 更新 domains 表的依据：获取到的 cname 存在且 domains_cname 不存在 更新
    # cname 或 domains_cname 不存在，developer 存在 更新
    if ad["cname"] and not domains_data[1]:
        # 更新 cname, ename, developer
        cname = pymysql.escape_string(ad['cname']) if ad['cname'] else ad['cname']
        ename = pymysql.escape_string(ad['ename']) if ad['ename'] else ad['ename']
        update_domains_brand(host=ad["host"], developer=developer, cname=cname, ename=ename, category=category)
    else:
        if developer and not domains_data[3]:
            # 只更新 developer，其余与原表不变
            cname = pymysql.escape_string(domains_data[1]) if domains_data[1] else domains_data[1]
            ename = pymysql.escape_string(domains_data[2]) if domains_data[2] else domains_data[2]
            update_domains_brand(host=ad["host"], developer=developer, cname=cname, ename=ename, category=category)
    # insert_es_domains(addata_id=addata_id, domains_id=domains_data[0], developer=developer)
    return


def update_info(developer=None, host=None, ad=None, addata_id=None, category=None):
    # 不存在 获取cname, ename, logo, have_logo 等广告信息，并插入domains 表
    insert_domains_data(host=host, cname=ad["cname"], ename=ad["ename"], logo=ad["logo"], have_logo=ad["have_logo"], hostmd5=comm.get_md5(text=host), developer=developer, category=category)
    domain_info = get_domains_data(host=host)
    # 将 addata_2018 表 与 domains 表 中的 id 插入 addata_domain 表
    insert_addata_domain(addata_id=addata_id, domains_id=domain_info[0])
    # 更新 es 中的 developer 等信息
    # insert_es_domains(addata_id=addata_id, domains_id=domain_info[0], developer=developer)


def get_ad_info(target_url):
    ad_info = {}
    html = s.fetch(target_url)
    item = handle(target_url, html)
    if not item:
        return
    ad_info["ename"] = item['ename'] if item['ename'] else ""
    if item['cname']:
        cname = item['cname']
    elif item['shop']:
        cname = item['shop']
    elif item['brand']:
        cname = item['brand']
    else:
        cname = ""
    ad_info["cname"] = cname
    ad_info["logo"] = item['icon']
    ad_info["have_logo"] = 1 if item['icon'] else 0
    ad_info["host"] = item['identifier']
    if not ad_info["host"]:
        return
    ad_info["company"] = item["company"]
    ad_info["category"] = item["category"]
    ad_info["developer"] = item["developer"]
    return ad_info


while True:
    try:
        s = Spider()
        q = queue.Queue()
        run()
    except:
        print(traceback.format_exc())


