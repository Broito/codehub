import os 
import geopandas as gpd

os.chdir(r'I:\DataHub\全国POI2020\2020高德POI_2级分类数据\2020高德POI_2级分类_shp')
pois = [i for i in os.listdir() if i[-4:]=='.shp']

os.chdir(r'C:\Users\NingchengWang\Desktop\天津POI')
path_head_poi = r'I:\\DataHub\\全国POI2020\\2020高德POI_2级分类数据\\2020高德POI_2级分类_shp\\'

for poi in pois[251:]:
    name = poi[:-4]

    gdf_poi = gpd.read_file(path_head_poi+poi)

    gdf_poi_selected = gdf_poi[(gdf_poi['city']=="天津市")&(gdf_poi['district']=="和平区")]

    if gdf_poi_selected.shape[0] == 0:
        print(f'{name}此类型和平区不存在。')
    else:
        gdf_poi_selected.to_file(name+'.shp', encoding = 'utf8')
        print(name)
















