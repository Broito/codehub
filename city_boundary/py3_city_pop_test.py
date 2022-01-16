# %%
from arcpy import *
import os
from arcpy.analysis import Intersect
from arcpy.sa.Functions import ExtractByMask, ZonalStatisticsAsTable
from arcpy.sa import Con
import pandas as pd
from dbfread import DBF

os.chdir(r'F:\\workspace\\Research_2022_city_boundary\\data_processing\\')
env.workspace = r'F:\workspace\Research_2022_city_boundary\data_processing\temp_workspace'
env.overwriteOutput = True

# %%
def zonal(polygon,polygon_field,raster):
    temp_zonal_table = f'temp_table.dbf'
    ZonalStatisticsAsTable(polygon,polygon_field,raster,temp_zonal_table)
    table = DBF(env.workspace+r'\\'+temp_zonal_table, encoding='utf8')
    result = sum(pd.DataFrame(iter(table))['SUM'])
    Delete_management(temp_zonal_table)
    return result

# %%
# 选择需要进行操作的地区矢量
ori_county_polygon = r"F:\workspace\Research_2022_city_boundary\data_processing\county_with_census_data.shp"
destination_county = "上海市辖区"
county_name = destination_county
file_selected_county = f'{county_name}_polygon.shp'
MakeFeatureLayer_management(ori_county_polygon, "lyr_counties")
where_clause = '"name6" = \'{}\''.format(destination_county)
SelectLayerByAttribute_management("lyr_counties", "NEW_SELECTION",where_clause)
CopyFeatures_management("lyr_counties", file_selected_county)

# 裁切城市栅格
ori_landuse = r'H:\DataHub\Landcover_liujiyuan\China LandCover 00-08-10.gdb\CHINA2010'
file_landuse_county = f'{county_name}_landuse.tif'
extracted = ExtractByMask(ori_landuse,file_selected_county)
extracted.save(file_landuse_county)

# 裁切人口栅格
# ori_pop_raster = r"H:\DataHub\WorldPop_proj\chn_ppp_2010.tif"
# ori_pop_raster = r"I:\DataHub\Landscan\LandScan Global 2010\lspop2010"
ori_pop_raster = r"H:\DataHub\GPWv4_Columbia\gpw_v4_population_count_rev11_2010_30_sec.tif"
file_extracted_pop = f'{county_name}_pop.tif'
extracted = ExtractByMask(ori_pop_raster,file_selected_county)
extracted.save(file_extracted_pop)

# 提取土地利用类型为51和52的作为不透水面像元
file_con = f'{county_name}_landuse_urban.tif'
conned = Con(file_landuse_county,1,"","VALUE = 51 or VALUE = 53")
conned.save(file_con)

# 转为矢量 
file_urban_polygon = f'{county_name}_ori_urban_polygon.shp'
RasterToPolygon_conversion(file_con, file_urban_polygon, "NO_SIMPLIFY")

# 计算该区域人口数据产品的原始总人口数
data_ori_pop = zonal(file_selected_county,'NAME',file_extracted_pop)
data_urban_pop = zonal(file_urban_polygon,'FID',file_extracted_pop)
data_urban_ratio = data_urban_pop/data_ori_pop
print(f'{destination_county}产品总人口为{data_ori_pop},不透水面人口为{data_urban_pop},城镇化率为{data_urban_ratio}')

# %% 计算全国六普的
census6 = pd.read_csv(r"F:\workspace\Research_2022_city_boundary\data_processing\county_with_census_data.csv",encoding = 'utf8')
select_city = census6[census6['name6']==destination_county]
urban_ratio6 = float(select_city['uratio6'].values[0])
pop6 = select_city['pop6'].values[0]
urban6 = select_city['urban6'].values[0]
print(f'{destination_county}6普总人口为{pop6},城镇人口为{urban6},城镇化率为{urban_ratio6}')
