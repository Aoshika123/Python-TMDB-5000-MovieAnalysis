# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 11:57:49 2019

@author: 吴清典
"""

#导入需要的包

#数据处理
import json
import pandas as pd
import numpy as np
from pandas import Series,DataFrame
from datetime import datetime
#不显示警告
import warnings
warnings.filterwarnings('ignore') 
#数据可视化
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
from scipy.misc import imread

#导入电影数据
movies_file = r'E:\python代码\python数据分析大作业\tmdb_5000_movies.csv '
credits_file = r'E:\python代码\python数据分析大作业\tmdb_5000_credits.csv '
credits = pd.read_csv('tmdb_5000_movies.csv')
movies = pd.read_csv('tmdb_5000_credits.csv')


#合并两个数据表
fulldf = pd.concat([credits,movies],axis=1)
#查看合并结果
fulldf.info()


#选取子集
moviesdf=fulldf[['original_title','crew','release_date','genres','keywords','production_companies',
                 'production_countries','revenue','budget','runtime','vote_average']]
moviesdf.info()

moviesdf["profit"] = moviesdf['revenue']- moviesdf['budget']
moviesdf.head(2)

#缺失值处理
# release_date缺失一个数据
# runtime 缺失两个
# 我们可以到网上查询来补充
#找出缺失的
release_date_null = moviesdf["release_date"].isnull()
moviesdf.loc[release_date_null,:]



#同理查找出缺失的runtime 并填充
runtime_null = moviesdf["runtime"].isnull()
moviesdf.loc[runtime_null,:]

# 电影《Chiamatemi Francesco - Il Papa della gente》的时长为98分钟；
# 电影《To Be Frank, Sinatra at 100》的时长为81分钟
values1 = {'runtime':98.0}
values2 = {'runtime':81.0}
moviesdf.fillna(value=values1,limit=1,inplace=True)
moviesdf.fillna(value=values2,limit=1,inplace=True)
# moviesdf.info()
moviesdf.loc[runtime_null,:]

#数据格式装换
# json.loads():将字符串编码为一个python对象
# genres列格式化，建立包含所有genre类型的列表
#先将list编码成json(不需要) , 然后再解码成Python对象
# moviesdf['genres'] = moviesdf['genres'].apply(json.dumps) 
moviesdf['genres'] = moviesdf['genres'].apply(json.loads)
# 根据json数据格式自定义函数解码json数据
def decode(column):
    z = []
    for i in column:
        z.append(i['name'])
    return ' '.join(z)
moviesdf['genres'] = moviesdf['genres'].apply(decode)
moviesdf.head(2)

# 建立genres列表，提取电影的类型
genres_list = set()    
# set()不可改变,不重复集合
# str() 函数将对象转化为适于人阅读的形式
# union() 方法返回两个集合的并集，即包含了所有集合的元素，重复的元素只会出现一次。
for i in moviesdf['genres'].str.split(' '):
    genres_list = set().union(i,genres_list)
    genres_list = list(genres_list)
    genres_list
    
genres_list.remove('')
print(genres_list)  

# release_date 处理
# 保留日期中的年份
# pandas.series.dt.year  #the year of datetime
moviesdf['release_date'] = pd.to_datetime(moviesdf['release_date']).dt.year
columns = {'release_date':'year'}
moviesdf.rename(columns=columns,inplace=True) #将该列改成year
#moviesdf['year'].apply(int).head() #转换为int

# 从类型列表中 遍历
# pandas时，str.contains()进行一次模糊匹配多个值
for genre in genres_list:
    moviesdf[genre] = moviesdf['genres'].str.contains(genre).apply(lambda x:1 if x else 0)

moviesdf[genre].tail()
genre_year = moviesdf.loc[:,genres_list]
genre_year.tail(2)

# 把年份作为索引标签
genre_year.index = moviesdf['year']
# 将数据集按年份分组并求和，得出每个年份，各电影类型的电影总数
genresdf = genre_year.groupby('year').sum()
# 查看数据集,tail默认查看后5行的数据
genresdf.tail() 

genresdfSum = genresdf.sum(axis=0).sort_values(ascending=False)

#计算百分比
genres_pie = genresdfSum / genresdfSum.sum()

# 设置other类，当电影类型所占比例小于%1时，全部归到other类中
others = 0.01
genres_pie_otr = genres_pie[genres_pie >= others]
genres_pie_otr['Other'] = genres_pie[genres_pie < others].sum()

# 所占比例小于或等于%2时，对应的饼状图往外长高一截
explode = (genres_pie_otr <= 0.02) / 10 + 0.04

# 设置饼状图的参数
genres_pie_otr.plot(kind='pie',label='',startangle=50,shadow=False,figsize=(10,10),autopct='%1.1f%%',explode=explode)

plt.title('各种电影类型所占的比例')
plt.savefig('电影类型所占比例')