# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 16:38:38 2019

@author: 吴清典
"""

#导入需要的包

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
 
#%matplotlib inline

import json
import warnings
warnings.filterwarnings('ignore')
import seaborn as sns

sns.set(color_codes=True)


#设置表格字体
font = {
    'family' : 'SimHei'
}

matplotlib.rc('font', **font)

#1.1分析之前先理解，整理一下数据

#导入数据
movies = pd.read_csv('tmdb_5000_movies.csv')
creditss = pd.read_csv('tmdb_5000_credits.csv')

print(movies.columns)
print(creditss.columns)
#查看movies中数据
print(movies.head())

 
#查看movies中所有列名，以字典形式存储
print(movies.columns)

 
##查看creditss中数据
print(creditss.head())


#查看creditss中所有列名，以字典形式存储,一共4个列名
print(creditss.columns)
 

#两个数据框中的title列重复了，删除credits中的title列，还剩3个列名
del creditss['title'] 
print(creditss.columns)

#movies中的id列与credits中的movie_id列实际上等同，可当做主键合并数据框
full = pd.merge(movies, creditss, left_on='id', right_on='movie_id', how='left') 
#某些列不在本次研究范围，将其删除
full.drop(['homepage','original_title','overview','spoken_languages',           
           'status','tagline','movie_id'],axis=1,inplace=True) 
#查看数据信息，每个字段数据量。
print(full.info())

#1.2数据清洗
#判断哪些列有缺失值，以True=缺失，False=不缺失，得到release_date，runtime有缺失值。
print(full.isnull().any())

#release_date列有1条缺失数据，将其查找出来
print(full.loc[full['release_date'].isnull()==True])

#根据title经上网搜索，该影片上映日期为2014年6月1日，填补该值
full['release_date'] = full['release_date'].fillna('2014-06-01')

#runtime列有2条缺失数据，将其查找出来
print(full.loc[full['runtime'].isnull()==True])
#根据title经上网搜索，影片时长分别为94分钟和240分钟，填补缺失值
full['runtime'] = full['runtime'].fillna(94, limit=1)#limit=1，限制每次只填补一个值
full['runtime'] = full['runtime'].fillna(240, limit=1)

#将release_date列转换为日期类型

full['release_date'] = pd.to_datetime(full['release_date'], format='%Y-%m-%d', errors='coerce').dt.year
'''
genres,keywords,production_companies,production_countries,cast,crew列为json类型
需要解析json数据，分两步：
1. json本身为字符串类型，先转换为字典列表
2. 再将字典列表转换为，以'|'分割的字符串
定义一个json类型的列名列表
'''
json_column = ['genres','keywords','production_companies',
               'production_countries','cast','crew']
#将各json列转换为字典列表
for column in json_column:
    full[column]=full[column].map(json.loads)
#函数功能：将字典内的键‘name’对应的值取出，生成用'|'分隔的字符串
def getname(x):
    list = []
    for i in x:
        list.append(i['name'])
    return '|'.join(list)

#对genres,keywords,production_companies,production_countries列执行函数
for column in json_column[0:4]:
    full[column] = full[column].map(getname)

#定义提取2名主演的函数：
def getcharacter(x):
    list = []
    for i in x:
        list.append(i['character'])
    return '|'.join(list[0:2])
#对cast列执行函数
full['cast']=full['cast'].map(getcharacter)
#定义提取导演的函数：
def getdirector(x):
    list=[]
    for i in x:
        if i['job']=='Director':
            list.append(i['name'])
    return "|".join(list)
#对crew列执行函数
full['crew']=full['crew'].map(getdirector)

#重命名列
rename_dict = {'release_date':'year','cast':'actor','crew':'director'}
full.rename(columns=rename_dict, inplace=True)
#查看full表格中前2行数据
print(full.head(2))
#备份原始数据框
original_dforiginal_df = full.copy()

#1.3数据可视化
#问题1：研究电影风格随时间的变化趋势，提取所有的电影风格，存储在有去重功能的集合中。


genre_set = set()   #设置空集合
for x in full['genres']:
    genre_set.update(x.split('|'))  #genres数据以'|'来分隔
genre_set.discard('')  #删除''字符
print(genre_set)

#对各种电影风格genre，进行one-hot编码

genre_df = pd.DataFrame()  # 创建空的数据框

for genre in genre_set:
    #如果一个值中包含特定内容，则编码为1，否则编码为0
    genre_df[genre] = full['genres'].str.contains(genre).map(lambda x:1 if x else 0)

#将原数据集中的year列，添加至genre_df数据框中
genre_df['year']=full['year']





#将genre_df按year分组，计算每组之和。groupby之后，year列通过默认参数as_index=True自动转化为df.index

genre_by_year = genre_df.groupby('year').sum()  
genresum_by_year = genre_by_year.sum().sort_values(ascending=False)

#计算每个风格genre的电影总数目，并降序排列，再可视化

fig = plt.figure(figsize=(15,11))   #设置画图框的大小
ax = plt.subplot(1,1,1)     #设置框的位置
ax = genresum_by_year.plot.bar()
plt.xticks(rotation=60)
plt.title('Film genre by year', fontsize=18)    #设置标题的字体大小，标题名
plt.xlabel('genre(电影风格)', fontsize=18)    #X轴名及轴名大小
plt.ylabel('count（数量）', fontsize=18)    #y轴名及轴名大小
plt.show()  #可以用查看数据画的图。

#保存图片


#筛选出电影风格TOP9


genre_by_year = genre_by_year[['Drama','Comedy','Thriller','Action','Romance',

                               'Adventure','Crime', 'Science Fiction',

                               'Horror']].loc[1960:,:]

year_min = full['year'].min()   #最小年份
year_max = full['year'].max()   #最大年份

#可视化电影风格genre随时间的变化趋势(1960年至今)

fig = plt.figure(figsize=(10,8))
ax1 = plt.subplot(1,1,1)
plt.plot(genre_by_year)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Film count', fontsize=12)
plt.title('Film count by year', fontsize=15)
plt.xticks(range(1960, 2017, 10))  #横坐标每隔10年一个刻度

#plt.legend(loc='best',ncol=2) #https://blog.csdn.net/you_are_my_dream/article/details/53440964

plt.legend(['Drama(戏剧类)','Comedy(喜剧类)','Thriller(惊悚类)','Action(动作)','Romance(浪漫类)',
                               'Adventure(Adventure)','Crime(犯罪类)', 'Science Fiction(科幻类)',
                               'Horror(惊恐类)'], loc='best',ncol=2) #设置说明标签
fig.savefig('film count by year.png',dpi=200)

#可以看出，从上世纪90年代开始，整个电影市场呈现爆发式增长。
#其中，排名前五的戏剧类（Drama）、喜剧类（Comedy）、惊悚类（Thriller）、浪漫类（Romance）、动作（Action电影数量增长显著。


f, (ax1) = plt.subplots(figsize = (16,12),nrows=1)
 
# cmap用cubehelix map颜色
cmap = sns.cubehelix_palette(start = 1.5, rot = 3, gamma=0.8, as_cmap = True)
pt = genre_df.corr()   # pt为数据框或者是协方差矩阵
sns.heatmap(np.abs(pt), linewidths = 0.05, ax = ax1,cmap=cmap,annot=True,vmin=0,vmax=1)
ax1.set_title('相关系数矩阵')
f.savefig('相关系数矩阵')
print(pt)
#问题2：不同风格电影的收益能力

#增加收益列 收益列 = 收入 - 花费
full['profit'] = full['revenue']-full['budget']

#创建收益数据框

profit_df = pd.DataFrame()#创建空的数据框
profit_df = pd.concat([genre_df.iloc[:,:-1],full['profit']],axis=1)  #合并
print(profit_df.head())#查看新数据框信息

#创建一个Series，其index为各个genre，值为按genre分类计算的profit之和

profit_by_genre = pd.Series(index=genre_set)
for genre in genre_set:
    profit_by_genre.loc[genre]=profit_df.loc[:,[genre,'profit']].groupby(genre, as_index=False).sum().loc[1,'profit']
print(profit_by_genre)

#创建一个Series，其index为各个genre，值为按genre分类计算的budget之和
budget_df = pd.concat([genre_df.iloc[:,:-1],full['budget']],axis=1)
budget_df.head(2)
budget_by_genre = pd.Series(index=genre_set)
for genre in genre_set:
    budget_by_genre.loc[genre]=budget_df.loc[:,[genre,'budget']].groupby(genre,as_index=False).sum().loc[1,'budget']
print(budget_by_genre)

#向合并数据框
profit_rate = pd.concat([profit_by_genre, budget_by_genre],axis=1)
profit_rate.columns=['profit','budget']   #更改列名
#加收益率列
profit_rate['profit_rate'] = (profit_rate['profit']/profit_rate['budget'])*100
profit_rate.sort_values(by=['profit','profit_rate'], ascending=False, inplace=True)
print(profit_rate)




#x为索引长度的序列
x = list(range(len(profit_rate.index)))

#可视化不同风格电影的收益（柱状图）和收益率（折线图）
xl = list(range(len(genre_df.index)))

fig = plt.figure(figsize=(18,13))
ax1 = fig.add_subplot(111)
plt.bar(x, profit_rate['profit'],label='profit',alpha=0.7)
plt.xticks(x,genre_df,rotation=60,fontsize=12) # 数据，下标，旋转角度，字体大小
plt.yticks(fontsize=12)
ax1.set_title('Profit by genres', fontsize=20)
ax1.set_ylabel('Film Profit',fontsize=18)
ax1.set_xlabel('Genre',fontsize=18)
ax1.set_ylim(0,1.2e11)
ax1.legend(loc=2,fontsize=15)

#次纵坐标轴标签设置为百分比显示

import matplotlib.ticker as mtick
ax2 = ax1.twinx()
ax2.plot(x, profit_rate['profit_rate'],'ro-',lw=2,label='profit_rate')
fmt='%.2f%%'
yticks = mtick.FormatStrFormatter(fmt)
ax2.yaxis.set_major_formatter(yticks)
plt.xticks(x,genre_df,fontsize=12,rotation=60)
plt.yticks(fontsize=15)
ax2.set_ylabel('Profit_rate',fontsize=18)
ax2.legend(loc=1,fontsize=15)
plt.grid(False)

#保存图片
fig.savefig('profit by genres.png')

#问题3：比较Universal Pictures与Paramount Pictures两家巨头公司的业绩
#创建公司数据框

company_list = ['Universal Pictures', 'Paramount Pictures']
company_df = pd.DataFrame()

for company in company_list:

    company_df[company]=full['production_companies'].str.contains(company).map(lambda x:1 if x else 0)
company_df = pd.concat([company_df,genre_df.iloc[:,:-1],full['revenue']],axis=1)

#创建巨头对比数据框

Uni_vs_Para = pd.DataFrame(index=['Universal Pictures', 'Paramount Pictures'],
                           columns=company_df.columns[2:])

#计算两家公司各自收益总额

Uni_vs_Para.loc['Universal Pictures']=company_df.groupby('Universal Pictures',
               as_index=False).sum().iloc[1,2:]

Uni_vs_Para.loc['Paramount Pictures']=company_df.groupby('Paramount Pictures',
               as_index=False).sum().iloc[1,2:]

#可视化两公司票房收入对比


fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
Uni_vs_Para['revenue'].plot(ax=ax,kind='bar')
plt.xticks(rotation=0)
plt.title('Universal VS. Paramount')
plt.ylabel('Revenue')
fig.savefig('Universal vs Paramount by revenue.png')

#"""Universal Pictrues总票房收入高于Paramount Pictures"""
Uni_vs_Para = Uni_vs_Para.T

#分解两公司数据框

universal = Uni_vs_Para['Universal Pictures'].iloc[:-1]
paramount = Uni_vs_Para['Paramount Pictures'].iloc[:-1]

#将universal数量排名9之后的加和，命名为others

universal['others']=universal.sort_values(ascending=False).iloc[8:].sum()
universal = universal.sort_values(ascending=True).iloc[-9:]

#将paramount数量排名9之后的加和，命名为others

paramount['others']=paramount.sort_values(ascending=False).iloc[8:].sum()
paramount = paramount.sort_values(ascending=True).iloc[-9:]

#可视化两公司电影风格数量占比

fig = plt.figure(figsize=(13,6))
ax1 = plt.subplot(1,2,1)
ax1 = plt.pie(universal, labels=universal.index, autopct='%.2f%%',startangle=90,pctdistance=0.75)
plt.title('Universal Pictures',fontsize=15)
 

ax2 = plt.subplot(1,2,2)
ax2 = plt.pie(paramount, labels=paramount.index, autopct='%.2f%%',startangle=90,pctdistance=0.75)
plt.title('Paramount Pictures',fontsize=15)

fig.savefig('Company Picture.png')
#问题4：看看票房与哪些因素有关
#计算相关系数矩阵

aa=full[['runtime','popularity','vote_average',
      'vote_count','budget','revenue']].corr()
print(aa[u'revenue'])
'''
受欢迎度和票房相关性：0.64
评价次数和票房相关性：0.78
电影预算和票房相关性：0.73
平均评分和票房相关性：0.20
电影时常和票房相关性：0.25

创建票房收入数据框
'''
revenue = full[['popularity','vote_count','budget','revenue']]

#可视化票房收入分别与受欢迎度（蓝）、评价次数（绿）、电影预算（红）的相关性散点图，并配线性回归线。


fig = plt.figure(figsize=(8,6))

ax1 = plt.subplot(3,1,1)
ax1 = sns.regplot(x='popularity', y='revenue', data=revenue, x_jitter=.1)
ax1.text(400,2e9,'r=0.64',fontsize=15)
plt.title('revenue by popularity',fontsize=15)
plt.xlabel('popularity',fontsize=13)
plt.ylabel('revenue',fontsize=13)

ax2 = plt.subplot(3,1,2)
ax2 = sns.regplot(x='vote_count', y='revenue', data=revenue, x_jitter=.1,color='g',marker='+')
ax2.text(6800,1.1e9,'r=0.78',fontsize=15)
plt.title('revenue by vote_count',fontsize=15)
plt.xlabel('vote_count',fontsize=13)
plt.ylabel('revenue',fontsize=13)


ax3 = plt.subplot(3,1,3)
ax3 = sns.regplot(x='budget', y='revenue', data=revenue, x_jitter=.1,color='r',marker='^')
ax3.text(1.6e8,2.2e9,'r=0.73',fontsize=15)
plt.title('revenue by budget',fontsize=15)
plt.xlabel('budget',fontsize=13)
plt.ylabel('revenue',fontsize=13)

fig.savefig('revenue.png')

#电影评次与票房收入最相关（绿色），电影预算与票房收入高度相关（红色），
#受欢迎度与评次高度相关，因此与票房收入相关性较高。

#建议：增加电影预算 用于电影本身、多用于渠道宣传
from wordcloud import WordCloud
def decode(x):
    z=[]
    for i in x:
        z.append(i['name'])
    return '|'.join(z)

#利用电影关键字制作词云图
#对keywords列数据处理
movies['keywords']=movies['keywords'].apply(json.loads)
#调用自定义函数decode处理keywords列数据
movies['keywords']=movies['keywords'].apply(decode)
movies['keywords'].tail()
#建立keywordlist列表
keyword_list=[]
for i in movies['keywords']:
    keyword_list.append(i)
    keyword_list=list(keyword_list)
    keyword_list
#把字符串列表连接成一个长字符串
lis=' '.join(keyword_list)
lis.replace('\'s',' ') 
wc=WordCloud(background_color='white',#设置背景颜色
            max_words=1000,#设置最大词数
            max_font_size=100,#字体最大值
            random_state=12#设置一个随机种子，用于随机着色
            )
#根据字符串生成词云
wc.generate(lis)
plt.figure(figsize=(16,8))
#显示图片
plt.imshow(wc)
plt.axis('off')
plt.savefig("keywords.png")


