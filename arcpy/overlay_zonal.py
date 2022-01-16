# -*- coding: utf-8 -*-

# 导入系统模块
import arcgisscripting
import os

# 创建Geoprocessor对象
gp = arcgisscripting.create(10.6)
gp.OverWriteOutput = 1

# 检查许可
gp.CheckOutExtension("Spatial")

#设置默认工作空间
gp.workspace = r"E:\workspace\Research_2021_weather_collision\data_processing\NTL"

# 设置变量
raster = r"E:\workspace\Research_2021_weather_collision\data_processing\NTL\changning_NTL_transformed.tif"
inFC = r"E:\workspace\Research_2021_weather_collision\data_processing\road_data.gdb\road_OSM_sim200_buffer100"
outTable = r"zonal_luojia.dbf"
DBF_dir = r"E:\workspace\Research_2021_weather_collision\data_processing\dbfs" #folder for temp dbf outputs

if not os.path.exists(DBF_dir):
    os.mkdir(DBF_dir)

#循环处理要素
inRows = gp.searchcursor(inFC)
inRows.reset()
inRow = inRows.next()



while inRow:
# Zone_ID is the assumed name of the zone field
    print ("{0} is being processed".format(inRow.roadid_sim))
    lyr = "Zone {0}".format(inRow.roadid_sim)
    gp.MakeFeatureLayer_management(inFC, lyr, '"OBJECTID" = {0}'.format(inRow.roadid_sim))
    tempTable = "{0}/DBF_{1}.dbf".format(DBF_dir, inRow.roadid_sim)
    try:
        gp.ZonalStatisticsAsTable_sa(lyr, "roadid_sim", raster, tempTable, "DATA")
    except:
        print("error")
    inRow = inRows.next()

#设置临时DBF文件的存储路径
gp.workspace = DBF_dir
TableList = gp.ListTables("*")

#合并临时DBF文件
gp.Merge(TableList, outTable)
