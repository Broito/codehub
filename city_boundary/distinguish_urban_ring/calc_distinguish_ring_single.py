# %%
from arcpy import *
import os
from arcpy.analysis import Intersect
from arcpy.sa.Functions import ExtractByMask, ZonalStatisticsAsTable
from arcpy.sa import Con, Shrink, Expand
import pandas as pd
from dbfread import DBF
import numpy as np
import math

os.chdir(r'E:\\workspace\\Research_2022_city_boundary\\distinguish_ring\\')
env.workspace = r'E:\workspace\Research_2022_city_boundary\distinguish_ring\temp_workspace'
env.overwriteOutput = True

# %% 这里的zonal是取均值（忽略空值）
def zonal(polygon,polygon_field,raster):
    try:
        temp_zonal_table = f'temp_table.dbf'
        ZonalStatisticsAsTable(polygon,polygon_field,raster,temp_zonal_table)
        table = DBF(env.workspace+r'\\'+temp_zonal_table, encoding='utf8')
        result = np.mean(pd.DataFrame(iter(table))['MEAN'])
        Delete_management(temp_zonal_table)
    except:
        return None
    return result

# 选择所在省的栅格，但用完该方法后要记得重新设置env.workspace
def select_region(code6):
    prov_code = str(code6)[:2]
    env.workspace = r'I:\DataHub\Landuse_GAIA\Urban and rural'
    tifs = ListRasters()
    for tif in tifs:
        if prov_code == tif[:2]:
            return tif

# %%
def preprocessing(county_code6,county_name):

    # 选择需要进行操作的地区矢量
    ori_county_polygon = r".\county_with_census_data.shp"
    county_name = county_name
    county_code6 = county_code6
    file_selected_county = f'{county_name}_polygon.shp'
    MakeFeatureLayer_management(ori_county_polygon, "lyr_counties")
    where_clause = '"code6" = \'{}\''.format(county_code6)
    SelectLayerByAttribute_management("lyr_counties", "NEW_SELECTION",where_clause)
    CopyFeatures_management("lyr_counties", file_selected_county)
    
    # 选择所在省份栅格
    tif_path = r'I:\\DataHub\\Landuse_GAIA\\Urban and rural\\'
    ori_landuse = tif_path + select_region(county_code6)
    env.workspace = r'.\temp_workspace'
    # 裁切城市栅格
    file_landuse_county = f'{county_name}_landuse.tif'
    extracted = ExtractByMask(ori_landuse,file_selected_county)
    extracted.save(file_landuse_county)

    # 裁切人口栅格
    ori_pop_raster = r"I:\DataHub\WorldPop_proj\chn_ppp_2010.tif"
    global file_extracted_pop
    file_extracted_pop = f'{county_name}_pop.tif'
    extracted = ExtractByMask(ori_pop_raster,file_selected_county)
    extracted.save(file_extracted_pop)

    # 裁切夜间灯光栅格
    ori_ntl = r"I:\DataHub\Long_NTL\LongNTL_2010.tif"
    global file_ntl
    file_ntl = f'{county_name}_ntl.tif'
    extracted = ExtractByMask(ori_ntl,file_selected_county)
    extracted.save(file_ntl) 


    # 裁切政府所在地
    ori_gov = r".\governments\China_county_gov_total.shp"
    global file_gov
    file_gov = f'{county_name}_gov.shp'
    Clip_analysis(ori_gov,file_selected_county,file_gov)

    # 提取像元值大于7的作为2010年不透水面像元
    file_con = f'{county_name}_landuse_urban.tif'
    conned = Con(file_landuse_county,1,"","VALUE > 7")
    conned.save(file_con)

    # 先收缩后膨胀
    shrink_radius = 1
    file_shrink = f'{county_name}_shrink{shrink_radius}_urban.tif'
    layer_shrink = Shrink(file_con,shrink_radius,1)
    layer_shrink.save(file_shrink)

    file_expand = f'{county_name}_expand{shrink_radius}_urban.tif'
    layer_expand = Expand(file_shrink,shrink_radius,1)
    layer_expand.save(file_expand)
    
    # 转为矢量
    global file_urban_polygon
    file_urban_polygon = f'{county_name}_ori_urban_polygon.shp'
    RasterToPolygon_conversion(file_expand, file_urban_polygon, "NO_SIMPLIFY")


def get_buffer_urban_patch(county_name,radius):

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
    SelectLayerByLocation_management("lyr_buffer", 'intersect',"lyr_gov",'500 Meters')
    CopyFeatures_management("lyr_buffer", file_buffer_contain_gov)

    # 选中未buffer的原始斑块，代表在radius下，这些斑块属于urban area
    file_patch_urban = f'{county_name}_urban_{radius}.shp'
    Intersect_analysis([file_urban_polygon,file_buffer_contain_gov],file_patch_urban)
    
    return file_patch_urban

