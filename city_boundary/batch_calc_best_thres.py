# %%
from arcpy import *
import os
from arcpy.analysis import Intersect
from arcpy.sa.Functions import ExtractByMask, ZonalStatisticsAsTable
from arcpy.sa import Con
import pandas as pd
import math
from dbfread import DBF
from datetime import datetime 

os.chdir(r'E:\\workspace\\Research_2022_city_boundary\\data_processing\\')
env.workspace = r'E:\workspace\Research_2022_city_boundary\data_processing\temp_workspace'
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

# %%
def preprocessing(county_code6,county_name):
# 选择需要进行操作的地区矢量
    ori_county_polygon = r"E:\workspace\Research_2022_city_boundary\data_processing\county_with_census_data.shp"
    county_name = county_name
    county_code6 = county_code6
    file_selected_county = f'{county_name}_polygon.shp'
    MakeFeatureLayer_management(ori_county_polygon, "lyr_counties")
    where_clause = '"code6" = \'{}\''.format(county_code6)
    SelectLayerByAttribute_management("lyr_counties", "NEW_SELECTION",where_clause)
    CopyFeatures_management("lyr_counties", file_selected_county)
    # 裁切城市栅格
    ori_landuse = r'I:\DataHub\Landcover_liujiyuan\China LandCover 00-08-10.gdb\CHINA2010'
    file_landuse_county = f'{county_name}_landuse.tif'
    extracted = ExtractByMask(ori_landuse,file_selected_county)
    extracted.save(file_landuse_county)
    # 裁切人口栅格
    ori_pop_raster = r"I:\DataHub\WorldPop_proj\chn_ppp_2010.tif"
    # ori_pop_raster = r"I:\DataHub\Landscan\LandScan Global 2010\lspop2010"
    global file_extracted_pop
    file_extracted_pop = f'{county_name}_pop.tif'
    extracted = ExtractByMask(ori_pop_raster,file_selected_county)
    extracted.save(file_extracted_pop)

    # 裁切政府所在地
    ori_gov = r"E:\workspace\Research_2022_city_boundary\data_processing\governments\China_county_gov_total.shp"
    global file_gov
    file_gov = f'{county_name}_gov.shp'
    Clip_analysis(ori_gov,file_selected_county,file_gov)

    # 提取土地利用类型为51,52,53的作为不透水面像元
    file_con = f'{county_name}_landuse_urban.tif'
    conned = Con(file_landuse_county,1,"","VALUE = 51 or VALUE = 52 or VALUE = 53")
    conned.save(file_con)

    # 转为矢量
    global file_urban_polygon
    file_urban_polygon = f'{county_name}_ori_urban_polygon.shp'
    RasterToPolygon_conversion(file_con, file_urban_polygon, "NO_SIMPLIFY")

    # 计算不透水面总人口
    impervious_pop = zonal(file_urban_polygon,'Id',file_extracted_pop)
    benchmark_pop = impervious_pop*ratio6

    return impervious_pop,benchmark_pop

def calc_data_urban_pop(county_name,radius):
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
    result_selected_ori = f'{county_name}_urban_{radius}.shp'
    Intersect_analysis([file_urban_polygon,file_buffer_contain_gov],result_selected_ori)

    # zonal生成各斑块上的人口
    urban_pop = zonal(result_selected_ori,'Id',file_extracted_pop)

    return urban_pop


