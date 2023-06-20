# -*- coding: utf-8 -*-
# @Author  : Huang Deng
# @Email   : 280418304@qq.com
# @File    : train.py
# @Software: PyCharm
import torch
from torch import optim
import torch.nn.functional as F

from Model import Model


def train(model):
    # 配置训练参数
    lr = 0.001
    Epoches = 10
    torch.device('cpu')

    # 启动训练
    model.train()
    # 获得数据读取器
    data_loader = model.train_loader
    # 使用adam优化器，学习率使用0.01
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(0, Epoches):
        for idx, data in enumerate(data_loader()):
            # 获得数据，并转为tensor格式
            usr, mov, score = data
            usr_v = [torch.tensor(var) for var in usr]
            mov_v = [torch.tensor(var) for var in mov]
            scores_label = torch.tensor(score)
            # 计算出算法的前向计算结果
            _, _, scores_predict = model(usr_v, mov_v)
            # 计算loss
            loss = F.mse_loss(scores_predict, scores_label)
            avg_loss = torch.mean(loss)

            if idx % 500 == 0:
                print("epoch: {}, batch_id: {}, loss is: {}".format(epoch, idx, avg_loss.detach().numpy()))

            # 损失函数下降，并清除梯度
            optimizer.zero_grad()
            avg_loss.backward()
            optimizer.step()
        # 每个epoch 保存一次模型
        torch.save(model.state_dict(), './checkpoint/epoch' + str(epoch) + '.pdparams')

# 启动训练
fc_sizes=[128, 64, 32]
use_mov_title, use_mov_cat, use_age_job = True, True, True
model = Model(use_mov_title, use_mov_cat, use_age_job,fc_sizes)
train(model)