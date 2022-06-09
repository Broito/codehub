import geopandas as gpd
import pandas as pd
import numpy as np

gdf = gpd.GeoDataFrame.from_file('E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\commuting_baidu\China_urban_2018_with_pop_20220501v2\China_urban_2018_with_pop_v2.shp')
gdf_county = gpd.GeoDataFrame.from_file("E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\百度扩样\百度对应_县级区划.shp")
df_home = pd.read_excel("E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\百度扩样\百度扩样0510.xlsx",'home')
df_work = pd.read_excel("E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\百度扩样\百度扩样0510.xlsx",'work')

gdf.rename(columns={'工作':'work_andr','居住':'home_andr' },inplace=True)
gdf_county = gdf_county.drop(gdf_county[gdf_county['codeF7']==0].index)

unmatched = [] #存放匹配不上的表
def calc_avg_ratio(df,code_list):
    ratio_list = []
    for code in code_list:
        try:
            ratio = df[df['district_id']==code]['android_percent'].values[0]
            ratio_list.append(ratio)
        except:
            unmatched.append(code)
            print(f'{code}匹配不上百度的表。')
            continue
    return np.mean(ratio_list)

urbans = list(gdf.iterrows())
for urban in urbans: 
    urban_index = urban[0]
    geometry = urban[1]['geometry']
    counties = gdf_county[gdf_county.intersects(geometry)] 
    counties_id = list(counties['codeF7'])
    ratio_home = calc_avg_ratio(df_home,counties_id)
    ratio_work = calc_avg_ratio(df_work,counties_id)
    gdf.loc[urban_index,'work_all'] = int(gdf.loc[urban_index,'work_andr']/ratio_work)
    gdf.loc[urban_index,'home_all'] = int(gdf.loc[urban_index,'home_andr']/ratio_home)

gdf.to_file('E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\commuting_baidu\China_urban_2018_with_pop_20220501v2\China_urban_2018_with_pop_扩样.shp',encoding = 'utf8')

# 匹配不上的code
# [350681,
#  350625,
#  431121,
#  340203,
#  340221,
#  340222,
#  654223,
#  350402,
#  350403,
#  350427,
#  320602,
#  320684,
#  410322,
#  410381,
#  410306,
#  520221,
#  421023,
#  330104,
#  632321,
#  330103,
#  632857,
#  520522]








