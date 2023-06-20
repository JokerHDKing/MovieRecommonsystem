# -*- coding: utf-8 -*-
# @Author  : Huang Deng
# @Email   : 280418304@qq.com
# @File    : app.py
# @Software: PyCharm
import random
import time

from flask import Flask, render_template, request,redirect
from recomon import chuan
import re
import pymysql
from UserCF import get_movies_info
app=Flask(__name__)
conn = pymysql.connect(
    host="localhost",
    user='root',  # 用户名
    passwd='root',  # 密码
    port=3306,  # 端口，默认为3306
    db='movielens',  # 数据库名称
    charset='utf8',  # 字符编码
    autocommit=True,
)

# 拿到游标
cursor = conn.cursor()
def get_mov_info():
    infodict=dict()
    sql="select * from movies"
    cursor.execute(sql)
    info = cursor.fetchall()
    for i in info:
        info = i[1]
        # 提取括号中的数字
        year_match = re.search(r'\((\d+)\)', info)
        if year_match:
            year = year_match.group(1)
        else:
            year = None
        # 删除括号和里面的数字
        clean_title = re.sub(r'\s*\([^)]*\)', '', info)

        infodict[i[0]]={
            'movid':i[0],
            'title':clean_title,
            'year':year,
            'cat': i[2].replace("\r",""),
            'url':i[3]
        }
    sql="select movieId from movies"
    cursor.execute(sql)
    id_list = [item[0] for item in cursor.fetchall()]

    return infodict,id_list
moviesinfo ,id_list= get_mov_info()

def sp(vv):
    for i, value in vv.items():
       info=value['movie_info'][1]
       # 提取括号中的数字
       year_match = re.search(r'\((\d+)\)', info)
       if year_match:
           year = year_match.group(1)
       else:
           year = None
       # 删除括号和里面的数字
       clean_title = re.sub(r'\s*\([^)]*\)', '', info)
       value['movie_info'][1]=clean_title
       value['movie_info'].append(year)

@app.route("/",methods=['GET','POST'])
def index():
    movie_info=list()
    #随机选取10张电影图片
    random_ids = random.sample(id_list, 14)
    for i in random_ids:
        movie_info.append(moviesinfo[i])
    if request.method=='POST':
        userid=request.form.get('username')
        sql = f"select UserId from users where username='{userid}'"
        cursor.execute(sql)
        m = cursor.fetchone()
        if m==None:
            error="登录失败，请检查用户名和密码"
            return   render_template('login.html', error=error)
        t=m[0]
        if t<=6040:
            rec, read = chuan(t)
            print(rec)
        else:
            rec=get_movies_info(int(t))
            print(rec)
        sp(rec)
        return render_template('index.html', userid=t,movie_info=movie_info,username=userid,rec=rec)
    # else:
    return render_template('index.html',userid=0,movie_info=movie_info)

@app.route("/login",methods=['GET','POST'])
def login():

    return render_template('login.html')



@app.route("/rec", methods=['POST'])
def rec_now():
    usr_id = request.form.get('userid')
    if usr_id is None:
        usr_id=1
    m=int(usr_id)
    rec,read=dict(),dict()
    if m<=6040:
        usr_id=m
        rec,read=chuan(usr_id)
        sp(rec)
        sp(read)
        print(rec)
        print(read)
    else:
        usr_id=int(m)
        rec=get_movies_info(usr_id)
    return render_template('rec.html',rec=rec,read=read,id=usr_id)

#注册
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        Occupation=1
        usrname = request.form.get('username')
        age = int(request.form.get('age'))
        gender = request.form.get('gender')
        # passward = request.form.get('password')
        sql=f"insert into users  (gender,Occupation,username,age) values ('{gender}',{Occupation},'{usrname}',{age})"
        print(sql)
        cursor.execute(sql)
        conn.commit()
        return redirect('/')
    return render_template('register.html')

#目的将用户的点击行为判断为一次评分
@app.route('/save',methods=['GET','POST'])
def save():
    movid=int(request.form.get("movieId"))
    usrid=int(request.form.get("usrid"))
    socre=3
    print(usrid)
    print(movid)
    timestamp = int(time.time())
    print(timestamp)
    if usrid >0:
        sql1=f"SELECT rating FROM ratings WHERE movieId = {movid} AND userId = {usrid}"
        print(sql1)
        cursor.execute(sql1)
        results = cursor.fetchall()
        if results:
            ratings = [result[0] for result in results]
            max_rating = max(ratings)
            if max_rating > 3:
                print("最大评分大于3，不插入新记录")
            else:
                sql=f"INSERT INTO ratings (movieId, usrid, rating,timestamp) VALUES ({movid},{usrid},{socre})"
                print(sql)
                cursor.execute(sql)
                print("插入新记录成功")
            print(results)
        else:
            # 如果记录不存在，则插入新的记录
            sql=f"INSERT INTO ratings ( userId, movieId,rating,timestamp) VALUES ({usrid}, {movid}, {socre},{timestamp})"
            print(sql)
            cursor.execute(sql)
            print("插入新记录成功")


    return redirect("/")


if __name__ == '__main__':
    app.run(port=2020,host="127.0.0.1",debug=True)