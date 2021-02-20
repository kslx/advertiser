# !/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pymysql
import time
import traceback

from pymongo import MongoClient
from os.path import abspath, dirname
from DBUtils.PooledDB import PooledDB
from configparser import ConfigParser
from pymysql.cursors import DictCursor

cf = ConfigParser()
current_path = abspath(dirname(__file__))
cf.read(current_path + r"/conf/db.ini")


class MySQLData(object):

    def __init__(self, host=None, user=None, password=None, keys=None, database=None, form="dict"):
        self.cf = cf
        self.form = form
        self.host = host
        self.keys = keys
        self.user = user
        self.database = database
        self.password = password
        self.pool = PooledDB(
            port=3306,
            mincached=5,
            maxcached=15,
            blocking=True,
            maxusage=None,
            charset='utf8',
            creator=pymysql,
            maxconnections=100,
            host=self.host if self.host else self.cf.get(self.keys, "host"),
            user=self.user if self.user else self.cf.get(self.keys, "user"),
            database=self.database if self.database else self.cf.get(self.keys, "database"),
            password=self.password if self.password else self.cf.get(self.keys, "password"),
        )
        self.conn = pymysql.connect(
            port=3306,
            host=self.host if self.host else self.cf.get(self.keys, "host"),
            user=self.user if self.user else self.cf.get(self.keys, "user"),
            database=self.database if self.database else self.cf.get(self.keys, "database"),
            password=self.password if self.password else self.cf.get(self.keys, "password"),
        )
        self.cursor = self.conn.cursor(cursor=DictCursor) if self.form == "dict" else self.conn.cursor()

    def __new__(cls, *args, **kw):
        """启用单例模式"""
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def get_connect(self, form="dict", keys=None):
        """
        :param form: dict：字典，否：元组
        """
        self.keys = keys
        conn = pymysql.connect(
            port=3306,
            host=self.host if self.host else self.cf.get(self.keys, "host"),
            user=self.user if self.user else self.cf.get(self.keys, "user"),
            database=self.database if self.database else self.cf.get(self.keys, "database"),
            password=self.password if self.password else self.cf.get(self.keys, "password"),
        )
        cur = conn.cursor(cursor=DictCursor) if form == "dict" else conn.cursor()
        return conn, cur

    def get_mysql_pool(self, database=None):
        """
        获取 MySQL 数据库的连接池对象
        @maxcached：链接池中最多闲置的链接，0和None不限制，默认为 0；
        @maxusage：一个链接最多被重复使用的次数，None表示无限制，默认为 None；
        @mincached: 初始化时，链接池中至少创建的空闲的链接，0表示不创建，默认为 0；
        @maxconnections: 连接池允许的最大连接数，0和None表示不限制连接数，默认为 0；
        @blocking：连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错，默认为 False；
        """
        pool = PooledDB(
            port=3306,
            mincached=5,
            maxcached=15,
            blocking=True,
            maxusage=None,
            charset='utf8',
            creator=pymysql,
            maxconnections=100,
            host=self.host if self.host else self.cf.get(self.keys, "host"),
            user=self.user if self.user else self.cf.get(self.keys, "user"),
            database=database if database else self.cf.get(self.keys, "database"),
            password=self.password if self.password else self.cf.get(self.keys, "password"),
        )
        return pool

    def connect(self, form='dict', pool=None):
        """启动连接"""
        conn = pool.connection() if pool else self.pool.connection()
        cursor = conn.cursor(cursor=DictCursor) if form == "dict" else conn.cursor()
        return conn, cursor

    # 封装执行命令
    def execute(self, sql, param=None, autoclose=True, form='dict'):
        """
        【主要判断是否有参数和是否执行完就释放连接】
        :param sql: 字符串类型，sql语句
        :param param: sql语句中要替换的参数"select %s from tab where id=%s" 其中的%s就是参数
        :param autoclose: 是否关闭连接
        :return: 返回连接conn和游标cursor
        """
        conn, cursor = self.connect(form=form)  # 从连接池获取连接
        try:
            cursor.execute(sql, args=param) if param else cursor.execute(sql)
            conn.commit()
            if autoclose:
                self.connect_close(cursor, conn)
        except:
            print(traceback.format_exc())
        return cursor

    def connect_close(self, conn=None, cursor=None):
        """关闭连接"""
        cursor.close()
        conn.close()

    def fetch_all(self, sql, param=None, form="dict", count=0):
        """
        批量查询
        :param args: sql语句中要替换的参数"select %s from tab where id=%s" 其中的%s就是参数
        """
        cursor = self.execute(sql, param=param, form=form)
        select_res = cursor.fetchall() if count == 0 else cursor.fetchmany(count)
        return select_res

    def fetch_one(self, sql, param=None, form="dict"):
        """
        查询单条数据
        :param args: sql语句中要替换的参数"select %s from tab where id=%s" 其中的 %s 就是参数
        """
        cursor = self.execute(sql, param=param, form=form)
        result = cursor.fetchone()
        return result

    def insertmany(self, sql_lis, param=None, form="dict"):
        """
        插入多条数据
        :param sql_lis: sql 列表或元组
        :param param: 必须是元组或列表[(), ()]或((), ())
        """
        conn, cursor = self.connect(form=form)  # 从连接池获取连接
        try:
            cursor.executemany(sql_lis, param) if param else cursor.execute(sql_lis)
            conn.commit()
            self.connect_close()
        except:
            print(traceback.format_exc())
            conn.rollback()
            self.connect_close(cursor, conn)

    def get_db_from_pool(self, pool=None, form="dict"):
        while True:
            try:
                conn = pool.connection()
                cursor = conn.cursor(cursor=DictCursor) if form == "dict" else conn.cursor()
                conn.ping(reconnect=True)
                return conn, cursor
            except:
                time.sleep(18000)
                self.get_db_from_pool(pool=pool)


