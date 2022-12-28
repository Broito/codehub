import coordinate_conversion
import geopandas as gpd
from shapely.geometry import Point
import os

os.chdir(r'G:\数据\全国百度POI数据（2012-2017）数据集\shanghai_2017_poi')
gdf = gpd.read_file(r'医疗保健服务.shp')
gdf['geometry'] = gdf['geometry'].apply(lambda a: Point(coordinate_conversion.gcj02towgs84(a.x,a.y)))

gdf.to_file(r'医疗保健服务_wgs84.shp',encoding = 'gb18030')


















