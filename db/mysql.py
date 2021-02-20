# -*- encoding: utf-8 -*-
import pymysql
from config.config import Config


class Mysql():
    def __init__(self):
        config = Config()
        self.host = config.getMysqlHost()
        self.user = config.getMysqlUser()
        self.port = int(config.getMysqlPort())
        self.db = config.getMysqlDb()
        self.pwd = config.getMysqlPasswd()

    def process(self, item):
        try:
            client = pymysql.connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db,port = self.port)
            sql = 'insert into ad_brand_detail(shop,brand,kd,description,icon,iconmd5,title,url,ename,cname,host,identifier,category,company,content,advertiser) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            cursor = client.cursor()
            cursor.execute(sql, (
                item['shop'], item['brand'], item['kd'], item['description'], item['icon'], item['iconmd5'],
                item['title'],
                item['url'], item['ename'], item['cname'], item['host'], item['identifier'], item['category'],
                item['company'], item['content'], item['advertiser']))
            client.commit()
            cursor.close()
            client.close()
        except Exception as e:
            client.close()

    def get_urls(self, id):
        data=None
        try:
            client = pymysql.connect(host='rm-bp1c5x1rhig246p88o.mysql.rds.aliyuncs.com',user='adbug',passwd='2YeoyszrQoUhzubO',db='adbugnew',port=3306)
            # client = pymysql.connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db,port = self.port)
            cursor = client.cursor()
            cursor.execute('select id,target_url,advertiser from addata_2018 where id<%d order by id desc limit 1000' % id)
            data= cursor.fetchall()
        except Exception as e:
            pass
        return data

    def get_id(self, identifier):
        id = None
        try:
            client = pymysql.connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db,port = self.port)
            cursor = client.cursor()
            cursor.execute("select id  from ad_brand_detail where identifier = '{0}'".format(identifier))
            id = cursor.fetchall()[0][0]
        except Exception as e:
            pass
        return id

    def insert(self, item):
        try:
            client = pymysql.connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db,port = self.port)
            sql = 'insert into ad_brand(advertiserid,detailid,advertiser) values(%s,%s,%s)'
            cursor = client.cursor()
            cursor.execute(sql, (item['advertiserid'], item['detailid'], item['advertiser']))
            client.commit()
            cursor.close()
            client.close()
        except Exception as e:
            client.close()

    
