# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import statsmodels.api as sm
from sklearn.preprocessing import OneHotEncoder

df = pd.read_csv(r"E:\workspace\Research_2022_rural_settlement\work_space\partial_processing\result_one\china_settlement_2y.csv")

df['GAIA'] = df['GAIA'].apply(lambda a: 1 if a > 10000 else 0 )
df['GLB30'] = df['GLB30'].apply(lambda a: 1 if a > 10000 else 0 )
df['urbanagg'] = df['urbanagg'].apply(lambda a: 'non_agg' if a == ' ' else a)
df.rename(columns={'�����.1':'ur_code'},inplace=True)
df['urbanagg'] = df['urbanagg'].astype('category')
df['ur_code'] = df['ur_code'].astype('category')

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

# 选择特征
feature_cols = ['dem','RANGE','aggregate']+col_names
X = df.loc[:,feature_cols]
y = df['GAIA']

# %% 运行logit模型
lgt = sm.Logit(y,X).fit()
print(lgt.summary())








































# %%
