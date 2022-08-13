import pandas as pd
import os

os.chdir(r"C:\Users\NingchengWang\Desktop")
df = pd.read_excel(r'243000033城中城账户修改.xls','证件类型有误')
df_2 = pd.read_excel(r'243000033-城中城支行客户信息治理清单（编号001）整改月报.xls','2、证件类型不规范台账管理')

id_2 = list(df_2['证件号码'].astype('str'))
df['比对结果'] = df['证件号码'].apply(lambda a:1 if a in id_2 else 0)

































