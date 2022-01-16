import os
import pandas as pd

os.chdir(r'E:\workspace\Research_2021_7thCencus_AgingPeople\data_processing\七普_沪苏浙粤_区镇预测人口结构')
# df = pd.read_csv('六普区县_矢量导出.csv')
# df['old_ratio'] = df['SUM_F65岁']/df['SUM_总人口']

df_city = pd.read_csv('六普地级市_矢量导出.csv')
df_city['old_ratio_city'] = df_city['SUM_SUM_F6']/df_city['SUM_SUM_总']

# # 计算各区县六普的相对老龄化差异
# df = df.set_index("FIRST_SHI").join(df_city.loc[:,['FIRST_SHI','old_ratio_city']].set_index("FIRST_SHI"),on = 'FIRST_SHI',how = 'left')
# df['residual'] = df['old_ratio'] - df['old_ratio_city']

# # 上海的手动处理吧，就差长宁区和黄浦区的了
# df = df[df['FIRST_NA_2'].isin(['江苏省','浙江省','广东省'])]

# df_7th_city = pd.read_excel('七普_沪苏浙粤_区镇预测人口结构.xlsx','地级市')
# df_7th_county = pd.read_excel('七普_沪苏浙粤_区镇预测人口结构.xlsx','区县')
# df_7th_county = df_7th_county[df_7th_county['省级'].isin(['江苏省','浙江省','广东省'])]

# df_7th_city = df_7th_city.loc[:,['prefcode','公报名称','常住人口','#65岁及以上占比']]
# df_7th_city['#65岁及以上占比'] = df_7th_city['#65岁及以上占比']/100


# df = df.join(df_7th_city.set_index("prefcode"),how = 'left') # join 7普地级市老龄化率
# df2 = df.set_index("XIAN").join(df_7th_county.loc[:,['codeF7','七普人口']].set_index("codeF7"),how = 'left')

df = pd.read_csv('【正式使用】改制_沪苏浙粤区镇人口预测.csv',encoding = 'GB18030')
# df_7th_county = pd.read_excel('七普_沪苏浙粤_区镇预测人口结构.xlsx','区县')
# df_7th_county = df_7th_county[df_7th_county['省级'].isin(['江苏省','浙江省','广东省'])]
# df2 = df.set_index("FIRST_XIAN").join(df_7th_county.loc[:,['codeF7','七普人口']].set_index("codeF7"),how = 'left')

df['FIRST_SHI'] = df['FIRST_XIAN'].map(lambda a: int(str(a)[:4]))
del df['old_ratio_city']
del df['residual']
del df['city_name']
del df['pred_old_ratio']
df = df.set_index("FIRST_SHI").join(df_city.loc[:,['FIRST_SHI','old_ratio_city']].set_index("FIRST_SHI"),on = 'FIRST_SHI',how = 'left')

df['6th_residual'] = df['old_ratio'] - df['old_ratio_city']
df['pred_7th_old_ratio'] = df['7th_up65_city'] + df['6th_residual']
df['pred_7th_old_pop'] = df['7th_county_pop']*df['pred_7th_old_ratio']