# %% 计算最佳阈值，benchmark_pop为要比对的基准人口
def find_best_thres(code6,name6,init_thres_step):
    times = 0
    status = 0 # residual < 0, status = 0; else status = 1
    thres = 0
    thres_step = init_thres_step

    impervious_pop, benchmark_pop = preprocessing(code6,name6)
    print(impervious_pop,benchmark_pop)
    data_urban_pop = calc_data_urban_pop(name6,1) # 最小buffer的radius不能为0，所以用1来代替
    # 防止无政府poi的地区出现，这些地方单独跑。
    if data_urban_pop == None:
        return 9999,0,0,0,0,0
    # status不变化时，radius按照步长增长；status发生变化，则radius_step转为1/2
    print(data_urban_pop)
    residual = data_urban_pop - benchmark_pop
    # 若是搜索半径为0时，data_urban_pop就大于pop6了，那么直接以最小半径0为最佳阈值
    if residual > 0:
        residual_prop = abs(residual/benchmark_pop) 
        return 0,residual,residual_prop,pop6,urban6,data_urban_pop
    residual_list = []
    thres_list = []
    residual_list.append(residual)
    thres_list.append(thres)

    while True:
        
        times += 1 # 用于计数 

        # 判断radius如何变化
        # 四种情况，连续小于真值，按当前步长增加
        if residual < 0 and status == 0:
            thres += thres_step
        # 特殊情况，防止为0
        elif thres-thres_step == 0 and status == 1:
            thres_step = round(thres_step/2)
            thres -= thres_step
        # 连续大于真值，就按相同倍率减小
        elif residual > 0 and status == 1:
            thres -= thres_step
        # 上次小于，这次大于，则步长减半，半径减小
        elif residual > 0 and status == 0:
            status = 1
            thres_step = round(thres_step/2)
            thres -= thres_step
        # 上次大于于，这次小于，则步长减半，半径增加
        elif residual < 0 and status == 1:
            status = 0
            thres_step = round(thres_step/2)
            thres += thres_step    
        
        data_urban_pop = calc_data_urban_pop(name6,thres)
        residual = data_urban_pop - benchmark_pop
        print(f'round:{times} -=> thres={thres},thres_step={thres_step},residual = {residual}\n')
        residual_list.append(residual)
        thres_list.append(thres)
        
        # 最小的有效buffer即15，或者buffer小于0了
        if thres_step <= 15 or thres < 0 or thres > 2000:
            break

    residual_abs_list = [abs(i) for i in residual_list]
    min_residual = min(residual_abs_list)
    best_indexes = [i for i,x in enumerate(residual_abs_list) if x==min_residual]
    best_thres = min([thres_list[i] for i in best_indexes]) 
    residual_prop = abs(min_residual/benchmark_pop) 

    print(residual_list)
    print(min_residual)
    print(best_thres)

    return best_thres,min_residual,residual_prop,pop6,urban6,data_urban_pop

# %% select final polygon
def copy_polygon_to_result(county_name,best_thres):
    out_path = r'.\\result_folder\\'
    temp_selected_file = f'{county_name}_urban_{best_thres}.shp'
    CopyFeatures_management(temp_selected_file,out_path+temp_selected_file)

# %%  <<<<<<<<<<<<<<<<<<<<<<<<<<<-----运行部分----->>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 获取六普人口和城市化率
df = pd.read_csv('census6_main.csv',encoding = 'gb18030')
df.index = df['code6']

count = 1
start_time = datetime.now()
lst_df = list(df.iterrows())[34:]

for i in lst_df:
    row = i[1]
    code6 = row['code6']
    name = row['城市名']
    pop6 = row['总人口']
    urban6 = row['市人口']
    ratio6 = urban6/pop6

    best_thres,best_residual,residual_prop,pop6,urban6,data_urban_pop = find_best_thres(code6,name,120)

    df.loc[code6,'best_thres'] = best_thres
    df.loc[code6,'best_residual'] = best_residual
    df.loc[code6,'data_urban_pop'] = data_urban_pop
    df.loc[code6,'residual_prop'] = residual_prop

    if best_thres != 0 and best_thres != 9999:
        copy_polygon_to_result(name,best_thres)
    elif best_thres == 0:
        copy_polygon_to_result(name,1)
    elif best_thres == 9999:
        pass

    print(f'{count}//{len(lst_df)},{code6},{name}-->best thres:{best_thres}, --> best residual:{best_residual}.  \n time:{(datetime.now()-start_time).seconds/60} min')
    count += 1

df.to_excel('result_best_thres_37.xlsx')
 
