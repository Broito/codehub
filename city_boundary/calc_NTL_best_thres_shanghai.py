# %%
from arcpy import *
import os
from dbfread import DBF
import pandas as pd
from arcpy.sa.Functions import ExtractByMask, ZonalStatisticsAsTable
from arcpy.sa import SetNull


os.chdir(r'F:\workspace\Research_2022_city_boundary\NTL_thres_calc')
env.workspace = r'F:\workspace\Research_2022_city_boundary\NTL_thres_calc\temp_folder'
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
    ori_county_polygon = r"F:\workspace\Research_2022_city_boundary\data_processing\county_with_census_data.shp"
    county_code6 = county_code6
    global file_selected_county
    file_selected_county = f'{county_name}_polygon.shp'
    MakeFeatureLayer_management(ori_county_polygon, "lyr_counties")
    where_clause = '"code6" = \'{}\''.format(county_code6)
    SelectLayerByAttribute_management("lyr_counties", "NEW_SELECTION",where_clause)
    CopyFeatures_management("lyr_counties", file_selected_county)
    
    # 裁切人口栅格
    ori_pop_raster = r"H:\DataHub\WorldPop_proj\chn_ppp_2010.tif"
    # ori_pop_raster = r"H:\DataHub\Landscan\LandScan Global 2010\lspop2010"
    # ori_pop_raster = r"H:\DataHub\GPWv4_Columbia\gpw_v4_population_count_rev11_2010_30_sec.tif"
    global file_extracted_pop
    file_extracted_pop = f'{county_name}_pop.tif'
    extracted = ExtractByMask(ori_pop_raster,file_selected_county)
    extracted.save(file_extracted_pop)

    # 裁切政府所在地
    ori_gov = r"F:\workspace\Research_2022_city_boundary\data_processing\governments\China_county_gov_total.shp"
    global file_gov
    file_gov = f'{county_name}_gov.shp'
    Clip_analysis(ori_gov,file_selected_county,file_gov)

    # 裁切夜间灯光栅格
    ori_ntl = r"H:\DataHub\Long_NTL\LongNTL_2010.tif"
    global file_ntl
    file_ntl = f'{county_name}_ntl.tif'
    extracted = ExtractByMask(ori_ntl,file_selected_county)
    extracted.save(file_ntl) 

    print(f'{county_name} init success.')  

def calc_data_urban_ratio(county_name,thres):  
    # set_null
    file_city_raster = f'{county_name}_city_ntl_{thres}.tif'
    outSetNull = SetNull(file_ntl, 1, f"VALUE < {thres}")
    outSetNull.save(file_city_raster)

    # raster to polygon
    global file_city_polygon
    file_city_polygon = f'{county_name}_city_ntl_{thres}.shp'
    RasterToPolygon_conversion(file_city_raster,file_city_polygon,"NO_SIMPLIFY")

    # zonal city pop
    data_urban_pop = zonal(file_city_polygon,'gridcode',file_extracted_pop)

    # zonal total pop
    data_total_pop = zonal(file_selected_county,'code6',file_extracted_pop)

    # calc data city ratio
    data_urban_ratio = data_urban_pop/data_total_pop

    print(f'{county_name}-thres = {thres} --> total:{data_total_pop}; urban:{data_urban_pop}; ratio:{data_urban_ratio}')
    return data_total_pop,data_urban_pop,data_urban_ratio

def calc_census6_urban_ratio(county_name):
    census6 = pd.read_csv(r"F:\workspace\Research_2022_city_boundary\data_processing\county_with_census_data.csv",encoding = 'utf8')
    select_city = census6[census6['name6']==county_name]
    urban_ratio6 = float(select_city['uratio6'].values[0])
    pop6 = select_city['pop6'].values[0]
    urban6 = select_city['urban6'].values[0]
    print(f'{county_name}6普总人口为{pop6},城镇人口为{urban6},城镇化率为{urban_ratio6}')
    return pop6,urban6,urban_ratio6

# %%
def find_best_thres(code6,name6,init_thres_step):
    times = 0
    status = 0 # residual > 0, status = 0; else status = 1
    thres = 1
    thres_step = init_thres_step

    preprocessing(code6,name6)
    pop6,urban6,urban_ratio6 = calc_census6_urban_ratio(name6)
    data_total_pop,data_urban_pop,data_urban_ratio = calc_data_urban_ratio(name6,thres)
    # status不变化时，radius按照步长增长；status发生变化，则radius_step转为1/2
    residual = data_urban_ratio-urban_ratio6
    if residual < 0:
        return 1,residual
    residual_list = []
    thres_list = []
    residual_list.append(residual)
    thres_list.append(thres)

    while True:
        
        times += 1 # 用于计数 

        # 判断radius如何变化
        # 四种情况，连续大于真值，按当前步长增加
        if residual > 0 and status == 0:
            thres += thres_step
        # 连续小于真值，就按相同倍率减小
        elif residual < 0 and status == 1:
            thres -= thres_step
        # 上次大于，这次小于，则步长减半减小
        elif residual < 0 and status == 0:
            status = 1
            thres_step = round(thres_step/2)
            thres -= thres_step
        # 上次小于，这次大于，则倍率减半增加
        elif residual > 0 and status == 1:
            status = 0
            thres_step = round(thres_step/2)
            thres += thres_step    
        
        data_total_pop,data_urban_pop,data_urban_ratio = calc_data_urban_ratio(name6,thres)
        residual = data_urban_ratio-urban_ratio6
        print(f'round:{times} -=> thres={thres},thres_step={thres_step},residual = {residual}\n')
        residual_list.append(residual)
        thres_list.append(thres)
        
        if thres_step == 0:
            break

    residual_abs_list = [abs(i) for i in residual_list]
    min_residual = min(residual_abs_list)
    best_index = residual_abs_list.index(min_residual)
    best_thres = thres_list[best_index]
    best_residual =residual_list[best_index]
    print(residual_list)
    print(min_residual)
    print(best_thres)
    print(best_residual)

    return best_thres,best_residual

# %% select final polygon
def copy_polygon_to_result(county_name,best_thres):
    out_path = r'.\\result_folder\\'
    temp_selected_file = f'{county_name}_city_ntl_{best_thres}.shp'
    CopyFeatures_management(temp_selected_file,out_path+temp_selected_file)

# %%
county_name = '衡水市辖区'
code6 = '131100'
best_thres,best_residual = find_best_thres(code6,county_name,5)
copy_polygon_to_result(county_name,best_thres)