# 获得当前环带的三个判别值
def get_ring_value(county_name,certain_urban,new_urban_patch,radius):

    # 获取当前环带矢量
    file_ring_patch = f'{county_name}_ring_{radius}.shp'
    Erase_analysis(new_urban_patch,certain_urban,file_ring_patch)

    # merge 环带斑块
    file_merged_ring = f'{county_name}_merged_ring_{radius}.shp'
    Dissolve_management(file_ring_patch,file_merged_ring)

    # 计算三个判别值
    mean_pop_ring = zonal(file_merged_ring,'Id',file_extracted_pop)
    mean_ntl_ring = zonal(file_merged_ring,'Id',file_ntl)
    combo_ring = mean_pop_ring*mean_ntl_ring

    return mean_pop_ring,mean_ntl_ring,combo_ring

def get_threshold(county_name,certain_urban,radius):

    file_patch_urban = certain_urban

    # rural_patch = total patch - urban_patch
    file_patch_rural = f'{county_name}_rural_{radius}.shp'
    Erase_analysis(file_urban_polygon,file_patch_urban,file_patch_rural)

    # merge urban斑块和rural斑块，用来下一步直接zonal求mean 
    file_merged_urban = f'{county_name}_merged_urban_{radius}.shp'
    file_merged_rural = f'{county_name}_merged_rural_{radius}.shp'
    Dissolve_management(file_patch_urban,file_merged_urban)
    Dissolve_management(file_patch_rural,file_merged_rural)

    # zonal生成各斑块上的人口
    mean_pop_urban = zonal(file_merged_urban,'Id',file_extracted_pop)
    mean_pop_rural = zonal(file_merged_rural,'Id',file_extracted_pop)
    # zonal生成各斑块上的夜间灯光
    mean_ntl_urban = zonal(file_merged_urban,'Id',file_ntl)
    mean_ntl_rural = zonal(file_merged_rural,'Id',file_ntl)

    # 计算三个指标
    threshold_pop = math.sqrt(mean_pop_urban*mean_pop_rural)
    threshold_ntl = math.sqrt(mean_ntl_urban*mean_ntl_rural)
    threshold_combo = threshold_pop * threshold_ntl

    return threshold_pop,threshold_ntl,threshold_combo

def strategy_deside(strategy,threshold_pop,threshold_ntl,threshold_combo,current_pop,current_ntl,current_combo):
    
    # 如果策略为 loose
    if strategy == 'loose':
        if current_pop < threshold_pop and current_ntl < threshold_ntl:
            return False
        else:
            return True

    # 如果策略为 strict
    elif strategy == 'strict':
        if current_pop >= threshold_pop and current_ntl >= threshold_ntl:
            return True
        else:
            return False

    # 如果策略为 median
    elif strategy == 'combo':
        if current_combo >= threshold_combo:
            return True
        else:
            return False
    
    elif strategy == 'only_pop':
        if current_pop >= threshold_pop:
            return True
        else:
            return False
    
    elif strategy == 'only_ntl':
        if current_ntl >= threshold_ntl:
            return True
        else:
            return False

# %% select final polygon
def copy_polygon_to_result(county_name,selected_file,thres,strategy):
    out_path = f'.\\result_folder\\{strategy}\\'
    out_selected_file = f'{county_name}_urban_{strategy}_{thres}.shp'
    CopyFeatures_management(selected_file,out_path+out_selected_file)

# %%  <<<<<<<<<<<<<<<<<<<<<<<<<<<-----运行部分----->>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 获取六普人口和城市化率
df = pd.read_csv('census6_main.csv',encoding = 'gb18030')
df.index = df['code6']
code6 = 110100
name = df.loc[code6,'城市名']

strategy_list = ['loose','strict','combo','only_pop','only_ntl']
for strategy in strategy_list:


    preprocessing(code6,name)
    file_patch_urban = get_buffer_urban_patch(name,1) # 获取初始斑块
    threshold_pop,threshold_ntl,threshold_combo = get_threshold(name,file_patch_urban,1)


    # setup variable
    times = 0
    step = 15
    radius = 15

    # strategy = 'loose'  


    # 日志记录
    log = open('log.txt','a')
    log.write(f'{code6},{name},strategy:{strategy}：↓ [pop,ntl,combo]\n')
    print(f'{code6},{name},strategy:{strategy}：↓ [pop,ntl,combo]\n')

    while True:

        times += 1

        new_urban_patch = get_buffer_urban_patch(name,radius)
        current_pop,current_ntl,current_combo = get_ring_value(name,file_patch_urban,new_urban_patch,radius)
        print(f'round:{times} -=> radius={radius},\n\t thres:{threshold_pop},{threshold_ntl},{threshold_combo} \n\t current:{current_pop},{current_ntl},{current_combo}\n')
        log.write(f'round:{times} -=> radius={radius},\n\t thres:{threshold_pop},{threshold_ntl},{threshold_combo} \n\t current:{current_pop},{current_ntl},{current_combo}\n')
        decide = strategy_deside(strategy,threshold_pop,threshold_ntl,threshold_combo,current_pop,current_ntl,current_combo)
        if decide:
            file_patch_urban = new_urban_patch
            threshold_pop,threshold_ntl,threshold_combo = get_threshold(name,file_patch_urban,radius)
            radius += step
            continue
        else:
            finally_urban = file_patch_urban
            copy_polygon_to_result(name,finally_urban,radius,strategy)
            print(f'>>>>>>> urban radius = {radius-15}\n\n')
            log.write(f'>>>>>>> urban radius = {radius-15}\n\n')
            break

    log.close()













