# %% 
from arcpy import *
import os
from dbfread import DBF
from arcpy.sa.Functions import ZonalStatisticsAsTable

os.chdir(r'E:\workspace\Research_2022_rural_settlement\work_space\partial_processing')
env.overwriteOutput = True
env.workspace = r'E:\workspace\Research_2022_rural_settlement\work_space\partial_processing\original_settlement_province'
features = ListFeatureClasses()
for feature in features:
    prov_name = feature.split('_')[0]
    ori_settlement = f'E:\workspace\Research_2022_rural_settlement\work_space\partial_processing\original_settlement_province\{prov_name}_settlement.shp'
    env.workspace = r'E:\\workspace\\Research_2022_rural_settlement\\work_space\\partial_processing\\temp_workspace\\'+prov_name
    ori_landuse = r"E:\workspace\Research_2022_rural_settlement\work_space\landuse_data\Globeland30\globeland30_2020.tif"

    # 生成buffer
    file_buffer = f'{prov_name}_landuse_buffer.shp'
    Buffer_analysis(ori_settlement,file_buffer,'250 Meters')
    print(f'{prov_name} buffer 生成成功。')

    # zonal as table
    file_zonal = f'{prov_name}_landuse_zonal_table.dbf'
    ZonalStatisticsAsTable(file_buffer,'FID',ori_landuse,file_zonal,statistics_type='SUM')
    print(f'{prov_name} zonal 成功。')

    # join field to ori point
    JoinField_management(ori_settlement,'FID',file_zonal,'FID_','SUM')
    print(f'{prov_name} dem range join 成功。')

    # 计算大致面积
    pixel_area = 30*30
    field_name = 'GLB30'
    AddField_management(ori_settlement,field_name, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    CalculateField_management(ori_settlement, field_name, f"!SUM!*{pixel_area}", "PYTHON_9.3", "")
    DeleteField_management(ori_settlement, ["SUM"])
    print(f'{prov_name} 面积计算成功！')





























