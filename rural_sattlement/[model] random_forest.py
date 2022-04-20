# %%
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt 
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
import os

os.chdir(r'E:\workspace\Research_2021_weather_collision\data_processing')
df = pd.read_excel('total_upper_tata_20220418.xls','Sheet1') 
# df = df[df.loc[:,'road_binary_type']=='branch road']
df = df[df.loc[:,'road_binary_type']=='upper-level road']

feature_cols=['Shape_Length','Avg_carNumAll','Avg_landuse_green','num_junction','num_hospital','npp_500_mean','tree_area','avg_height',
              'non_motor_arti','num_sign','sum_pop','landuse_commercial','num_subbus','num_school','CompassA','Sum_zebra',
'Avg_price','prop_old_65','prop_children_0_14','num_clinic','num_store']

# %% 独热编码
enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(df[['sidewalk_type']].values)
# matrix里记录了独热编码值，labels里记录了field
matrix = enc.transform(df[['sidewalk_type']].values).toarray()
feature_labels = list(np.array(enc.categories_).ravel())
# 把转换好的 Encoding 变成 DataFrame
col_names = []
for suffix in feature_labels:
  col_names.append("{}_{}".format('sidewalk_', suffix))
ohe_df = pd.DataFrame(data = matrix, columns=col_names, dtype=int)  
# 拼接至原始df里面
df = pd.concat([df,ohe_df],axis=1)

# %%  选择特征
feature_cols = feature_cols+col_names
X = df.loc[:,feature_cols]
y = df['density_vehicle']

# %% 构建模型
rfr = RandomForestRegressor(n_estimators=1500, n_jobs=-1,oob_score = True)
rfr.fit(X,y)
oob = rfr.oob_score_

print(f"oob_score:{oob}")

feat_labels = X.columns
importances = rfr.feature_importances_
indices = np.argsort(importances)[::-1]
for i in range(X.shape[1]):
    print ("(%2d) %-*s %f" % (i + 1, 30,feat_labels[indices[i]], importances[indices[i]]))










# %%
