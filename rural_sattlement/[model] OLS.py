# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import statsmodels.api as sm
from sklearn.preprocessing import OneHotEncoder
import geopandas as gpd


df = gpd.read_file(r"E:\workspace\Research_2022_rural_settlement\work_space\村落验证一张表\村落验证一张表\rural_settlement_total_point_v5.shp")


# %% 独热编码
enc = OneHotEncoder(handle_unknown='ignore')
enc.fit(df[['ur_code','urbanagg']].values)
# matrix里记录了独热编码值，labels里记录了field
matrix = enc.transform(df[['ur_code','urbanagg']].values).toarray()
feature_labels = list(np.array(enc.categories_).ravel())
# 把转换好的 Encoding 变成 DataFrame
col_names = []
for field,field_name in zip(feature_labels,['ur_code','urbanagg']):
  for suffix in field:
    col_names.append("{}_{}".format(field_name, suffix))
ohe_df = pd.DataFrame(data = matrix, columns=col_names, dtype=int)  
# 拼接至原始df里面
df = pd.concat([df,ohe_df],axis=1)


# %% 选择特征
feature_cols = ['dem','RANGE','aggregate']+col_names
X = df.loc[:,feature_cols]
y = df['F_glc30']

# 运行logit模型
lgt = sm.OLS(y,X).fit()
print(lgt.summary())


# %%
