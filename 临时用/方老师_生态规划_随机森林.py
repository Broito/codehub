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

os.chdir(r'E:\workspace\Help_2022_方老师')
df = pd.read_excel(r'村镇类型判断表.xlsx','Sheet1')
df_train = df.iloc[:200,:] 
df_pred = df.iloc[200:,:]

X_train = df_train[['旱地', '水田及水域用地', '工业仓储用地', '公共服务与管理用地', '水浇地', '林园地', '其他用地类型面积']]
y_train = df_train[['村镇类型']]

X_last_pred = df_pred[['旱地', '水田及水域用地', '工业仓储用地', '公共服务与管理用地', '水浇地', '林园地', '其他用地类型面积']]
y_last = df_pred[['村镇类型']]

rfc = RandomForestClassifier(random_state=3, n_estimators=100, n_jobs=-1)
rfc.fit(X_train,y_train)

y_pred_train = rfc.predict(X_train)
y_last_pred = rfc.predict(X_last_pred)

print("训练集的混淆矩阵\n",confusion_matrix(y_train,y_pred_train))#训练集上的混淆矩阵
print("测试集的混淆矩阵\n",confusion_matrix(y_last,y_last_pred) )#测试集上的混淆矩阵
print(classification_report(y_last,y_last_pred) )

y_pred = list(y_pred_train)+list(y_last_pred)

df['rfc_pred'] = y_pred

# df.to_excel(r'村镇类型判断表_随机森林输出.xlsx')

feat_labels = X_train.columns
importances = rfc.feature_importances_
indices = np.argsort(importances)[::-1]
for i in range(X_train.shape[1]):
    print ("(%2d) %-*s %f" % (i + 1, 30,feat_labels[indices[i]], importances[indices[i]]))

































































