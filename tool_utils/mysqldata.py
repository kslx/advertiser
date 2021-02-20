# !/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pymysql
import time

from os.path import abspath, dirname
from DBUtils.PooledDB import PooledDB
from configparser import ConfigParser


class mysqldata(object):
    cf = ConfigParser()
    current_path = abspath(dirname(__file__))
    cf.read(current_path + r"/conf/db.ini")

    def __init__(self, host=None, user=None, password=None, keys=None):
        self.host = host
        self.keys = keys
        self.user = user
        self.password = password

    def get_mysql_pool(self, db=None):
        """获取线上库的连接池对象"""
        pool = PooledDB(
            creator=pymysql,
            maxconnections=100,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=5,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=15,  # 链接池中最多闲置的链接，0和None不限制
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            port=3306,
            charset='utf8',
            database=db if db else self.cf.get(self.keys, "database"),
            host=self.host if self.host else self.cf.get(self.keys, "host"),
            user=self.user if self.user else self.cf.get(self.keys, "user"),
            password=self.password if self.password else self.cf.get(self.keys, "password")
        )
        return pool

    def get_mysql_pool_2(self, db=None):
        """获取线上库的连接池对象"""
        pool = PooledDB(
            creator=pymysql,
            maxconnections=100,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=5,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=15,  # 链接池中最多闲置的链接，0和None不限制
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            host=self.cf.get(self.keys, "host"),
            port=3306,
            user=self.cf.get(self.keys, "user"),
            password=self.cf.get(self.keys, "password"),
            database=self.cf.get(self.keys, "database"),
            charset='utf8')
        return pool

    def get_db_from_pool(self, pool=None, type=None):
        while True:
            try:
                conn = pool.connection()
                if type == "tuple":
                    cursor = conn.cursor()
                else:
                    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
                conn.ping(reconnect=True)
                return conn, cursor
            except:
                time.sleep(18000)
                self.get_db_from_pool(pool=pool, type=type)


if __name__ == '__main__':
    current_path = abspath(dirname(__file__))
    print(os.path.abspath(os.path.dirname(__file__)))
    # host = 'rm-bp1gd84j036vfip2d8o.mysql.rds.aliyuncs.com'
    # user = 'oom10'
    # passwd = 'Y5djQBVpHPWYH9tZ'
    # db = 'adbug2'
    service = mysqldata(keys="adbug1")
    print(service.cf.get(service.keys, "user"))
    # # print(host)
    # pool = service.get_mysql_pool_2()
    # conn, cur = service.get_db_from_pool(pool=pool)
    # cur.execute("select * from addata_keywords_tb_dkk where status=0 limit 0,100")
    # key_infos = cur.fetchall()
    # for key_info in key_infos:
    #     print(key_info)
