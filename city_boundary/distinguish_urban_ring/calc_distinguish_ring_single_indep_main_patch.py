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
from datetime import datetime 

os.chdir(r'E:\\workspace\\Research_2022_city_boundary\\distinguish_ring')
header_workspace = r'E:/workspace/Research_2022_city_boundary/distinguish_ring/temp_workspace/'
env.overwriteOutput = True

# <------------------------ 小工具-------------------------->
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

# %%选择所在省的栅格，但用完该方法后要记得重新设置env.workspace
def select_region(code6):
    prov_code = str(code6)[:2]
    env.workspace = r'I:\DataHub\Landuse_GAIA\Urban and rural'
    tifs = ListRasters()
    for tif in tifs:
        if prov_code == tif[:2]:
            return tif

# 从shp里提取geometry，返回geometry列表
def extract_geometry(shp):
    geo_list = []
    cur = da.SearchCursor(shp,['SHAPE@'])
    for row in cur:
        geo_list.append(row[0])
    del cur
    return geo_list

def select_by_location(target_file,ref_file,output_file):
    # 选中存在有政府的buffer斑块
    MakeFeatureLayer_management(target_file, "lyr_target")
    MakeFeatureLayer_management(ref_file, "lyr_ref")
    SelectLayerByLocation_management("lyr_target", 'intersect',"lyr_ref")
    CopyFeatures_management("lyr_target", output_file)

def select_by_attribute(target_file,where_clause,output_file):
    MakeFeatureLayer_management(target_file, "lyr_target")
    SelectLayerByAttribute_management("lyr_target", "NEW_SELECTION",where_clause)
    CopyFeatures_management("lyr_target", output_file)

# 判别策略选择宽松原则
def strategy_loose(threshold_pop,threshold_ntl,current_pop,current_ntl):    
    if current_pop <= threshold_pop and current_ntl <= threshold_ntl:
        return False
    else:
        return True

def copy_polygon_to_result(city_code,city_name,selected_file):
    out_path = f'.\\result_folder\\'
    out_selected_file = f'{city_code}_{city_name}_urban.shp'
    CopyFeatures_management(selected_file,out_path+out_selected_file)

# <-----------------------------运行模块-------------------------------->
# %% 
def preprocessing(city_code,city_name):

    # 选择需要进行操作的地区矢量
    ori_city_polygon = r".\七普地级区划.shp"
    city_name = city_name
    city_code = city_code
    file_selected_city = f'{city_name}_polygon.shp'
    MakeFeatureLayer_management(ori_city_polygon, "lyr_cities")
    where_clause = f'"prefcodeF7" = {city_code}'
    SelectLayerByAttribute_management("lyr_cities", "NEW_SELECTION",where_clause)
    CopyFeatures_management("lyr_cities", file_selected_city)
    
    # 选择所在省份栅格
    tif_path = r'I:\\DataHub\\Landuse_GAIA\\Urban and rural\\'
    ori_landuse = tif_path + select_region(city_code)
    env.workspace = f'./temp_workspace/{city_code}_{city_name}'
    # 裁切城市栅格
    file_landuse_city = f'{city_name}_landuse.tif'
    extracted = ExtractByMask(ori_landuse,file_selected_city)
    extracted.save(file_landuse_city)

    # 裁切人口栅格
    ori_pop_raster = r"I:\DataHub\WorldPop_proj\chn_ppp_2010.tif"
    global file_extracted_pop
    file_extracted_pop = f'{city_name}_pop.tif'
    extracted = ExtractByMask(ori_pop_raster,file_selected_city)
    extracted.save(file_extracted_pop)

    # 裁切夜间灯光栅格
    ori_ntl = r"I:\DataHub\Long_NTL\LongNTL_2010.tif"
    global file_ntl
    file_ntl = f'{city_name}_ntl.tif'
    extracted = ExtractByMask(ori_ntl,file_selected_city)
    extracted.save(file_ntl) 

    # 裁切政府所在地
    ori_gov = r".\governments\2021基础数据_区县级政府.shp"
    global file_gov
    file_gov = f'{city_name}_gov.shp'
    Clip_analysis(ori_gov,file_selected_city,file_gov)

    # 提取像元值大于7的作为2010年不透水面像元
    file_con = f'{city_name}_landuse_urban.tif'
    conned = Con(file_landuse_city,1,"","VALUE > 7")
    conned.save(file_con)

    # 先收缩后膨胀
    shrink_radius = 1
    file_shrink = f'{city_name}_shrink{shrink_radius}_urban.tif'
    layer_shrink = Shrink(file_con,shrink_radius,1)
    layer_shrink.save(file_shrink)

    file_expand = f'{city_name}_expand{shrink_radius}_urban.tif'
    layer_expand = Expand(file_shrink,shrink_radius,1)
    layer_expand.save(file_expand)
    
    # 转为矢量
    file_urban_polygon = f'{city_name}_ori_urban_polygon.shp'
    RasterToPolygon_conversion(file_expand, file_urban_polygon, "NO_SIMPLIFY")

    # 转坐标系统
    file_urban_polygon_proj = f'{city_name}_ori_urban_polygon_proj.shp'
    sr = arcpy.SpatialReference("Asia North Albers Equal Area Conic")
    Project_management(file_urban_polygon,file_urban_polygon_proj,sr)

    return file_urban_polygon_proj

