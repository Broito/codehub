import os
import pandas as pd
import numpy as np
import math

def if_contain(x,y):
    minus = y.map(lambda a: abs(a-x))
    if True in list(minus<0.0000001):
        return True
    else:
        return False

os.chdir(r'E:\\workspace\\Research_2021_7thCencus_AgingPeople\\data_processing\\长三角官方养老院数据\\江苏养老机构')
df = pd.read_csv('江苏养老机构2017(带坐标).csv',encoding = 'GB18030')
df_ylw =  pd.read_excel(r"E:\workspace\Research_2021_7thCencus_AgingPeople\data_processing\aging_faculties\china_aging_faculties.xls","Sheet1")
df_ylw = df_ylw[df_ylw['province']=='江苏省']

x_df = df['lng']
y_df = df['lat']
df_ylw_notin = df_ylw[~(df_ylw['lon_wgs84'].apply(if_contain,y = x_df) | df_ylw['lat_wgs84'].apply(if_contain,y = x_df ))]

df_ylw_notin.to_csv('养老网增补.csv',encoding = 'GB18030')





































