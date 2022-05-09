import coordinate_conversion
import geopandas as gpd
from shapely.geometry import Polygon,MultiPolygon

(x,y) = coordinate_conversion.gcj02towgs84(121.377,31.158)

gdf = gpd.GeoDataFrame.from_file(r"J:\数据\上海市门牌尺度人口数据\wgs84修正_residential_area_population_shanghai.gdb",
                                 driver='OpenFileGDB',
                                 layer="residential_pop_Shanghai")

gdf.rename(columns={'城乡分':'ur_code', 
                    'Sum_经度':'sum_lon',
                    'Sum_纬度':'sum_lat',
                    'Sum_房屋':'num_room',
                    'Sum_0_4岁_男':'男0_4',
                    'Sum_0_4岁_女':'女0_4',
                    'Sum_5_9岁_男':'男5_9',
                    'Sum_5_9岁_女':'女5_9',
                    'Sum_10_14岁_男':'男10_14',
                    'Sum_10_14岁_女':'女10_14',
                    'Sum_15_19岁_男':'男15_19',
                    'Sum_15_19岁_女':'女15_19',
                    'Sum_20_24岁_男':'男20_24',
                    'Sum_20_24岁_女':'女20_24',
                    'Sum_25_29岁_男':'男25_29',
                    'Sum_25_29岁_女':'女25_29',
                    'Sum_30_34岁_男':'男30_34',
                    'Sum_30_34岁_女':'女30_34',
                    'Sum_35_39岁_男':'男35_39',
                    'Sum_35_39岁_女':'女35_39',
                    'Sum_40_44岁_男':'男40_44',
                    'Sum_40_44岁_女':'女40_44',
                    'Sum_45_49岁_男':'男45_49',
                    'Sum_45_49岁_女':'女45_49',
                    'Sum_50_54岁_男':'男50_54',
                    'Sum_50_54岁_女':'女50_54',
                    'Sum_55_59岁_男':'男55_59',
                    'Sum_55_59岁_女':'女55_59',
                    'Sum_60_64岁_男':'男60_64',
                    'Sum_60_64岁_女':'女60_64',
                    'Sum_65_69岁_男':'男65_69',
                    'Sum_65_69岁_女':'女65_69',
                    'Sum_70_74岁_男':'男70_74',
                    'Sum_70_74岁_女':'女70_74',
                    'Sum_75_79岁_男':'男75_79',
                    'Sum_75_79岁_女':'女75_79',
                    'Sum_80岁以上_男':'男80_', 
                    'Sum_80岁以上_女':'女80_',
                    'Sum_合_男':'男sum',
                    'Sum_合_女':'女sum',
                    'Sum_60岁以上_男':'男60_',
                    'Sum_60岁以上_女':'女60_',
                    'Sum_60岁以上':'60_',
                    'Sum_合':'pop_sum'},inplace=True)

def polygon_gjc02_to_wgs84(geo):
    polygon = geo[0]
    ext_coords = list(polygon.exterior.coords) # 获取外边界线坐标list
    wgs84_ext_coords = [tuple(coordinate_conversion.gcj02towgs84(i[0],i[1])) for i in ext_coords]
    wgs84_polygon = Polygon(wgs84_ext_coords)
    return wgs84_polygon

for row in gdf.iterrows():
    index = row[0]
    item = row[1]
    geo = item['geometry']
    wgs84_geo = polygon_gjc02_to_wgs84(geo)
    gdf.loc[index,'geometry'] = wgs84_geo
    print(index)

gdf.to_file(r'J:\数据\上海市门牌尺度人口数据\wgs84建筑物polygon人口2016_王宁诚修正\wgs84上海polygon人口带年龄结构2016.shp',encoding = 'gb18030')
    























