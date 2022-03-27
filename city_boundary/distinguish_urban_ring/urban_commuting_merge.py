from arcpy import *
from math import *

def calc_buffer_radius_circle(core_area):
    core_r = sqrt(core_area/pi)
    commute_area = pow(core_area,1.17)
    commute_r = sqrt(commute_area/pi)
    radius = commute_r - core_r
    return radius

def calc_buffer_radius_rectangle(core_area):
    core_d = sqrt(core_area)
    commute_d = 1.17*pow(math.e,1.17*log(core_d))
    radius = (commute_d - core_d)/2
    return radius

# 存疑：为什么不是这样
# def calc_buffer_radius_rectangle(core_area):
#     core_r = sqrt(core_area)/2
#     commute_area = pow(core_area,1.17)
#     commute_r = sqrt(commute_area)/2
#     radius = commute_r - core_r
#     return commute_d
# 从shp里提取geometry，返回geometry列表
def extract_geometry(shp):
    geo_list = []
    cur = da.SearchCursor(shp,['SHAPE@'])
    for row in cur:
        geo_list.append(row[0])
    del cur
    return geo_list

def merge_buffer(p_list):
    new_list = p_list[:] # 复制一个用于修改
    for p_index in range(len(p_list)):
        for p_ref_index in range(len(p_list)):
            polygon1 = new_list[p_index]
            polygon2 = new_list[p_ref_index]
            is_overlap = polygon1.overlaps(polygon2)
            if_self = polygon1.equals(polygon2)
            if if_self == False and is_overlap:
                new_list[p_index] = new_list[p_index].union(new_list[p_ref_index])
                new_list.remove(new_list[p_ref_index])
                return merge_buffer()



def proximity_merge(p_list):
    new_list = p_list[:] # 复制一个用于修改
    for p_index in range(len(p_list)):
        for p_ref_index in range(len(p_list)):
            polygon1 = new_list[p_index]
            polygon2 = new_list[p_ref_index]
            dis = polygon1.distanceTo(polygon2)
            if_self = polygon1.equals(polygon2)
            if  if_self == False and dis < 2000:
                new_list[p_index] = new_list[p_index].union(new_list[p_ref_index])
                new_list.remove(new_list[p_ref_index])
                return proximity_merge(new_list)
    return new_list

os.chdir(r'E:\workspace\Research_2022_city_boundary\distinguish_ring\result_folder')
env.workspace = r'E:\workspace\Research_2022_city_boundary\commuting_buffer_merge'

core_shp = r'E:\workspace\Research_2022_city_boundary\distinguish_ring\result_folder\苏州市_urban.shp'
geos = extract_geometry(core_shp)
buffers = []
for geo in geos:
    # radius = calc_buffer_radius_rectangle(geo.area)
    radius = calc_buffer_radius_circle(geo.area)
    buffer = geo.buffer(radius)
    buffers.append(buffer)






