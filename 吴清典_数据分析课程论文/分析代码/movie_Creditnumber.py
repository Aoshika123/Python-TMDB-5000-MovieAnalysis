# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 17:51:47 2019

@author: 吴清典
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


movies = pd.read_csv('tmdb_5000_movies.csv')

creditsss = pd.read_csv('tmdb_5000_credits.csv')

movies_credits = movies.merge(creditsss, left_on = 'id', right_on = 'movie_id', how = 'left')
#movies_credits = pd.merge(movies, creditsss, left_on='id', right_on='movie_id', how='left') 
movies_credits.genres[0]
import json
json_columns = ['genres', 'keywords', 'production_companies', 'production_countries', 'cast', 'crew']
for column in json_columns:
    movies_credits[column] = movies_credits[column].apply(json.loads)
def extractName(column):
    col = [[di['name'] for di in row] for row in column]
    return col
ex_name = ['genres', 'production_companies', 'production_countries']
for column in ex_name:
    movies_credits[column] = extractName(movies_credits[column])
movies_credits['actors'] = [[di['name'] for di in row[0:4]] for row in movies_credits['cast']]    #演员只取前4位
movies_credits['keywords'] = [[di['name'] for di in row[0:10]] for row in movies_credits['keywords']]    #关键词只取前10个

def extractDirector(crew, job):
    name = ''
    for di in crew:
        if di['job'] == job:
            name = di['name']
            break 
        else:
            pass
    return name
movies_credits['director'] = [extractDirector(crew, 'Director') for crew in movies_credits.crew]
movies_credits['writer'] = [extractDirector(crew, 'Writer') for crew in movies_credits.crew]
movies_credits['producer'] = [extractDirector(crew, 'producer') for crew in movies_credits.crew]

movies_credits['year'] = pd.to_datetime(movies_credits['release_date']).apply(lambda x: x.year)

movies = movies_credits[['title_x', 'genres', 'keywords', 'director', 'actors', 'writer', 'producer', 'budget', 'revenue', 'popularity', 'vote_average', 'vote_count', 'production_companies', 'production_countries', 'year']].dropna()
movies.rename(columns={'title_x': 'title'}, inplace = True)
movies.year = movies.year.astype(int)
movies.describe()
movies[movies.year >= 2000].groupby('year').size().plot(kind = 'bar')
movies_15 = movies[(movies.year >= 2000) & (movies.year < 2016) & (movies.vote_count > 40) &(movies.budget * movies.revenue * movies.popularity * movies.vote_average !=0)].reset_index(drop = 'True')

def countN(column):
    count = dict()
    for row in column:
        for ele in row:
            if ele in count:
                count[ele] += 1
            else:
                count[ele] = 1
    return count

def binary(wordlist0, wordlist):
    binary = []
    for word in wordlist0.index:
        if word in wordlist:
            binary.append(1)
        else:
            binary.append(0)
    return binary

genres = pd.Series(countN(movies_15.genres)).sort_values()

movies_15['genres_bin'] = [binary(genres, x) for x in movies_15.genres]    #影片类型的二元数组
directors = movies_15.groupby('director').size().sort_values(ascending=False)
movies_15['director_bin'] = [binary(directors, x) for x in movies_15.director]    #影片导演的二元数组
actors = pd.Series(countN(movies_15.actors)).sort_values(ascending=False)
movies_15['actors_bin'] = [binary(actors, x) for x in movies_15.actors]    #影片主演的二元数组

from scipy import spatial
def angle(movie1, movie2):
    dis_tot = 0
    iterlist = [[movie1.genres_bin, movie2.genres_bin],
                [movie1.director_bin, movie2.director_bin],
                [movie1.actors_bin, movie2.actors_bin]]                
    for b1, b2 in iterlist:
        if (1 not in b1) or (1 not in b2):
            dis = 1
        else:
            dis = spatial.distance.cosine(b1, b2)
        dis_tot += dis
    return dis_tot

def predictor(new_movie):
    movie_bin = pd.Series()
    movie_bin['genres_bin'] = binary(genres, new_movie['genres'])
    movie_bin['director_bin'] = binary(directors, new_movie['director'])
    movie_bin['actors_bin'] = binary(actors, new_movie['actors'])
    vote = movies_15.copy()
    vote['angle'] = [angle(vote.iloc[i], movie_bin) for i in range(len(vote))]
    vote = vote.sort_values('angle')
    vote_avg = np.mean(vote.vote_average[0:5])
    return vote_avg


The_Fate_of_the_Furious  = {'genres': ['Action', 'Thriller', 'Adventure'], 
                    'director': ['F. Gary Gray'], 'actors': 
                    ['Vin Diesel', 'Jason Statham', 'Dwayne Johnson', 'Michelle Rodriguez', 'Tyrese Gibson']}
print('速度与激情8（The_Fate_of_the_Furious）的预测分数是：',predictor(The_Fate_of_the_Furious))