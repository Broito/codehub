'''
Author: your name
Date: 2021-12-29 16:10:00
LastEditTime: 2021-12-30 16:06:41
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: \【代码库】\city_boundary\py3_calc_best_thres_init.py
'''
# %%
from arcpy import *
import os
from arcpy.analysis import Intersect
from arcpy.sa.Functions import ExtractByMask, ZonalStatisticsAsTable
from arcpy.sa import Con
import pandas as pd

'''
区县级政府所在地筛选原则
step1： where "name" LIKE '%市人民政府' or  "name" LIKE '%县人民政府'   
    or  "name" LIKE '%州人民政府'   or  "name" LIKE '%旗人民政府'   
    or  "name" LIKE '%盟人民政府' 
step2: 在那些没有这些政府的区域，筛选 name LIKE '%政协%' 
        and name not LIKE '%镇%'  and name not LIKE '%村%' 
step3: 在那些仍没有这些政府的区域，筛选
        type LIKE '%区县级政府%' and ( name like '%政府%' or name like '%政%') 
        剩下26个实在没有的就手动选一下
step4: step123 merge
!!!!!!!要记得写上没有政府与斑块重叠的情况！
'''
'''
# ori前缀为原始数据，不可删除
# file前缀为中间过程数据，需要处理完删除
# 无前缀为常量
'''

os.chdir(r'E:\\workspace\\Research_2022_city_boundary\\data_processing\\')
env.workspace = r'E:\workspace\Research_2022_city_boundary\data_processing\temp_workspace'
env.overwriteOutput = True

def zonal(polygon,polygon_field,raster):
    temp_zonal_table = f'temp_table'
    temp_zonal_table2 = f'temp_table.csv'
    ZonalStatisticsAsTable(polygon,polygon_field,raster,temp_zonal_table)
    TableToTable_conversion(temp_zonal_table,env.workspace,temp_zonal_table2)
    result = pd.read_csv(env.workspace+r'\\'+temp_zonal_table2)['SUM']
    Delete_management(temp_zonal_table)
    Delete_management(temp_zonal_table2)

# %%
# 参数设置
real_urban_pop_6 = 20217748
real_total_pop_6 = 22315474
urban_ratio = real_urban_pop_6/real_total_pop_6
data_total_pop = 13431743
# 刘纪远的数据，分辨率为30，因此radius应为30的倍数，步长以15记
radius = 500

''' ***********   土地利用数据预处理  ************'''
''' 每个城市跑一遍就可以了 '''
# %%
# 选择需要进行操作的地区矢量
ori_county_polygon = r"E:\workspace\Research_2022_city_boundary\data_processing\county_with_census_data.shp"
destination_county = "上海市辖区"
county_name = "上海"
file_selected_county = f'{county_name}_polygon.shp'
MakeFeatureLayer_management(ori_county_polygon, "lyr_counties")
where_clause = '"name6" = \'{}\''.format(destination_county)
SelectLayerByAttribute_management("lyr_counties", "NEW_SELECTION",where_clause)
CopyFeatures_management("lyr_counties", file_selected_county)
# 裁切城市栅格
ori_landuse = r'I:\DataHub\Landcover_liujiyuan\China LandCover 00-08-10.gdb\CHINA2010'
file_landuse_county = f'{county_name}_landuse.tif'
extracted = ExtractByMask(ori_landuse,file_selected_county)
extracted.save(file_landuse_county)
# 裁切人口栅格
# ori_pop_raster = r"I:\DataHub\WorldPop_proj\chn_ppp_2010.tif"
ori_pop_raster = r"I:\DataHub\Landscan\LandScan Global 2010\lspop2010"
file_extracted_pop = f'{county_name}_pop.tif'
extracted = ExtractByMask(ori_pop_raster,file_selected_county)
extracted.save(file_extracted_pop)
# 裁切政府所在地
ori_gov = r"E:\workspace\Research_2022_city_boundary\data_processing\governments\China_county_gov_total.shp"
file_gov = f'{county_name}_gov.shp'
Clip_analysis(ori_gov,file_selected_county,file_gov)
# 计算该区域人口数据产品的原始总人口数


# %% 提取城市区域
# 提取土地利用类型为51和52的作为不透水面像元
file_con = f'{county_name}_landuse_urban.tif'
conned = Con(file_landuse_county,1,"","VALUE = 51 or VALUE = 52")
conned.save(file_con)

# 转为矢量 
file_urban_polygon = f'{county_name}_ori_urban_polygon.shp'
RasterToPolygon_conversion(file_con, file_urban_polygon, "NO_SIMPLIFY")


''' ********** 计算阈值范围下的城市边界 *********** '''
'''  按radius循环，每个城市不同radius都需要跑一遍    '''

# %%
# 作buffer
file_buffer = f'{county_name}_buffer_{radius}.shp'
Buffer_analysis(file_urban_polygon,file_buffer,f'{radius} Meters')

# %%
# dissolve
file_dissolved_buffer = f'{county_name}_dissolve_{radius}.shp'
Dissolve_management(file_buffer,file_dissolved_buffer)

# %%
# explode
file_explode_buffer = f'{county_name}_explode_{radius}.shp'
MultipartToSinglepart_management(file_dissolved_buffer,file_explode_buffer)

# %%
# 选中存在有政府的buffer斑块
file_buffer_contain_gov = f'{county_name}_{radius}_buffer_gov.shp'
MakeFeatureLayer_management(file_explode_buffer, "lyr_buffer")
MakeFeatureLayer_management(file_gov, "lyr_gov")
SelectLayerByLocation_management("lyr_buffer", 'intersect',"lyr_gov")
CopyFeatures_management("lyr_buffer", file_buffer_contain_gov)

# %% 选中未buffer的原始斑块，代表在radius下，这些斑块属于urban area
result_selected_ori = os.getcwd() + r'\\result_urban_ratio\\' + f'{county_name}_urban_{radius}.shp'
Intersect_analysis([file_urban_polygon,file_buffer_contain_gov],result_selected_ori)



'''  **********        下面是人口计算部分        *********  '''

# %% zonal生成各斑块上的人口
file_zonal_table = f'{county_name}_{radius}_table'
file_zonal_table2 = f'{county_name}_{radius}_table.csv'
ZonalStatisticsAsTable(result_selected_ori,'Id',file_extracted_pop,file_zonal_table)
TableToTable_conversion(file_zonal_table,env.workspace,file_zonal_table2)
# %% 计算城镇化率
df = pd.read_csv(r'.\\temp_workspace\\'+ file_zonal_table2,encoding='utf-8')
urban_pop = sum(df['SUM'])
ratio = urban_pop/data_total_pop 
print(ratio)


'''  **********        删除过程文件        *********  '''
# %%
Delete_management(file_buffer_contain_gov)
Delete_management(file_buffer)
Delete_management(file_con)
Delete_management(file_dissolved_buffer)
Delete_management(file_explode_buffer)
Delete_management(file_dissolved_buffer)
Delete_management(file_selected_county)
Delete_management(file_landuse_county)
Delete_management(file_extracted_pop)
Delete_management(file_urban_polygon)
Delete_management(file_zonal_table)
Delete_management(file_zonal_table2)
Delete_management(file_gov)