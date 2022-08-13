import os 
import geopandas as gpd
import pandas as pd

os.chdir(r'I:\DataHub\全国POI2020\2020高德POI_2级分类数据\2020高德POI_1级分类_csv\csv')
csvs = os.listdir()

os.chdir(r'C:\Users\NingchengWang\Desktop\天津POI\一级分类')
path_head_csv = r'I:\\DataHub\\全国POI2020\\2020高德POI_2级分类数据\\2020高德POI_1级分类_csv\\csv\\'

for csv in csvs:

    df = pd.read_csv(path_head_csv+csv)
    df_selected = df[(df['city']=="天津市")&(df['district']=="和平区")]

    gdf = gpd.GeoDataFrame()