# %% 选择出初始的政府斑块
def get_init_gov_patch(ori_patch,city_name):

    # 作政府点的500mbuffer
    file_gov_buffer = f'{city_name}_gov_buffer.shp'
    Buffer_analysis(file_gov,file_gov_buffer,'500 Meters')

    # 要知道每个政府点都属于哪个斑块，将斑块名字赋予政府buffer
    file_gov_buffer_joined = f'{city_name}_gov_buffer_joined_patch.shp'
    SpatialJoin_analysis(file_gov_buffer,ori_patch,file_gov_buffer_joined,'JOIN_ONE_TO_ONE')

    # 将相同斑块的政府buffer 合并为同一个要素
    file_gov_buffer_dissolved = f'{city_name}_gov_buffer_dissolved.shp'
    Dissolve_management(file_gov_buffer_joined,file_gov_buffer_dissolved,'Id')

    # spatial join 将buffer的名字赋给相交的斑块
    file_joined_ori_urban = f'{city_name}_joined_ori_urban.shp'
    SpatialJoin_analysis(ori_patch,file_gov_buffer_dissolved,file_joined_ori_urban,'JOIN_ONE_TO_ONE')

    # 按照buffer id 对斑块进行dissolve
    file_dissolved_ori_urban = f'{city_name}_dissolved_ori_urban.shp'
    Dissolve_management(file_joined_ori_urban,file_dissolved_ori_urban,'Id_1')

    # 选择出Id_1不是0的区域，即政府所在斑块
    file_init_urban_polygon = f'{city_name}_init_gov_polygon.shp'
    Select_analysis(file_dissolved_ori_urban,file_init_urban_polygon,"Id_1 <> 0")

    return file_init_urban_polygon

# %% 选出初始的最大斑块
def get_init_big_patch(ori_patch,city_name,city_code):
    biggest_patch_list = []

    # 选择出该地级市的所有区县单元
    ref_china_county = r'./七普县级区划.shp'
    file_selected_counties = f'{city_name}_counties_polygon.shp'
    where_clause = f'"prefcode" = {city_code}'
    select_by_attribute(ref_china_county,where_clause,file_selected_counties)

    # 要知道每个斑块属于哪个区县，同时进行切割
    file_ori_patch_intersect_county = f'{city_name}_patch_intersect_county.shp'
    Intersect_analysis([ori_patch,file_selected_counties],file_ori_patch_intersect_county)

    # 挑出每个区县里最大的斑块
    fields = ['xian']
    cur = da.SearchCursor(file_selected_counties,fields)
    for xian in cur:
        name = xian[0]
        file_xian_patch = f'{city_name}_{name}_patch.shp'
        select_by_attribute(file_ori_patch_intersect_county,f'"xian" = \'{name}\'',file_xian_patch)
        polygons = extract_geometry(file_xian_patch)
        polygons.sort(key = lambda a: a.area, reverse=True) # 按从大到小排序斑块
        biggest_patch_list.append(polygons[0])
    del cur

    file_init_big_patch = f'{city_name}_init_big_polygon.shp'
    CopyFeatures_management(biggest_patch_list,file_init_big_patch)

    return file_init_big_patch
        
