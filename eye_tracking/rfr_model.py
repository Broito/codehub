# %%
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.metrics import mean_squared_error,r2_score
from sklearn.model_selection import train_test_split, GridSearchCV,cross_val_score,KFold
from sklearn.svm import SVR
from sklearn.metrics import classification_report
from matplotlib.font_manager import FontProperties
from treeinterpreter import treeinterpreter as ti
from sklearn.metrics import confusion_matrix    #混淆矩阵模块
from sklearn.metrics import classification_report#准确率及召回率等Report模块
from sklearn.preprocessing import OneHotEncoder,LabelEncoder

# %%
os.chdir(r'E:\workspace\Thesis_2022_walkability_eye_tracking\analysis_part')
df = pd.read_excel('答案总表_v67_眼动语义汇总_回归版_像元统计_注视次数.xlsx','Sheet1')
df = df.reset_index()

# %%独热编码
oenc=OneHotEncoder(sparse=False)
lenc=LabelEncoder()
store1=pd.DataFrame({'condition_addi':['blank', 'noise_low', 'sign_pedes', 'noise_high', 'hint_school',
       'hint_hospital', 'hint_commercal', 'hint_park', 'hint_residential']})
store2=pd.DataFrame({'condition_aim':['commute', 'Leisure', 'shopping']})
store3= pd.DataFrame({'gender':['male', 'female']})
dummy_addi = pd.get_dummies(store1['condition_addi'],prefix='addi')
dummy_aim = pd.get_dummies(store2['condition_aim'],prefix='aim')
dummy_gender = pd.get_dummies(store3['gender'],prefix='gender')
df_addi = pd.concat([store1,dummy_addi],axis = 1)
df_aim = pd.concat([store2,dummy_aim],axis = 1)
df_gender = pd.concat([store3,dummy_gender],axis = 1)
df_addi.index = df_addi['condition_addi']
df_aim.index = df_aim['condition_aim']
df_gender.index = df_gender['gender']

df2 = df.join(df_addi,on='condition_addi', lsuffix='_left', rsuffix='_right')
df3 = df2.join(df_aim,on='condition_aim', lsuffix='_left', rsuffix='_right')
df_complete = df3.join(df_gender,on='gender', lsuffix='_left', rsuffix='_right')

y_names = ['safety_car','safety_bicycle','safety_self','comfort','attract_walk','attract_run','attract_dog']
def reclassfy(a):
       if a <= 2 and not np.isnan(a):
              return 0
       elif a >= 4 and not np.isnan(a):
              return 1
       else:
              return np.nan
for y_name in y_names:
       df_complete[f'{y_name}_binary'] = df_complete[f'{y_name}'].apply(reclassfy)

# %% 基础指标版
'''
带上了熟悉感，到时候再来一版对熟悉感的预测
'''
'''
# df_complete.dropna(axis = 0, subset=['Total_amplitude_of_saccades','safety_car'],inplace= True)

# X = df_complete.loc[:,['bicycle_time', 'exercise_time',
# 'run_time', 'walking_time',
# 'gender_female', 'gender_male',
# 'addi_blank', 'addi_hint_commercal',
#        'addi_hint_hospital', 'addi_hint_park', 'addi_hint_residential',
#        'addi_hint_school', 'addi_noise_high', 'addi_noise_low',
#        'addi_sign_pedes',
# 'aim_Leisure', 'aim_commute','aim_shopping',
# 'familiarity',
# 'pupil_avg','Total_duration_of_whole_fixations',
#        'Average_duration_of_whole_fixations', 'Number_of_whole_fixations',
#        'Duration_of_first_whole_fixation',
#        'Average_whole-fixation_pupil_diameter', 'Number_of_saccades',
#        'Average_peak_velocity_of_saccades',
#        'Minimum_peak_velocity_of_saccades',
#        'Maximum_peak_velocity_of_saccades',
#        'Standard_deviation_of_peak_velocity_of_saccades',
#        'Average_amplitude_of_saccades', 'Minimum_amplitude_of_saccades',
#        'Maximum_amplitude_of_saccades', 'Total_amplitude_of_saccades'
# ]]
# X = X.fillna(0)
# y = df_complete['attract_walk']

# rfr = RandomForestRegressor(n_estimators=1000, n_jobs=-1, oob_score=True)
# rfr.fit(X,y)

# print(f'oob score: {rfr.oob_score_}')
# feat_labels = X.columns
# importances = rfr.feature_importances_
# indices = np.argsort(importances)[::-1]
# for i in range(X.shape[1]):
#     print ("(%2d) %-*s %f" % (i + 1, 30,feat_labels[indices[i]], importances[indices[i]]))
# '''

# # %% 眼动指标版
# '''
# 带上了熟悉感，到时候再来一版对熟悉感的预测
# '''

# df_complete.dropna(axis = 0, subset=['attract_dog'],inplace= True)

# X = df_complete.loc[:,['bicycle_time', 'exercise_time',
# 'run_time', 'walking_time',
# 'gender_female', 'gender_male',
# 'addi_blank', 'addi_hint_commercal',
#        'addi_hint_hospital', 'addi_hint_park', 'addi_hint_residential',
#        'addi_hint_school', 'addi_noise_high', 'addi_noise_low',
#        'addi_sign_pedes',
# 'aim_Leisure', 'aim_commute','aim_shopping',
# 'familiarity',
# 'pupil_avg','building', 'fence', 'person', 'road', 'sidewalk',
#        'vegetation', 'bicycle', 'motorcycle', 'car', 'wall', 'traffic sign',
#        'sky'
# ]]
# X = X.fillna(0)
# y = df_complete['attract_dog']

