# %%
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt 
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
import os
from treeinterpreter import treeinterpreter as ti

os.chdir(r'E:\workspace\Research_2021_weather_collision\data_processing')
df = pd.read_excel('total_upper_tata_20220418.xls','Sheet1') 
# df = df[df.loc[:,'road_binary_type']=='branch road']
# df = df[df.loc[:,'road_binary_type']=='upper-level road']

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
y = df['density_pedestrain']

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
prediction, bias, contributions = ti.predict(rfr, X)
# %%
contri_df = pd.DataFrame(contributions,columns= list(map(lambda a: 'c_' + a, feature_cols)))
df_contri = pd.concat([df[['roadid_sim']],contri_df],axis=1)

df_contri.to_csv(r'E:\workspace\Research_2021_weather_collision\data_processing\tree_interpreter_result\pedes_upper_result.csv', index=False)

# %%
def draw_line(df,field_x,field_y):
    df2 = df.sort_values(by = field_x)
    x = df2[field_x]
    y = df2[field_y]
    plt.plot(x,y)
    plt.xlabel(field_x)
    plt.ylabel(field_y)
    plt.show()

def scatter_yx(df,field_x,field_y):
    df2 = df.sort_values(by = field_x)
    x = df2[field_x]
    y = df2[field_y]
    plt.scatter(y,x)
    plt.xlabel(field_y)
    plt.ylabel(field_x)
    plt.show()


lst_field_y = ['density_pedestrain','density_vehicle']
df_draw = pd.concat([df,contri_df],axis=1)
for field_y in lst_field_y:
    for field_x in list(map(lambda a: 'c_' + a, feature_cols)):
        scatter_yx(df_draw,field_x,field_y)
