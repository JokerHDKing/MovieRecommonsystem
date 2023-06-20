# -*- coding: utf-8 -*-
# @Time    : 2023-06-16 16:08
# @Author  : Huang Deng
# @Email   : 280418304@qq.com
# @File    : 1.py
# @Software: PyCharm
import pandas as pd
import pymysql

conn = pymysql.connect(
    host="localhost",
    user='root',  # 用户名
    passwd='root',  # 密码
    port=3306,  # 端口，默认为3306
    db='movielens',  # 数据库名称
    charset='utf8',  # 字符编码
)
link=pd.read_csv('links.csv', dtype = {'imdbId' : str,'movieId':str})
for i in link.values:
    id=i[0]
    imdb=i[1]
    url="https://www.imdb.com/title/tt"+imdb
    sql=f"update movies set url='{url}' where movieId={id}"+";"
    print(sql)