# rfr = RandomForestRegressor(n_estimators=100, n_jobs=-1, oob_score=True)
# rfr.fit(X,y)

# print(f'oob score: {rfr.oob_score_}')
# feat_labels = X.columns
# importances = rfr.feature_importances_
# indices = np.argsort(importances)[::-1]
# for i in range(X.shape[1]):
#     print ("(%2d) %-*s %f" % (i + 1, 30,feat_labels[indices[i]], importances[indices[i]]))


# %% 语义分割指标版
'''
带上了熟悉感，到时候再来一版对熟悉感的预测
'''
# y_names = ['safety_car','safety_bicycle','safety_self','comfort','attract_walk','attract_run','attract_dog']
# for y_name in y_names:
#        df_complete.dropna(axis = 0, subset=[y_name],inplace= True)

#        X = df_complete.loc[:,['bicycle_time', 'exercise_time',
#        'run_time', 'walking_time',
#        'gender_female', 'gender_male',
#        'familiarity',
#        'pupil_avg',
       
#        # 'building_px', 'fence_px', 'person_px', 'road_px', 'sidewalk_px',
#        #        'vegetation_px', 'bicycle_px', 'motorcycle_px', 'car_px', 'wall_px',
#        #        'traffic sign_px', 'sky_px', 
#        # 
#        'building_t_px', 'fence_t_px',
#               'person_t_px', 'road_t_px', 'sidewalk_t_px', 'vegetation_t_px',
#               'bicycle_t_px', 'motorcycle_t_px', 'car_t_px', 'wall_t_px',
#               'traffic sign_t_px', 'sky_t_px',
       
#        'fc_road',
#        'fc_sidewalk', 'fc_building', 'fc_wall', 'fc_fence', 'fc_traffic sign',
#        'fc_vegetation', 'fc_sky', 'fc_person', 'fc_car', 'fc_motorcycle',
#        'fc_bicycle',

#        '1st_road', '1st_sidewalk', '1st_building', '1st_wall',
#        '1st_fence', '1st_traffic sign', '1st_vegetation', '1st_sky',
#        '1st_person', '1st_car', '1st_motorcycle', '1st_bicycle'
              
#        #        'building', 'fence', 'person', 'road', 'sidewalk',
#        # 'vegetation', 'bicycle', 'motorcycle', 'car', 'wall', 'traffic sign',
#        # 'sky'
#        ]]
#        X = X.fillna(0)
#        y = df_complete[y_name]

#        rfr = RandomForestRegressor(n_estimators=100, n_jobs=-1, oob_score=True)
#        rfr.fit(X,y)

#        print(f'{y_name} oob score: {rfr.oob_score_}')
#        feat_labels = X.columns
#        importances = rfr.feature_importances_
#        indices = np.argsort(importances)[::-1]
#        for i in range(X.shape[1]):
#               print ("(%2d) %-*s %f" % (i + 1, 30,feat_labels[indices[i]], importances[indices[i]]))


# %% 二分类预测

y_names = ['safety_car','safety_bicycle','safety_self','comfort','attract_walk','attract_run','attract_dog']
y_names_binary = [i+'_binary' for i in y_names]
for y_name in y_names_binary:
       df_temp = df_complete.dropna(axis = 0, subset=[y_name])

       print(df_temp.shape)
       X = df_temp.loc[:,['bicycle_time', 'exercise_time',
       'run_time', 'walking_time',
       'gender_female', 'gender_male',

       'familiarity',
       'pupil_avg',

              'building', 'fence', 'person', 'road', 'sidewalk',
       'vegetation', 'bicycle', 'motorcycle', 'car', 'wall', 'traffic sign',
       'sky',

#       'building_t_px', 'fence_t_px',
#               'person_t_px', 'road_t_px', 'sidewalk_t_px', 'vegetation_t_px',
#               'bicycle_t_px', 'motorcycle_t_px', 'car_t_px', 'wall_t_px',
#               'traffic sign_t_px', 'sky_t_px',
       
       'fc_road',
       'fc_sidewalk', 'fc_building', 'fc_wall', 'fc_fence', 'fc_traffic sign',
       'fc_vegetation', 'fc_sky', 'fc_person', 'fc_car', 'fc_motorcycle',
       'fc_bicycle',

       'building_px', 'fence_px', 'person_px', 'road_px', 'sidewalk_px',
              'vegetation_px', 'bicycle_px', 'motorcycle_px', 'car_px', 'wall_px',
              'traffic sign_px', 'sky_px', 

       # '1st_road', '1st_sidewalk', '1st_building', '1st_wall',
       # '1st_fence', '1st_traffic sign', '1st_vegetation', '1st_sky',
       # '1st_person', '1st_car', '1st_motorcycle', '1st_bicycle'
       ]]
       X = X.fillna(0)
       y = df_temp[y_name]

       rfc = RandomForestClassifier(n_estimators=100, n_jobs=-1, oob_score=True)
       rfc.fit(X,y)

       print(f'{y_name} oob score: {rfc.oob_score_}')
       # feat_labels = X.columns
       # importances = rfc.feature_importances_
       # indices = np.argsort(importances)[::-1]
       # for i in range(X.shape[1]):
       #        print ("(%2d) %-*s %f" % (i + 1, 30,feat_labels[indices[i]], importances[indices[i]]))




# %%