# %% 合并政府斑块和最大斑块
def get_init_urban_patch(ori_patch,city_name,city_code):

    ori_gov_shp = get_init_gov_patch(ori_patch,city_name)
    ori_big_shp = get_init_big_patch(ori_patch,city_name,city_code)

    file_merge_init_patch = f'{city_name}_init_urban_merged.shp'
    Merge_management([ori_big_shp,ori_gov_shp],file_merge_init_patch)

    file_dissolved_init_patch = f'{city_name}_init_urban_dissovled.shp'
    Dissolve_management(file_merge_init_patch,file_dissolved_init_patch)

    file_explode_init_patch = f'{city_name}_init_urban_polygon.shp'
    MultipartToSinglepart_management(file_dissolved_init_patch,file_explode_init_patch)

    return file_explode_init_patch

# %% 合并2km以内的初始版块，并按从大到小排序
def merge_and_sort_init_patches(multi_shp,city_name):
    # 提取出来几何对象
    patch_list = extract_geometry(multi_shp)
    
    def proximity_merge(p_list):
        new_list = p_list[:] # 复制一个用于修改
        for p_index in range(len(p_list)):
            for p_ref_index in range(len(p_list)):
                dis = new_list[p_index].distanceTo(new_list[p_ref_index])
                if  dis > 0 and dis < 2000:
                    new_list[p_index] = new_list[p_index].union(new_list[p_ref_index])
                    new_list.remove(new_list[p_ref_index])
                    return proximity_merge(new_list)
        return new_list
    
    result_polygons = proximity_merge(patch_list)
    result_polygons.sort(key = lambda a: a.area, reverse=True) # 按照面积的从大到小排序
    result_shp = []

    # 将独立斑块的几何对象全部单独新建要素类
    n = 1
    for p_indep in result_polygons:
        indep_name = f'{city_name}_init_partial_patch_{n}.shp'
        CopyFeatures_management(p_indep,indep_name)
        result_shp.append(indep_name)
        n += 1

    return result_polygons,result_shp

# %% radius下的斑块扩张，返回扩张后的斑块
def get_buffer_urban_patch(total_patch,init_urban_patch,radius):

    # 斑块名字（序号）为去掉后缀的,这里指初始斑块
    patch_name = init_urban_patch[:-4]

    # 作buffer
    file_buffer = f'{patch_name}_buffer_{radius}.shp'
    Buffer_analysis(total_patch,file_buffer,f'{radius} Meters')

    # dissolve
    file_dissolved_buffer = f'{patch_name}_dissolve_{radius}.shp'
    Dissolve_management(file_buffer,file_dissolved_buffer)

    # explode
    file_explode_buffer = f'{patch_name}_explode_{radius}.shp'
    MultipartToSinglepart_management(file_dissolved_buffer,file_explode_buffer)

    # 选中存在有政府的buffer斑块
    file_buffer_contain_init_urban = f'{patch_name}_{radius}_buffer_init_urban.shp'
    MakeFeatureLayer_management(file_explode_buffer, "lyr_buffer")
    MakeFeatureLayer_management(init_urban_patch, "lyr_init_urban")
    SelectLayerByLocation_management("lyr_buffer", 'intersect',"lyr_init_urban")
    CopyFeatures_management("lyr_buffer", file_buffer_contain_init_urban)

    # 选中未buffer的原始斑块，代表在radius下，这些斑块属于urban area
    file_patch_urban = f'{patch_name}_urban_{radius}.shp'
    Intersect_analysis([total_patch,file_buffer_contain_init_urban],file_patch_urban)
    
    return file_patch_urban

# %%
# 获得当前环带的三个判别值
def get_ring_value(city_name,certain_urban,new_urban_patch,radius):

    # 获取当前环带矢量
    file_ring_patch = f'{city_name}_ring_{radius}.shp'
    Erase_analysis(new_urban_patch,certain_urban,file_ring_patch)

    # merge 环带斑块
    file_merged_ring = f'{city_name}_merged_ring_{radius}.shp'
    Dissolve_management(file_ring_patch,file_merged_ring)

    # 计算三个判别值
    mean_pop_ring = zonal(file_merged_ring,'Id',file_extracted_pop)
    mean_ntl_ring = zonal(file_merged_ring,'Id',file_ntl)

    # 防止None出现
    if mean_pop_ring == None:
        mean_pop_ring = 0
    if mean_ntl_ring == None:
        mean_ntl_ring = 0

    return mean_pop_ring,mean_ntl_ring

