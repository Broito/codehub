from arcpy import *
import os

def batch_add_fields(shp,field_name_list,field_type_list):
    for field_name,field_type in zip(field_name_list,field_type_list):
        AddField_management(shp,field_name,field_type)

def LU_point_to_30m_grid(x,y,d):
    array = Array()
    point1 = Point(x,y)
    point2 = Point(x,y-d)
    point3 = Point(x+d,y-d)
    point4 = Point(x+d,y)
    array.add(point1)
    array.add(point2)
    array.add(point3)
    array.add(point4)
    polygon = Polygon(array)
    return polygon     

os.chdir(r'E:\workspace\Research_2022_rural_settlement\work_space\generate_grid_test')
env.workspace = r'E:\workspace\Research_2022_rural_settlement\work_space\generate_grid_test'
env.overwriteOutput = True

rural_settlements = 'rural_example.shp'
grid_500m = 'grid_500m.shp'
grid_30m = 'grid_30m.shp'
CreateFeatureclass_management('.', grid_500m,'POLYGON', spatial_reference = 'rural_example.prj')
CreateFeatureclass_management('.', grid_30m,'POLYGON', spatial_reference = 'rural_example.prj')

# 获取村落点所有的字段
# desc = Describe(rural_settlements)
# fields = [i.name for i in desc.fields] # ['FID',  'Shape', '省份', '城市代', '城市', '区县代', '区县', '乡镇街', '乡镇_1', '居委会', '城乡分', '居委_1', '地址', 'lng_wgs84', 'lat_wgs84']

# 给新建的网格增加与村落点相同的字段
append_fields = ['RS_FID', '省', '市代码', '市', '区县码', '区县', '街道', '村', 'UR_code','address','category']
append_fields_type = ['SHORT','TEXT','TEXT','TEXT','TEXT','TEXT','TEXT','TEXT','TEXT','TEXT','SHORT']
batch_add_fields(grid_500m,append_fields,append_fields_type)
batch_add_fields(grid_30m,append_fields,append_fields_type)

# 循环创造网格
grid_500m_field = ['SHAPE@','RS_FID', '省', '市代码', '市', '区县码', '区县', '街道', '村', 'UR_code','address']
grid_30m_field = ['SHAPE@','RS_FID', '省', '市代码', '市', '区县码', '区县', '街道', '村', 'UR_code','address']
point_field = ['SHAPE@XY','FID','省份', '城市代', '城市', '区县代', '区县', '乡镇_1', '居委_1', '城乡分', '地址']
cur_point = da.SearchCursor(rural_settlements,point_field)
cur_500m = da.InsertCursor(grid_500m,grid_500m_field)
cur_30m = da.InsertCursor(grid_30m,grid_30m_field)

# 生成500m格网
for ur_row in list(cur_point):
    point_x,point_y = ur_row[0]

    # 生成500m网格
    polygon500 = LU_point_to_30m_grid(point_x-250,point_y+250,500)
    cur_500m.insertRow([polygon500,str(ur_row[1]),ur_row[2],str(ur_row[3]),ur_row[4],str(ur_row[5]),ur_row[6],ur_row[7],ur_row[8],str(ur_row[9]),ur_row[10]])

    # 生成30m网格
    ori_LU_x = point_x-30*8
    ori_LU_y = point_y+30*8
    for y in range(16):
        for x in range(16):
            LU_x = ori_LU_x + 30*x
            LU_y = ori_LU_y - 30*y
            polygon30 = LU_point_to_30m_grid(LU_x,LU_y,30)
            cur_30m.insertRow([polygon30,str(ur_row[1]),ur_row[2],str(ur_row[3]),ur_row[4],str(ur_row[5]),ur_row[6],ur_row[7],ur_row[8],str(ur_row[9]),ur_row[10]])

del cur_30m











del cur_point
del cur_500m
























