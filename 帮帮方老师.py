import geopandas as gpd
import pandas as pd
import os 
from numpy import *

os.chdir(r'C:\Users\NingchengWang\Desktop')
df = pd.read_excel(r"C:\Users\NingchengWang\Desktop\生态安全指标得分情况.xlsx","Sheet1")

years = list(range(2009,2019))
gdf_names = ['gdf_'+str(i) for i in years]
sprawl = []
gdfs = []

# 读取所有gdf,变量名是 gdf_2009
for year,gdf_name in zip(years,gdf_names):
    globals()[gdf_name] = gpd.GeoDataFrame.from_file(r"I:\finished_project\Research_2021_urban_population_calc\data_processing\outcome_folder_city_unit\area_limit_world_pop_density_polygon_finally.gdb",
                                 driver='OpenFileGDB',
                                 layer=f"chn_ppp_{year}_density_stat")
    gdfs.append(globals()[gdf_name])

for i in df.iterrows():
    index = i[0]
    item = i[1]
    city = item['城市']+'市'
    sprawl_area = []
    sprawl_area_high = []
    sprawl_area_low = []
    sprawl_area_speed = []
    sprawl_area_high_speed = []
    sprawl_area_low_speed = []
    
    urban_area_bench = gdf_2010.loc[(gdf['type']=='urban')&(gdf['city']==city)]['Shape_Area'].sum()
    urban_area_bench_low = gdf_2010.loc[(gdf['gridcode']==1)&(gdf['city']==city)]['Shape_Area'].sum()
    urban_area_bench_high = gdf_2010.loc[(gdf['gridcode']==2)&(gdf['city']==city)]['Shape_Area'].sum()

    for a in range(len(gdfs)-1):
        gdf1 = gdfs[a]
        gdf = gdfs[a+1]
        # 计算增加的面积
        urban_area_1 = gdf1.loc[(gdf1['type']=='urban')&(gdf1['city']==city)]['Shape_Area'].sum()
        urban_area_2 = gdf.loc[(gdf['type']=='urban')&(gdf['city']==city)]['Shape_Area'].sum()
        sprawl_area.append(urban_area_2-urban_area_1)
        # 计算高密度urban增加的面积
        urban_area_low_1 = gdf1.loc[(gdf1['gridcode']==1)&(gdf1['city']==city)]['Shape_Area'].sum()
        urban_area_low_2 = gdf.loc[(gdf['gridcode']==1)&(gdf['city']==city)]['Shape_Area'].sum()
        sprawl_area_low.append(urban_area_low_2-urban_area_low_1)
        # 计算低密度urban增加的面积
        urban_area_high_1 = gdf1.loc[(gdf1['gridcode']==2)&(gdf1['city']==city)]['Shape_Area'].sum()
        urban_area_high_2 = gdf.loc[(gdf['gridcode']==2)&(gdf['city']==city)]['Shape_Area'].sum()
        sprawl_area_high.append(urban_area_high_2-urban_area_high_1)

    # 计算增加的面积
    avg_sprawl_area = mean(sprawl_area)
    avg_sprawl_area_low = mean(sprawl_area_low)
    avg_sprawl_area_high = mean(sprawl_area_high)
    # 计算增加的速度
    urban_speed = avg_sprawl_area/urban_area_bench
    urban_speed_low = avg_sprawl_area_low/urban_area_bench_low
    urban_speed_high = avg_sprawl_area_high/urban_area_bench_high

    df.loc[index,'avg_sprawl_area'] = avg_sprawl_area
    df.loc[index,'avg_sprawl_area_low'] = avg_sprawl_area_low
    df.loc[index,'avg_sprawl_area_high'] = avg_sprawl_area_high
    df.loc[index,'urban_speed'] = urban_speed
    df.loc[index,'urban_speed_low'] = urban_speed_low
    df.loc[index,'urban_speed_high'] = urban_speed_high

    print(f'{city}')

df.to_excel('urban_sprawl_result.xlsx')



# egen std_avg_sprawl_area = std(avg_sprawl_area)
# egen std_avg_sprawl_area_low = std(avg_sprawl_area_low)
# egen std_avg_sprawl_area_high = std(avg_sprawl_area_high)
# egen std_urban_speed = std(urban_speed)
# egen std_urban_speed_low = std(urban_speed_low)
# egen std_urban_speed_high = std(urban_speed_high)
# reg 生态安全得分 std_avg_sprawl_area std_urban_speed std_urban_speed_low std_urban_speed_high,robust
















































































