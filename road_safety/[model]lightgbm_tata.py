# %%
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
X = df.loc[:,feature_cols]
y = df.loc[:,'density_vehicle'] #9-10

# from sklearn.model_selection import train_test_split  #这里是引用了交叉验证
# X_train,X_test, y_train, y_test = train_test_split(X, y)
# print (X_train.shape)
# print (y_train.shape)
# print (X_test.shape)
# print (y_test.shape)
scores = []
kf=KFold(n_splits=10,shuffle=True)
for train_index, test_index in kf.split(X):
    # print("TRAIN:", train_index, "TEST:", test_index)
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    # 训练模型
    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_test = lgb.Dataset(X_test, y_test, reference=lgb_train)

    params = {
        'num_leaves': 10,
        'learning_rate': 0.1,
        'metric': ['l1', 'l2'],
        'feature_fraction': 0.9, # 建树的特征选择比例
        'bagging_fraction': 0.8, # 建树的样本采样比例
        'bagging_freq': 5,  # k 意味着每 k 次迭代执行bagging
        'verbose': -1
    }

    evals_result = {}  # to record eval results for plotting
    gbm = lgb.train(params,
                    lgb_train,
                    num_boost_round=100,
                    valid_sets=[lgb_train, lgb_test],
                    feature_name=[feature_cols[i] for i in range(X_train.shape[-1])],
                    categorical_feature=['sidewalk_type'],
                    evals_result=evals_result,
                    verbose_eval=10)
    gbm.save_model('Regressionmodel.txt')
    y_pred_test = gbm.predict(X_test, num_iteration=gbm.best_iteration)
    # y_pred_train = gbm.predict(X_train, num_iteration=gbm.best_iteration)
    scores.append(r2_score(y_test,y_pred_test))

    # print("训练集合上R^2 = {:.3f}".format(r2_score(y_train, y_pred_train)))
    # print("测试集合上R^2 = {:.3f} ".format(r2_score(y_test,y_pred_test)))

print(f'10折交叉验证得分为：{np.mean(scores)}')
print(scores)
# # %% 绘图表示结果
def render_plot_importance(max_features=20,ignore_zero=True, precision=3):
    ax = lgb.plot_importance(gbm, importance_type='gain',
                             max_num_features=max_features,
                             ignore_zero=ignore_zero, figsize=(12, 8),
                             precision=precision)
    plt.show()












