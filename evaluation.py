# -*- coding: utf-8 -*-
# @Author  : Huang Deng
# @Email   : 280418304@qq.com
# @File    : evaluation.py
# @Software: PyCharm
import numpy as np
import torch
import pickle

from Model import Model


def evaluation(model, params_file_path):

    model.load_state_dict(torch.load(params_file_path))
    model.eval()

    acc_set = []
    avg_loss_set = []
    squaredError = []
    for idx, data in enumerate(model.valid_loader()):
        usr, mov, score_label = data
        usr_v = [torch.tensor(var) for var in usr]
        mov_v = [torch.tensor(var) for var in mov]

        _, _, scores_predict = model(usr_v, mov_v)

        pred_scores = scores_predict.detach().numpy()

        avg_loss_set.append(np.mean(np.abs(pred_scores - score_label)))
        squaredError.extend(np.abs(pred_scores - score_label) ** 2)

        diff = np.abs(pred_scores - score_label)
        diff[diff > 0.5] = 1
        acc = 1 - np.mean(diff)
        acc_set.append(acc)
    RMSE = np.sqrt(np.sum(squaredError) / len(squaredError))
    return np.mean(acc_set), np.mean(avg_loss_set), RMSE


# 定义特征保存函数
def get_usr_mov_features(model, params_file_path):
    torch.device('cpu')
    usr_pkl = {}
    mov_pkl = {}

    # 定义将list中每个元素转成tensor的函数
    def list2tensor(inputs, shape):
        inputs = np.reshape(np.array(inputs).astype(np.int64), shape)
        return torch.tensor(inputs)

    # 加载模型参数到模型中，设置为验证模式eval（）
    model.load_state_dict(torch.load(params_file_path))
    model.eval()
    # 获得整个数据集的数据
    dataset = model.Dataset.dataset

    for i in range(len(dataset)):
        # 获得用户数据，电影数据，评分数据
        # 本案例只转换所有在样本中出现过的user和movie，实际中可以使用业务系统中的全量数据
        usr_info, mov_info, score = dataset[i]['usr_info'], dataset[i]['mov_info'], dataset[i]['scores']
        usrid = str(usr_info['usr_id'])
        movid = str(mov_info['mov_id'])

        # 获得用户数据，计算得到用户特征，保存在usr_pkl字典中
        if usrid not in usr_pkl.keys():
            usr_id_v = list2tensor(usr_info['usr_id'], [1])
            usr_age_v = list2tensor(usr_info['age'], [1])
            usr_gender_v = list2tensor(usr_info['gender'], [1])
            usr_job_v = list2tensor(usr_info['job'], [1])

            usr_in = [usr_id_v, usr_gender_v, usr_age_v, usr_job_v]
            usr_feat = model.get_usr_feat(usr_in)

            usr_pkl[usrid] = usr_feat.detach().numpy()

        # 获得电影数据，计算得到电影特征，保存在mov_pkl字典中
        if movid not in mov_pkl.keys():
            mov_id_v = list2tensor(mov_info['mov_id'], [1])
            mov_tit_v = list2tensor(mov_info['title'], [1, 1, 15])
            mov_cat_v = list2tensor(mov_info['category'], [1, 6])

            mov_in = [mov_id_v, mov_cat_v, mov_tit_v]
            mov_feat = model.get_mov_feat(mov_in)

            mov_pkl[movid] = mov_feat.detach().numpy()

    print(len(mov_pkl.keys()))
    # 保存特征到本地
    pickle.dump(usr_pkl, open('./usr_feat.pkl', 'wb'))
    pickle.dump(mov_pkl, open('./mov_feat.pkl', 'wb'))
    print("usr / mov features saved!!!")

#存储模型
fc_sizes=[128, 64, 32]
use_mov_title, use_mov_cat, use_age_job = True, True, True
model = Model(use_mov_title, use_mov_cat, use_age_job,fc_sizes)
param_path = "./checkpoint/epoch9.pdparams"
get_usr_mov_features(model, param_path)
#对模型进行评价
# param_path = "./checkpoint/epoch"
#
# for i in range(10):
#     acc, mae,RMSE = evaluation(model, param_path+str(i)+'.pdparams')
#     print("ACC:", acc, "MAE:", mae,'RMSE:',RMSE)