class MongoData(object):

    def __init__(self, host=None, user=None, password=None, keys=None, database=None, port=27017, colletion=None):
        self.cf = cf
        self.colletion = colletion
        self.keys = keys
        self.host = host if host else self.cf.get(self.keys, "host")
        self.port = self.cf.get(self.keys, "port") if self.cf.get(self.keys, "port") else port
        self.user = user if user else self.cf.get(self.keys, "user")
        self.database = keys if keys else database
        self.password = password if password else self.cf.get(self.keys, "password")
        # 无密码连接mongodb 数据库
        self.client = MongoClient(self.host, int(self.port))  # 建立客户端对象
        # 使用默认数据库 admin 验证密码，再换其他数据库
        self.db = self.client.admin  # mydb数据库，同上解释
        self.db.authenticate(self.user, self.password)
        self.db = self.client[self.database]  # 连接mydb数据库，没有则自动创建
        self.myset = self.db[self.colletion]  # 使用test_set集合，没有则自动创建
        self.myset.insert_one({"name": "zhangsan", "age": 18})  # 插入一条数据，如果没出错那么说明连接成功

    def get_connect(self, auth=None):
        myclient = MongoClient('mongodb://{0}:{1}@{2}:{3}/'.format(self.user, self.password, self.host, self.port))
        mydb = myclient[self.database]
        db = mydb[self.colletion]


if __name__ == '__main__':
    # current_path = abspath(dirname(__file__))
    # print(os.path.abspath(os.path.dirname(__file__)))
    # host = 'rm-bp1gd84j036vfip2d8o.mysql.rds.aliyuncs.com'
    # user = 'oom10'
    # passwd = 'Y5djQBVpHPWYH9tZ'
    # db = 'adbug2'
    service = MongoData(keys="crawlab_pro", colletion="demo")
    # print(service.cf.get(service.keys, "user"))
    # sql = "select * from addata2_test where id=10"
    # service.fetch_one(sql=sql)
    # # print(host)
    # pool = service.get_mysql_pool_2()
    # conn, cur = service.get_db_from_pool(pool=pool)
    # cur.execute("select * from addata_keywords_tb_dkk where status=0 limit 0,100")
    # key_infos = cur.fetchall()
    # for key_info in key_infos:
    #     print(key_info)
