# %%
from arcpy import *
import os
from arcpy.analysis import Intersect
from arcpy.sa.Functions import ExtractByMask, ZonalStatisticsAsTable
from arcpy.sa import Con
import pandas as pd
import math
from dbfread import DBF

# 测试一下git
# 测试一下branch

# 参数设置(以上海为例)
# 市人口为 17640842，城镇人口为 20217748
real_urban_pop_6 = 17640842
real_total_pop_6 = 22315474
urban_ratio = real_urban_pop_6/real_total_pop_6
data_total_pop = 17236899.5
# 刘纪远的数据，分辨率为30，理论上，有效的radius应为30的倍数，最短buffer半径为15m
# 这里的radius都指buffer的半径，最终输出结果时需要*2
radius = 50
radius_step = 50

os.chdir(r'F:\\workspace\\Research_2022_city_boundary\\data_processing\\')
env.workspace = r'F:\workspace\Research_2022_city_boundary\data_processing\temp_workspace'
env.overwriteOutput = True

def zonal(polygon,polygon_field,raster):
    try:
        temp_zonal_table = f'temp_table.dbf'
        ZonalStatisticsAsTable(polygon,polygon_field,raster,temp_zonal_table)
        table = DBF(env.workspace+r'\\'+temp_zonal_table, encoding='utf8')
        result = sum(pd.DataFrame(iter(table))['SUM'])
        Delete_management(temp_zonal_table)
    except:
        return None
    return result

# %%
def preprocessing(county_code6,county_name):
# 选择需要进行操作的地区矢量
    ori_county_polygon = r"F:\workspace\Research_2022_city_boundary\data_processing\county_with_census_data.shp"
    county_name = county_name
    county_code6 = county_code6
    file_selected_county = f'{county_name}_polygon.shp'
    MakeFeatureLayer_management(ori_county_polygon, "lyr_counties")
    where_clause = '"code6" = \'{}\''.format(county_code6)
    SelectLayerByAttribute_management("lyr_counties", "NEW_SELECTION",where_clause)
    CopyFeatures_management("lyr_counties", file_selected_county)
    # 裁切城市栅格
    ori_landuse = r'H:\DataHub\Landcover_liujiyuan\China LandCover 00-08-10.gdb\CHINA2010'
    file_landuse_county = f'{county_name}_landuse.tif'
    extracted = ExtractByMask(ori_landuse,file_selected_county)
    extracted.save(file_landuse_county)
    # 裁切人口栅格
    ori_pop_raster = r"H:\DataHub\WorldPop_proj\chn_ppp_2010.tif"
    # ori_pop_raster = r"H:\DataHub\Landscan\LandScan Global 2010\lspop2010"
    global file_extracted_pop
    file_extracted_pop = f'{county_name}_pop.tif'
    extracted = ExtractByMask(ori_pop_raster,file_selected_county)
    extracted.save(file_extracted_pop)

    # 裁切政府所在地
    ori_gov = r"F:\workspace\Research_2022_city_boundary\data_processing\governments\China_county_gov_total.shp"
    global file_gov
    file_gov = f'{county_name}_gov.shp'
    Clip_analysis(ori_gov,file_selected_county,file_gov)

    # 提取土地利用类型为51和53的作为不透水面像元
    file_con = f'{county_name}_landuse_urban.tif'
    conned = Con(file_landuse_county,1,"","VALUE = 51 or VALUE = 53")
    conned.save(file_con)

    # 转为矢量
    global file_urban_polygon
    file_urban_polygon = f'{county_name}_ori_urban_polygon.shp'
    RasterToPolygon_conversion(file_con, file_urban_polygon, "NO_SIMPLIFY")


def calc_urban_ratio(county_name,radius):
    # 作buffer
    file_buffer = f'{county_name}_buffer_{radius}.shp'
    Buffer_analysis(file_urban_polygon,file_buffer,f'{radius} Meters')

    # dissolve
    file_dissolved_buffer = f'{county_name}_dissolve_{radius}.shp'
    Dissolve_management(file_buffer,file_dissolved_buffer)

    # explode
    file_explode_buffer = f'{county_name}_explode_{radius}.shp'
    MultipartToSinglepart_management(file_dissolved_buffer,file_explode_buffer)

    # 选中存在有政府的buffer斑块
    file_buffer_contain_gov = f'{county_name}_{radius}_buffer_gov.shp'
    MakeFeatureLayer_management(file_explode_buffer, "lyr_buffer")
    MakeFeatureLayer_management(file_gov, "lyr_gov")
    SelectLayerByLocation_management("lyr_buffer", 'intersect',"lyr_gov")
    CopyFeatures_management("lyr_buffer", file_buffer_contain_gov)

    # 选中未buffer的原始斑块，代表在radius下，这些斑块属于urban area
    result_selected_ori = os.getcwd() + r'\\result_urban_ratio\\' + f'{county_name}_urban_{radius}.shp'
    Intersect_analysis([file_urban_polygon,file_buffer_contain_gov],result_selected_ori)

    # zonal生成各斑块上的人口
    urban_pop = zonal(result_selected_ori,'Id',file_extracted_pop)
    ratio = urban_pop/data_total_pop

    return ratio

# %%
round = 0
status = 0 # residual < 0, status = 0; else status = 1
data_ratio = calc_urban_ratio(200100,init_radius)
# status不变化时，radius按照步长增长；status发生变化，则radius_step转为1/2
residual = data_ratio-urban_ratio
residual_list = []
radius_list = []
residual_list.append(residual)
radius_list.append(radius*2)

while True:
    
    round += 1 # 用于计数 

    # 判断radius如何变化
    # 四种情况，连续小于真值，按当前步长增加
    if residual < 0 and status == 0:
        radius += radius_step
    # 连续超过真值，就按相同倍率减小
    elif residual > 0 and status == 1:
        radius -= radius_step
    # 上次小于，这次大于，则步长减半减小
    elif residual > 0 and status == 0:
        status = 1
        radius_step = round(radius_step/2)
        radius -= radius_step
    # 上次大于，这次小于，则倍率减半增加
    elif residual < 0 and status == 1:
        status = 0
        radius_step = round(radius_step/2)
        radius += radius_step      
    
    data_ratio = calc_urban_ratio(200100,radius)
    residual = data_ratio-urban_ratio
    residual_list.append(residual)
    radius_list.append(radius*2)
    
    if radius < 15 or radius > 1000:
        break
    
    
min_residual = min([abs(i) for i in residual_list])
best_radius = radius_list[residual_list.index(min_residual)]


 
