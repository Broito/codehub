import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt 
# from sklearn.preprocessing import OneHotEncoder

df = pd.read_csv(r"E:\workspace\Research_2022_rural_settlement\work_space\partial_processing\result_one\china_settlement_2y.csv")

df['GAIA'] = df['GAIA'].apply(lambda a: 1 if a > 10000 else 0 )
df['GLB30'] = df['GLB30'].apply(lambda a: 1 if a > 10000 else 0 )
df['urbanagg'] = df['urbanagg'].apply(lambda a: 'non_agg' if a == ' ' else a)
df.rename(columns={'�����.1':'ur_code'},inplace=True)
df['urbanagg'] = df['urbanagg'].astype('category')
df['ur_code'] = df['ur_code'].astype('category')

# %%  选择特征
# enc = OneHotEncoder(handle_unknown='ignore')
feature_cols = ['ur_code','dem','RANGE','aggregate','urbanagg']
X = df.loc[:,feature_cols]
y = df['GAIA']

# %% 划分数据集
from sklearn.model_selection import train_test_split  #这里是引用了交叉验证
X_train,X_test, y_train, y_test = train_test_split(X, y, random_state=1)
print (X_train.shape)
print (y_train.shape)
print (X_test.shape)
print (y_test.shape)

# %% 训练模型
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
                categorical_feature=['ur_code','urbanagg'],
                evals_result=evals_result,
                verbose_eval=10)
gbm.save_model('Regressionmodel.txt')
y_pred_test = gbm.predict(X_test, num_iteration=gbm.best_iteration)
y_pred_train = gbm.predict(X_train, num_iteration=gbm.best_iteration)


print("训练集合上R^2 = {:.3f}".format(r2_score(y_train, y_pred_train)))
print("测试集合上R^2 = {:.3f} ".format(r2_score(y_test,y_pred_test)))

# %% 绘图表示结果
def render_plot_importance(max_features=10,ignore_zero=True, precision=3):
    ax = lgb.plot_importance(gbm, importance_type='gain',
                             max_num_features=max_features,
                             ignore_zero=ignore_zero, figsize=(12, 8),
                             precision=precision)
    plt.show()









































# %%
