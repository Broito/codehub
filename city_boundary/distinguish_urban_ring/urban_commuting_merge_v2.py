from arcpy import *
from math import *
import numpy as np

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
    commute_d = 1.17*pow(e,1.17*log(core_d))
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

core_shp = r'E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\core\京津冀.shp'
name = '京津冀'
geos = extract_geometry(core_shp)
geos.sort(key = lambda a: a.area, reverse=True) # 按照面积的从大到小排序

belong_id = list(range(len(geos)))
def commuting_merge_single(p_list):
    new_list = p_list[:] 
    for core in new_list[:-1]:
        core_index = new_list.index(core)
        core_id = belong_id[core_index]
        radius = calc_buffer_radius_circle(core.area)
        buffer = core.buffer(radius)
        print(core_id)
        for sub_core in new_list[core_index+1:]:
            overlap = buffer.overlaps(sub_core)
            contain = buffer.contains(sub_core)
            sub_index = new_list.index(sub_core)
            if overlap or contain:
                belong_id[sub_index] = core_id

finished_cores = []
def dissolve_urban(geos,belong_id):
    for i in range(len(geos)):
        print(i)
        same_index = [a for a,x in enumerate(belong_id) if x == i]
        if len(same_index) == 1:
            finished_cores.append(geos[same_index[0]])
        elif len(same_index) > 1:
            merged = geos[same_index[0]]
            for geo_index in same_index[1:]:
                merged = merged.union(geos[geo_index])
            finished_cores.append(merged)

commuting_merge_single(geos)
dissolve_urban(geos,belong_id)

# commuting_merge_iter(geos)
result = r'E:\\workspace\\Research_2022_city_boundary\\commuting_buffer_merge\\' + f'{name}_urban_commuting_merged2.shp'
CopyFeatures_management(finished_cores,result)


