# %%
# 获取下一圈层对应的阈值
def get_threshold(city_name,current_total_patch,certain_urban,radius):

    file_patch_urban = certain_urban

    # rural_patch = total patch - urban_patch
    file_patch_rural = f'{city_name}_rural_{radius}.shp'
    Erase_analysis(current_total_patch,file_patch_urban,file_patch_rural)

    # merge urban斑块和rural斑块，用来下一步直接zonal求mean 
    file_merged_urban = f'{city_name}_merged_urban_{radius}.shp'
    file_merged_rural = f'{city_name}_merged_rural_{radius}.shp'
    Dissolve_management(file_patch_urban,file_merged_urban)
    Dissolve_management(file_patch_rural,file_merged_rural)

    # zonal生成各斑块上的人口
    mean_pop_urban = zonal(file_merged_urban,'Id',file_extracted_pop)
    mean_pop_rural = zonal(file_merged_rural,'Id',file_extracted_pop)
    if mean_pop_urban == None:
        mean_pop_urban = 0
    if mean_pop_rural == None:
        mean_pop_rural = 0
    
    # zonal生成各斑块上的夜间灯光
    mean_ntl_urban = zonal(file_merged_urban,'Id',file_ntl)
    mean_ntl_rural = zonal(file_merged_rural,'Id',file_ntl)
    if mean_ntl_urban == None:
        mean_ntl_urban = 0
    if mean_ntl_rural == None:
        mean_ntl_rural = 0

    # 计算三个指标
    threshold_pop = math.sqrt(mean_pop_urban*mean_pop_rural)
    threshold_ntl = math.sqrt(mean_ntl_urban*mean_ntl_rural)

    return threshold_pop,threshold_ntl


# %% 计算当前初始斑块所扩张形成的urban
# patch_name 即urban初始斑块
def partial_calc(patch_name):
    name_list = patch_name[:-4].split('_')
    name_index = name_list[-1]
    name_city = name_list[0]
    name = name_city+'_'+name_index

    # 获取当前城市斑块涉及的行政边界
    current_admin_extent = f'{name}_current_admin_extent_{name_index}.shp'
    ref_china_county = r'./七普县级区划.shp'
    select_by_location(ref_china_county,patch_name,current_admin_extent)

    # 获取当前范围的所有斑块（用于限定后面斑块扩张范围和定义rural）
    # 当前用于计算的所有斑块 = 区划内所有斑块 - 全局已确定的urban斑块 + 该区划内初始urban斑块
    # 区划内所有斑块
    within_extent_total_patch = f'{name}_within_extent_total_patch_{name_index}.shp'
    select_by_location(total_ori_patch,current_admin_extent,within_extent_total_patch)
    # 去掉全局已确定的urban斑块
    within_extent_non_urban_patch = f'{name}_within_extent_non_urban_patch_{name_index}.shp'
    Erase_analysis(within_extent_total_patch,current_urban_polygon,within_extent_non_urban_patch)
    # 再加上该区划内初始urban斑块，得到最终用于计算的所有斑块
    current_total_patch = f'{name}_current_total_patch_{name_index}.shp'
    Merge_management([within_extent_non_urban_patch,patch_name],current_total_patch)

    # 开始计算urban范围
    current_urban_patch = patch_name # 最新城市范围，初始化为初始斑块
    threshold_pop,threshold_ntl = get_threshold(name,current_total_patch,current_urban_patch,1)

    # setup variable
    times = 0
    step = 30
    radius = 30

    while True:
        times += 1
        # 如果此时阈值有一个变成了0（rural区域变成0了）或者radius太长了，直到间隔500m（radius = 250m）
        if threshold_pop == 0 or threshold_ntl ==0 or radius >= 250:
            final_urban = current_urban_patch
            break
        new_urban_patch = get_buffer_urban_patch(current_total_patch,patch_name,radius)
        current_pop,current_ntl = get_ring_value(name,current_urban_patch,new_urban_patch,radius)
        log.write(f'round:{times} -=> radius={radius},\n\t thres:{threshold_pop},{threshold_ntl} \n\t current:{current_pop},{current_ntl}\n')
        # 如果此圈层没有要素，那么继续下一圈层
        if current_pop == 0 and current_ntl == 0:
            radius += step
            continue
        decide = strategy_loose(threshold_pop, threshold_ntl, current_pop, current_ntl)
        if decide:
            current_urban_patch = new_urban_patch
            threshold_pop,threshold_ntl = get_threshold(name,current_total_patch,current_urban_patch,radius)
            radius += step
            continue
        else:
            final_urban = current_urban_patch
            break
    
    return final_urban

