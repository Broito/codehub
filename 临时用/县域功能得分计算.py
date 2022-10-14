# %%
import numpy as np
import geopandas as gpd
import os
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform

os.chdir(r'E:\workspace\Help_2022_彭荣熙\221012 to wnc')

df_county = gpd.read_file('山东县界.shp')
df_village = gpd.read_file('221012打分评价版.shp')
function_fields = ['生产功','生活功','生态功']

# 计算字段对应的5个值
def calc_5value(county_code,field_name):

    villages = df_village[df_village['区县代'] == county_code]

    # 以生产功能为例
    ability_field = field_name
    ability_list = villages[ability_field].values
    ability_list.sort() # 从小到大排序，不返回值，修改原数组
    ability_list = ability_list[::-1] # 反转数组，变成降序

    # 首位比
    total_ability = sum(ability_list)
    max_ability = max(ability_list)
    result_primate_ratio = max_ability/total_ability 

    # 首位度
    second_ability = ability_list[1]
    result_primate_degree = max_ability/second_ability 

    # 集中度
    N = ability_list.shape[0]
    mu = ability_list.mean()
    m1 = np.reshape(np.array(list(ability_list)*N),(N,N))
    m2 = m1.T
    m = m1 - m2
    abs_m = np.absolute(m)
    ss_part = (sum(sum(abs_m)))/2
    G = (1/(2*N**2*mu))*ss_part
    result_concentrate_degree = G 

    # 离心性
    # 找到功能中心
    sorted_villages = villages.sort_values(by=[ability_field],ascending=False)
    center_village = sorted_villages.iloc[0,:]
    geo_center = center_village['geometry'].centroid #功能中心的质心点对象
    # 计算part1
    sorted_villages['center_distance'] = sorted_villages['geometry'].apply(lambda a: a.centroid.distance(geo_center))
    sorted_villages['p1_value'] = sorted_villages[ability_field]*sorted_villages['center_distance']
    p1 = sum(sorted_villages['p1_value'])
    # 计算part2
    p2 = sum(list(ability_list)[1:]) - max_ability
    # 计算part3
    p3 = sum(sorted_villages['center_distance'])
    # 去掉值为0的村
    if 0 in ability_list:
        ability_list = list(ability_list)
        ability_list.remove(0)
        n = len(ability_list)
    else: 
        n = N
    C = (p1/p2)/(p3/n-1)  # 这里小n等于N，待定
    result_offcenter = C

    # 分散度
    sorted_villages['centroid_x'] = sorted_villages['geometry'].apply(lambda a: a.centroid.x)
    sorted_villages['centroid_y'] = sorted_villages['geometry'].apply(lambda a: a.centroid.y)
    xy_array = sorted_villages[['centroid_x','centroid_y']].values
    # A是一个向量矩阵：euclidean代表欧式距离
    distA=pdist(xy_array,metric='euclidean')
    # 将distA数组变成一个矩阵
    distB = squareform(distA)
    xixj = m1*m2
    xixjdij = m1*m2*distB
    ss_part1 = sum(sum(xixjdij))/2
    ss_part2 = sum(sum(xixj))/2
    ss_part3 = sum(sum(distB))/2
    A = (ss_part1/ss_part2)/(ss_part3/(n*(n-1)))
    result_disperse = A

    return result_primate_ratio,result_primate_degree,result_concentrate_degree,result_offcenter,result_disperse

# %%
for i in df_county.iterrows():
    index = i[0]
    items = i[1]
    code_county = items['区县代']
    
    for field in function_fields:
        r1,r2,r3,r4,r5 = calc_5value(code_county,field)

        field_prefix = field[:-1]+'_'
        df_county.loc[index,field_prefix+'首位比'] = r1
        df_county.loc[index,field_prefix+'首位度'] = r2
        df_county.loc[index,field_prefix+'集中度'] = r3
        df_county.loc[index,field_prefix+'离心性'] = r4
        df_county.loc[index,field_prefix+'分散度'] = r5
    
    print(code_county)

df_county.to_excel('result.xlsx',encoding = 'GB18030')