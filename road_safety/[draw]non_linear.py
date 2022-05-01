import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt 
import os
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

os.chdir(r'E:\workspace\Research_2021_weather_collision\data_processing')
df = pd.read_excel('total_upper_tata_20220418.xls','Sheet1') 
df = df[df.loc[:,'road_binary_type']=='upper-level road']
df['pop24'] = df['pop_6_18'] + df['pop_18_6']
feature_cols=['Shape_Length','Avg_carNumAll','Avg_landuse_green','num_junction','num_hospital','npp_500_mean','tree_area','avg_height',
              'non_motor_arti','num_sign','sum_pop','landuse_commercial','num_subbus','num_school','CompassA','sidewalk_type','Sum_zebra',
'Avg_price','prop_old_65','prop_children_0_14','num_clinic','num_store']
# X = df.loc[:,feature_cols]
# y = df.loc[:,'density_vehicle'] #9-10

def draw_line(field_x,field_y):
    df2 = df.sort_values(by = field_x)
    x = df2[field_x]
    y = df2[field_y]
    plt.plot(x,y)
    plt.xlabel(field_x)
    plt.ylabel(field_y)
    plt.show()

def scatter(field_x,field_y):
    df2 = df.sort_values(by = field_x)
    x = df2[field_x]
    y = df2[field_y]
    plt.scatter(x,y)
    plt.xlabel(field_x)
    plt.ylabel(field_y)
    plt.show()

lst_y = ['density_pedestrain','density_vehicle']
# lst_y = ['pedes_collision']
for field_y in lst_y:
    for field_x in feature_cols:
        # draw_line(field_x,field_y)
        scatter(field_x,field_y)




