# %% 将单个斑块扩张后的结果合并至总的结果
def merge_partial_to_total(partial_name,total_result_name):

    # 先将分步结果merge到总结果
    merged_total = partial_name[:-4]+f'_merged_total.shp'
    Merge_management([partial_name,total_result_name],merged_total)

    # 再dissolve总结果为一个geometry
    dissolved_total = partial_name[:-4]+f'_dissolved_total.shp'
    Dissolve_management(merged_total,dissolved_total)

    return dissolved_total

# %%  <<<<<<<<<<<<<<<<<<<<<<<<<<<-----运行部分----->>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 获取六普人口和城市化率
df = pd.read_csv('七普地级市.csv',encoding = 'gb18030')
df.index = df['prefcodeF7']

start_time = datetime.now()

pref_list = list(df.loc[:,'prefcodeF7'])
run_list = pref_list[:]

for city_code in run_list:

    name = df.loc[city_code,'Name']
    round = pref_list.index(city_code)+1

    # 每个城市放在一个文件夹里
    os.mkdir(f'./temp_workspace/{city_code}_{name}')
    env.workspace = header_workspace+f'{city_code}_{name}'

    # 日志记录
    log = open('E:\workspace\Research_2022_city_boundary\distinguish_ring\log.txt','a')
    log.write(f'------------>>>>No.{round},{city_code},{name}\n')
    print(f'------------>>>>No.{round},{city_code},{name}\n')

    # 预处理
    total_ori_patch = preprocessing(city_code,name) # 返回该地级市内的所有斑块
    total_init_urban = get_init_urban_patch(total_ori_patch,name,city_code) # 返回政府所在地的所有斑块
    ori_init_urban_patch_geometry,ori_init_urban_shps = merge_and_sort_init_patches(total_init_urban,name) # 返回按面积排序的原始城区geometry列表

    # 当前城市斑块（不断更新，直到最终版）
    current_urban_polygon =  total_init_urban

    # 计算第一块扩张结果
    patch_sprawl_result = partial_calc(ori_init_urban_shps[0])
    # 将第1块扩张结果汇总至 current_urban_polygon 最新总斑块
    current_urban_polygon = merge_partial_to_total(patch_sprawl_result,current_urban_polygon)
    # 已建成urban的geometry（单个）
    finished_geometry = extract_geometry(current_urban_polygon)[0]

    #循环每一个初始斑块，开始扩张
    for patch_shp,patch_geo in zip(ori_init_urban_shps[1:],ori_init_urban_patch_geometry[1:]):
        # 判断当前初始斑块是否已经被现有城区吞并    
        if patch_geo.overlaps(finished_geometry):
            continue
        #计算得到第n块的扩张结果
        patch_sprawl_result = partial_calc(patch_shp) 
        # 将第n块扩张结果汇总至 current_urban_polygon 最新总斑块
        current_urban_polygon = merge_partial_to_total(patch_sprawl_result,current_urban_polygon)
        finished_geometry = extract_geometry(current_urban_polygon)[0]
        log.write(f'>>>{patch_shp}_finished')
        print(f'>>>{patch_shp}_finished')
        
    print(current_urban_polygon)
    copy_polygon_to_result(city_code,name,current_urban_polygon)

    print(f'==========>{round}//{len(pref_list)},{city_code},{name}  \n time:{(datetime.now()-start_time).seconds/60} min\n\n')
    log.write(f'==========>{round}//{len(pref_list)},{city_code},{name}  \n time:{(datetime.now()-start_time).seconds/60} min\n\n')
    log.close()










