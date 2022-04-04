from arcpy import *
from math import *

def calc_buffer_radius_circle(core_area):
    core_area = core_area/1000000
    core_r = sqrt(core_area/pi)
    commute_area = pow(core_area,1.17)
    commute_r = sqrt(commute_area/pi)
    radius = commute_r - core_r
    radius = radius*1000
    return radius

def calc_buffer_radius_rectangle(core_area):
    core_area = core_area/1000000
    core_d = sqrt(core_area)
    commute_d = 1.17*pow(math.e,1.17*log(core_d))
    radius = (commute_d - core_d)/2
    radius = radius*1000
    return radius


# 从shp里提取geometry，返回geometry列表
def extract_geometry(shp):
    geo_list = []
    cur = da.SearchCursor(shp,['SHAPE@'])
    for row in cur:
        geo_list.append(row[0])
    del cur
    return geo_list



os.chdir(r'E:\workspace\Research_2022_city_boundary\commuting_buffer_merge')
env.workspace = r'E:\workspace\Research_2022_city_boundary\commuting_buffer_merge'
env.overwriteOutput = True

core_shp = r'E:\workspace\Research_2022_city_boundary\distinguish_ring\result_folder\China_urban_2018_长三角京津冀.shp'
name = '长三角'
geos = extract_geometry(core_shp)
geos.sort(key = lambda a: a.area, reverse=True) # 按照面积的从大到小排序

finished_cores = []

def commuting_merge(p_list):
    new_list = p_list[:] # 复制一个用于修改
    for p_index in range(len(p_list)):
        for p_ref_index in range(len(p_list)):
            core1 = new_list[p_index]
            radius = calc_buffer_radius_circle(core1.area)
            buffer = new_list[p_index].buffer(radius)
            core2 = new_list[p_ref_index]
            overlap = buffer.overlaps(core2)
            if_self = core1.equals(core2)
            if  if_self == False and overlap:
                print(f'{p_index}合并了{p_ref_index}')
                if p_index != 0: # 若不是排首位的core开始合并，那么说明前面的core已经合并过了，加入已完成
                    finished_core = [i for i in new_list[:p_index]]
                    finished_cores += finished_core
                    print(f'{finished_core}已完成')
                new_list[p_index] = new_list[p_index].union(new_list[p_ref_index])
                new_list.remove(new_list[p_ref_index])
                new_list = new_list[p_index:]
                print(f'新的列表长度为是{len(new_list)}')
                return commuting_merge(new_list)
    # return new_list
    print('结束啦！')
    
commuting_merge(geos)
result = r'E:\\workspace\\Research_2022_city_boundary\\distinguish_ring\\result_one\\' + f'{name}_urban_commuting_merged.shp'
# # CopyFeatures_management(file_final_dissolve,result)





























# print('[1] generate buffer')
# for geo in geos:
#     # radius = calc_buffer_radius_rectangle(geo.area)
#     radius = calc_buffer_radius_circle(geo.area)
#     buffer = geo.buffer(radius)
#     buffers.append(buffer)

# file_buffer_shp = f'{name}_buffer.shp'
# CopyFeatures_management(buffers,file_buffer_shp)

# print('[2] dissolve buffer')
# # dissolve
# file_dissolved_buffer = f'{name}_dissolved.shp'
# Dissolve_management(file_buffer_shp,file_dissolved_buffer)

# print('[3] explode buffer')
# # explode
# file_explode_buffer = f'{name}_exploded.shp'
# MultipartToSinglepart_management(file_dissolved_buffer,file_explode_buffer)

# # add id to exploded polygon
# CalculateField_management(file_explode_buffer,'Id','!FID!')

# print('[4] spatial join')
# # spatial join
# file_spatial_join = f'{name}_spatial_join.shp'
# SpatialJoin_analysis(core_shp, file_explode_buffer, file_spatial_join)

# print('[5] 按照explode buffer来做dissolve')
# # 按照explode buffer来做dissolve
# file_final_dissolve = f'{name}_urban_commuting_merged.shp'
# Dissolve_management(file_spatial_join,file_final_dissolve,'Id_1')

# # result = r'E:\\workspace\\Research_2022_city_boundary\\distinguish_ring\\result_one\\' + f'{name}_urban_commuting_merged.shp'
# # CopyFeatures_management(file_final_dissolve,result)
# print('---->>>>>>>>> success! ')






