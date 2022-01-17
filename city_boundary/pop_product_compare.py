# %%
from arcpy import *
import os
from arcpy.analysis import Intersect
from arcpy.sa.Functions import ExtractByMask, ZonalStatisticsAsTable
from arcpy.sa import Con
import pandas as pd
from dbfread import DBF

os.chdir(r'F:\workspace\Research_2022_city_boundary\pop_data_compare')
env.workspace = r'F:\workspace\Research_2022_city_boundary\pop_data_compare\tempdata'
env.overwriteOutput = True

# %%
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

def extract_urban_pop(destination_county,ori_pop_raster):
    # 选择需要进行操作的地区矢量
    ori_county_polygon = r"H:\DataHub\China_4level_polygon_2015.mdb\city2015"
    destination_county = destination_county
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
    # ori_pop_raster = r"H:\DataHub\GPWv4_Columbia\gpw_v4_population_count_rev11_2010_30_sec.tif"
    ori_pop_raster = ori_pop_raster
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
    # data_ori_pop = zonal(file_selected_county,'NAME',file_extracted_pop)
    data_urban_pop = zonal(file_urban_polygon,'FID',file_extracted_pop)
    # data_urban_ratio = data_urban_pop/data_ori_pop
    print(f'{destination_county}产品不透水面人口为{data_urban_pop}')
    return data_urban_pop
    # print(f'{destination_county}产品总人口为{data_ori_pop},不透水面人口为{data_urban_pop},城镇化率为{data_urban_ratio}')



df = pd.read_csv(r'total_table3.csv',encoding='gbk')
df = df.loc[:,['code6','name6','pop6', 'hukou6', 'nonagr6', 'urban6',
       'rural6', 'migcunty6', 'migprov6', 'miginter6',
       'uratio6','pop2010_landscan?', 'pop2010_worldpop?', 'pop2010_GPW4?']]
df.index = df['code6']

# df = pd.read_excel(r"F:\workspace\Research_2022_city_boundary\五普六普数据整理_王洁晶 20160201.xls",'六普')
# df = df.loc[:,['code6','name6','pop6', 'hukou6', 'nonagr6', 'urban6',
#        'rural6', 'migcunty6', 'migprov6', 'miginter6',
#        'uratio6','pop2010_landscan?', 'pop2010_worldpop?', 'pop2010_GPW4?']]
# df.index = df['Code']


ori_pop_raster1 = r"H:\DataHub\Landscan\LandScan Global 2010\lspop2010"
ori_pop_raster2 = r"H:\DataHub\WorldPop_proj\chn_ppp_2010.tif"
ori_pop_raster3 = r"H:\DataHub\GPWv4_Columbia\gpw_v4_population_count_rev11_2010_30_sec.tif"
pop_rasters = [ori_pop_raster1,ori_pop_raster2,ori_pop_raster3]
pop_rasters_names = ['landscan','worldpop','gpw4']
pop_rasters_clip = [33,0,0]

for raster,raster_name,raster_clip in zip(pop_rasters,pop_rasters_names,pop_rasters_clip):
    count = 1
    lst_df = list(df.iterrows())[:raster_clip]
    for i in lst_df:
        row = i[1]
        code6 = row['code6']
        name = row['name6']
        data_urban_pop = extract_urban_pop(name,raster)
        result_df = df.loc[code6,'impervious_pop_'+raster_name] = data_urban_pop
        print(f'{count}//{len(lst_df)},{code6},{name}:{data_urban_pop}')
        count=count+1

df.to_excel('result_urban_pop_city.xlsx', index=False)























