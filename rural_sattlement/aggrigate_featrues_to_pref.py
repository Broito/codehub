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
    # settlement_shp = f'.\\original_settlement_province\\{prov_name}_settlement.shp'
    ori_settlement = f'E:\workspace\Research_2022_rural_settlement\work_space\partial_processing\original_settlement_province\{prov_name}_settlement.shp'
    os.mkdir(f'.\\temp_workspace\\{prov_name}')
    env.workspace = r'E:\\workspace\\Research_2022_rural_settlement\\work_space\\partial_processing\\temp_workspace\\'+prov_name
    ori_dem = r"I:\DataHub\SRTM3v4.1_90m\90m-NASA SRTM3 v4.1\China_SRTM3v4.1_90m\China_SRTM3v4.1_90m_proj.tif"

    # %% 计算1km内高差差异
    # 生成buffer
    file_buffer = f'{prov_name}_buffer.shp'
    Buffer_analysis(ori_settlement,file_buffer,'500 Meters')
    print(f'{prov_name} buffer 生成成功。')

    # dissolve buffer
    file_dissolve = f'{prov_name}_buffer_dissolved.shp'
    Dissolve_management(file_buffer,file_dissolve)
    print(f'{prov_name} dissolve 生成成功。')

    # explode
    file_explode = f'{prov_name}_buffer_exploded.shp'
    MultipartToSinglepart_management(file_dissolve,file_explode)
    print(f'{prov_name} explode 成功。')

    # zonal as table
    file_zonal = f'{prov_name}_zonal_table.dbf'
    ZonalStatisticsAsTable(file_explode,'FID',ori_dem,file_zonal,statistics_type='RANGE')
    print(f'{prov_name} zonal 成功。')

    # join field to ori point
    JoinField_management(ori_settlement,'FID',file_zonal,'FID_','RANGE')
    print(f'{prov_name} dem range join 成功。')

    # %% 计算村落聚集程度
    # 生成buffer，半径为全国村落的平均距离1402m
    file_buffer2 = f'{prov_name}_buffer2.shp'
    Buffer_analysis(ori_settlement,file_buffer2,'1402 Meters')
    print(f'{prov_name} buffer2 生成成功。')

    # 给原始数据添加字段为aggregation，统计这里面有多少村落
    AddField_management(ori_settlement,'aggregate', "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    file_intersect = f'{prov_name}_settlement_intersect.shp'
    Intersect_analysis([ori_settlement, file_buffer2], file_intersect)
    file_frequency_table = f'{prov_name}_frequency_table.dbf'
    Frequency_analysis(file_intersect, file_frequency_table, "ORIG_FID", "")
    JoinField_management(ori_settlement, "FID", file_frequency_table, "ORIG_FID", "FREQUENCY")
    CalculateField_management(ori_settlement, 'aggregate', "!FREQUENCY!-1", "PYTHON_9.3", "")
    DeleteField_management(ori_settlement, ["FREQUENCY"])
    print(f'{prov_name} 村落聚集性 生成成功。')

    # %% 计算所属城市群
    ori_urbanagg = r"E:\workspace\Research_2022_rural_settlement\work_space\城市群矢量\中国第一级城市群.shp"
    file_intersect_urbanagg = f'{prov_name}_urbanagg.shp'
    Intersect_analysis([ori_settlement, ori_urbanagg], file_intersect_urbanagg)

    JoinField_management(ori_settlement,"ori_id",file_intersect_urbanagg,'ori_id','urbanagg')
    # AddField_management(ori_settlement,'urban_agg', "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    # CalculateField_management(ori_settlement, 'urban_agg', '"Others" if !urbanagg! == None else !urbanagg!', "PYTHON_9.3", "")
    # DeleteField_management(ori_settlement, ["urbanagg"])
    print(f'{prov_name} 计算所属城市群 生成成功。')



























