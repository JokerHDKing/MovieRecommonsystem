# -*- coding: utf-8 -*-
# @Author  : Huang Deng
# @Email   : 280418304@qq.com
# @File    : recomon.py
# @Software: PyCharm
import csv
import pickle
import numpy as np
import torch

movie_data_path = "work/ml-1m/movies.dat"
usr_feat_path = 'usr_feat.pkl'
mov_feat_path='mov_feat.pkl'

def read_movies_from_csv(file_path):
    movies_info =dict()
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        # 跳过表头
        next(reader)
        # 逐行读取数据
        for row in reader:
            movies_info[row[0]]={
                'imdbId':row[1]
            }
    return movies_info

movies_info = read_movies_from_csv('links.csv')

def recommend_mov_for_usr(usr_id, top_k, pick_num, usr_feat_dir, mov_feat_dir, mov_info_path):
    assert pick_num <= top_k
    # 读取电影和用户的特征
    usr_feats = pickle.load(open(usr_feat_dir, 'rb'))
    mov_feats = pickle.load(open(mov_feat_dir, 'rb'))
    usr_feat = usr_feats[str(usr_id)]

    cos_sims = []

    # 索引电影特征，计算和输入用户ID的特征的相似度
    for idx, key in enumerate(mov_feats.keys()):
        mov_feat = mov_feats[key]
        usr_feat = torch.tensor(usr_feat)
        mov_feat = torch.tensor(mov_feat)
        # 计算余弦相似度
        sim = torch.nn.functional.cosine_similarity(usr_feat, mov_feat)
        cos_sims.append(sim.numpy()[0])
    # 对相似度排序
    index = np.argsort(cos_sims)[-top_k:]
    mov_info = {}
    # 读取电影文件里的数据，根据电影ID索引到电影信息
    with open(mov_info_path, 'r', encoding="ISO-8859-1") as f:
        data = f.readlines()
        for item in data:
            item = item.strip().split("::")
            mov_info[str(item[0])] = item

    print("推荐可能喜欢的电影是：")
    res = []
    # 加入随机选择因素，确保每次推荐的都不一样
    while len(res) < pick_num:
        val = np.random.choice(len(index), 1)[0]
        idx = index[val]
        mov_id = list(mov_feats.keys())[idx]
        if mov_id not in res:
            res.append(mov_id)
    rec_dict=dict()
    for id in res:
        print("mov_id:", id, mov_info[str(id)])
        url="https://www.imdb.com/title/tt"+movies_info.get("2762")['imdbId']
        mov_info[str(id)].append(url)
        rec_dict[id] = {
            "movie_info": mov_info[str(id)]
        }
    return  rec_dict

def usr_read(usr_a ,topk ):
    ##########################################
    ## 获得ID为usr_a的用户评分过的电影及对应评分 ##
    ##########################################
    rating_path = "work/ml-1m/ratings.dat"
    # 打开文件，ratings_data
    with open(rating_path, 'r') as f:
        ratings_data = f.readlines()

    usr_rating_info = {}
    for item in ratings_data:
        item = item.strip().split("::")
        # 处理每行数据，分别得到用户ID，电影ID，和评分
        usr_id, movie_id, score = item[0], item[1], item[2]
        if usr_id == str(usr_a):
            usr_rating_info[movie_id] = float(score)

    # 获得评分过的电影ID
    movie_ids = list(usr_rating_info.keys())
    print("ID为 {} 的用户，评分过的电影数量是: ".format(usr_a), len(movie_ids))

    #####################################
    ## 选出ID为usr_a评分最高的前topk个电影 ##
    #####################################
    ratings_topk = sorted(usr_rating_info.items(), key=lambda item: item[1])[-topk:]

    movie_info_path = "work/ml-1m/movies.dat"
    # 打开文件，编码方式选择ISO-8859-1，读取所有数据到data中
    with open(movie_info_path, 'r', encoding="ISO-8859-1") as f:
        data = f.readlines()

    movie_info = {}
    for item in data:
        item = item.strip().split("::")
        # 获得电影的ID信息
        v_id = item[0]
        movie_info[v_id] = item
    print(f"已看电影前{top_k}部")
    read_dict=dict()
    for k, score in ratings_topk:
        read_dict[k]={
            "score":score,
            "movie_info":movie_info[k]
        }
        print("电影ID: {}，评分是: {}, 电影信息: {}".format(k, score, movie_info[k]))
    return  read_dict

top_k, pick_num = 10, 6
usr_id = 6040



def chuan(usr_id):
    rec=recommend_mov_for_usr(usr_id, top_k, pick_num, usr_feat_path, mov_feat_path, movie_data_path)
    read=usr_read(usr_id,top_k)

    return  rec,read
# recommend_mov_for_usr(usr_id, top_k, pick_num, usr_feat_path, mov_feat_path, movie_data_path)
# read = usr_read(usr_id, top_k)
#
