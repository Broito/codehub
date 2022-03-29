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



os.chdir(r'E:\workspace\Research_2022_city_boundary\distinguish_ring\result_folder')
env.workspace = r'E:\workspace\Research_2022_city_boundary\commuting_buffer_merge'
env.overwriteOutput = True

core_shp = r'E:\workspace\Research_2022_city_boundary\distinguish_ring\result_folder\苏州市_urban.shp'
name = '苏州市'
geos = extract_geometry(core_shp)
buffers = []
for geo in geos:
    # radius = calc_buffer_radius_rectangle(geo.area)
    radius = calc_buffer_radius_circle(geo.area)
    buffer = geo.buffer(radius)
    buffers.append(buffer)

file_buffer_shp = f'{name}_buffer.shp'
CopyFeatures_management(buffers,file_buffer_shp)

# dissolve
file_dissolved_buffer = f'{name}_dissolved.shp'
Dissolve_management(file_buffer_shp,file_dissolved_buffer)

# explode
file_explode_buffer = f'{name}_exploded.shp'
MultipartToSinglepart_management(file_dissolved_buffer,file_explode_buffer)

# add id to exploded polygon
CalculateField_management(file_explode_buffer,'Id','!FID!')

# spatial join
file_spatial_join = f'{name}_spatial_join.shp'
SpatialJoin_analysis(core_shp, file_explode_buffer, file_spatial_join)

# 按照explode buffer来做dissolve
file_final_dissolve = f'{name}_urban_commuting_merged.shp'
Dissolve_management(file_spatial_join,file_final_dissolve,'Id_1')






