# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:03:31 2019

@author: 吴清典
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


movies = pd.read_csv('tmdb_5000_movies.csv')

creditsss = pd.read_csv('tmdb_5000_credits.csv')

'''
# encoding=utf-8
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
# 准备数据集
iris=load_iris()
# 获取特征集和分类标识
features = iris.data
labels = iris.target

# 随机抽取 33% 的数据作为测试集，其余为训练集 使用sklearn.model_selection train_test_split 训练
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=0.33, random_state=0)
# 创建 CART 分类树
clf = DecisionTreeClassifier(criterion='gini')
# 拟合构造 CART 分类树
clf = clf.fit(train_features, train_labels)
# 用 CART 分类树做预测  得到预测结果
test_predict = clf.predict(test_features)
# 预测结果与测试集结果作比对
score = accuracy_score(test_labels, test_predict)
print("CART 分类树准确率 %.4lf" % score)
'''
# coding=utf-8
from sklearn.cluster import Birch
from sklearn.cluster import KMeans

x = movies.loc[:,['popularity','vote_count']]
X = x.values

clf = KMeans(n_clusters=3) #表示类簇数为3，聚成3类数据，clf即赋值为KMeans
y_pred = clf.fit_predict(X) #载入数据集X，并且将聚类的结果赋值给y_pred

clf = KMeans(n_clusters=3)
y_pred = clf.fit_predict(X)
#输出完整Kmeans函数，包括很多省略参数
print(clf)
print('----------------')
#输出聚类预测结果，20行数据，每个y_pred对应X一行，聚成3类，类标为0、1、2
print(y_pred)
import matplotlib.pyplot as plt
import numpy as np
print('-----------------')

#获取第一列和第二列数据 使用for循环获取 n[0]表示X第一列
xx = [n[0] for n in X]
print(xx)
print('-----------------')
y = [n[1] for n in X]
print(y)
print('-----------------')

#绘制散点图 参数：x横轴 y纵轴 c=y_pred聚类预测结果 marker类型 o表示圆点 *表示星型 x表示点
plt.scatter(xx, y, c=y_pred, marker='o')
#绘制标题
plt.title("Kmeans-movie Data")
#绘制x轴和y轴坐标
plt.xlabel("popularity")
plt.ylabel("vote_count")
#设置右上角图例
plt.legend(["A","B","C"])
plt.savefig('聚类分析popularity和vote_count')
#显示图形
plt.show()
