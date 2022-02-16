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

os.chdir(r'E:\\workspace\\Research_2022_city_boundary\\distinguish_ring')
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

# %%选择所在省的栅格，但用完该方法后要记得重新设置env.workspace
def select_region(code6):
    prov_code = str(code6)[:2]
    env.workspace = r'I:\DataHub\Landuse_GAIA\Urban and rural'
    tifs = ListRasters()
    for tif in tifs:
        if prov_code == tif[:2]:
            return tif

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
    env.workspace = r'.\temp_workspace'
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
    shrink_radius = 2
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
def get_init_urban_patch(ori_patch,city_name):

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
    file_init_urban_polygon = f'{city_name}_init_urban_polygon.shp'
    Select_analysis(file_dissolved_ori_urban,file_init_urban_polygon,"Id_1 <> 0")

    return file_init_urban_polygon

# %% radius下的斑块扩张，返回扩张后的斑块
def get_buffer_urban_patch(ori_patch,radius):

    # 斑块名字（序号）为去掉后缀的
    patch_name = ori_patch[:-4]

    # 作buffer
    file_buffer = f'{patch_name}_buffer_{radius}.shp'
    Buffer_analysis(ori_patch,file_buffer,f'{radius} Meters')

    # dissolve
    file_dissolved_buffer = f'{patch_name}_dissolve_{radius}.shp'
    Dissolve_management(file_buffer,file_dissolved_buffer)

    # explode
    file_explode_buffer = f'{patch_name}_explode_{radius}.shp'
    MultipartToSinglepart_management(file_dissolved_buffer,file_explode_buffer)

    # 选中存在有政府的buffer斑块
    file_buffer_contain_gov = f'{patch_name}_{radius}_buffer_gov.shp'
    MakeFeatureLayer_management(file_explode_buffer, "lyr_buffer")
    MakeFeatureLayer_management(file_gov, "lyr_gov")
    SelectLayerByLocation_management("lyr_buffer", 'intersect',"lyr_gov",'500 Meters')
    CopyFeatures_management("lyr_buffer", file_buffer_contain_gov)

    # 选中未buffer的原始斑块，代表在radius下，这些斑块属于urban area
    file_patch_urban = f'{patch_name}_urban_{radius}.shp'
    Intersect_analysis([ori_patch,file_buffer_contain_gov],file_patch_urban)
    
    return file_patch_urban

# %% 拆分地级市单元中的所有斑块，并分辨出主城区
def single_shp_to_multi(multi_shp,city_name):

    # 提取出几何对象并按照面积排序
    fields = ['SHAPE@']
    patch_list = []
    cur = da.SearchCursor(multi_shp,fields)
    for row in cur:
        patch_list.append((row[0]))
    del cur
    patch_list.sort(key = lambda a: a.area, reverse=True) # 按照面积的从大到小排序
    main_patch_geo = patch_list[0]
    indep_patch_geos = []
    # 将斑块都拿出来看看是否有与buffer重合的
    for patch in patch_list[1:]:
        geometry = patch
        # print(main_patch_buffer.overlaps(geometry))
        print(main_patch_geo.distanceTo(geometry))
        if main_patch_geo.distanceTo(geometry) <= 2000:
            main_patch_geo = main_patch_geo.union(geometry)
        else:
            indep_patch_geos.append(geometry)
    # 将主城区的几何对象导出为独立要素
    main_patch = f'./init_patch_2km/{city_name}_init_main_patch.shp'
    CopyFeatures_management(main_patch_geo,main_patch)
    # 将独立斑块的几何对象全部单独新建要素类
    n = 1
    for p_indep in indep_patch_geos:
        indep_name = f'./init_patch_2km/{city_name}_init_partial_patch_{n}.shp'
        CopyFeatures_management(p_indep,indep_name)
        n += 1


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
    combo_ring = mean_pop_ring*mean_ntl_ring

    return mean_pop_ring,mean_ntl_ring,combo_ring

def get_threshold(city_name,certain_urban,radius):

    file_patch_urban = certain_urban

    # rural_patch = total patch - urban_patch
    file_patch_rural = f'{city_name}_rural_{radius}.shp'
    Erase_analysis(file_urban_polygon,file_patch_urban,file_patch_rural)

    # merge urban斑块和rural斑块，用来下一步直接zonal求mean 
    file_merged_urban = f'{city_name}_merged_urban_{radius}.shp'
    file_merged_rural = f'{city_name}_merged_rural_{radius}.shp'
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

    return threshold_pop,threshold_ntl

def strategy_loose(threshold_pop,threshold_ntl,current_pop,current_ntl):    
    if current_pop < threshold_pop and current_ntl < threshold_ntl:
        return False
    else:
        return True

# %% select final polygon
def copy_polygon_to_result(city_name,selected_file,thres,strategy):
    out_path = f'.\\result_folder\\{strategy}\\'
    out_selected_file = f'{city_name}_urban_{strategy}_{thres}.shp'
    CopyFeatures_management(selected_file,out_path+out_selected_file)

# %%  <<<<<<<<<<<<<<<<<<<<<<<<<<<-----运行部分----->>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 获取六普人口和城市化率
df = pd.read_csv('七普地级市.csv',encoding = 'gb18030')
df.index = df['prefcodeF7']

# prefcode7 = 4408
# name = df.loc[prefcode7,'Name']

# total_ori_patch = preprocessing(prefcode7,name) # 返回该地级市内的所有斑块
# total_init_gov_urban = get_init_urban_patch(total_ori_patch,name) # 返回政府所在地的所有斑块
# single_shp_to_multi(total_init_gov_urban,name)

code7_list = [1101,1201,1304,1402,1506,2203,3301,3101,3204,3302,3301,3408,3701,4113,4201,4211,4301,4401,4403,4408,4503,5116,5202]
for prefcode7 in code7_list:
    name = df.loc[prefcode7,'Name']

    total_ori_patch = preprocessing(prefcode7,name) # 返回该地级市内的所有斑块
    total_init_gov_urban = get_init_urban_patch(total_ori_patch,name) # 返回政府所在地的所有斑块
    single_shp_to_multi(total_init_gov_urban,name)
    print(name)



