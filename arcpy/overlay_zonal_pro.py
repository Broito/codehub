import os
from arcpy import *
from arcpy.sa import *


os.chdir(r"E:\workspace\Research_2022_rural_settlement\work_space")
env.workspace = r"E:\workspace\Research_2022_rural_settlement\work_space\dbf_folder"
raster = r"I:\DataHub\SRTM3v4.1_90m\90m-NASA SRTM3 v4.1\China_SRTM3v4.1_90m\China_SRTM3v4.1_90m_proj.tif"
polygon = r"E:\workspace\Research_2022_rural_settlement\work_space\main.gdb\行政村_dem_buffer1km"
outtable = r'zonal_result.dbf'
dbf_folder = r"E:\workspace\Research_2022_rural_settlement\work_space\dbf_folder"

if not os.path.exists(dbf_folder):
    os.mkdir(dbf_folder)

fields = ['OBJECTID']
cur = da.SearchCursor(polygon,fields)
for i in cur:
    objid = i[0]
    print ("{0} is being processed".format(objid))
    lyr = "Zone {0}".format(objid)
    lyr = MakeFeatureLayer_management(polygon,lyr,'"OBJECTID" = {0}'.format(objid))
    tempTable = "{0}\\DBF_{1}.dbf".format(dbf_folder, objid)
    # try:
    ZonalStatisticsAsTable(lyr, "OBJECTID", raster, tempTable, "DATA")
    # except:
    #     print("error")

dbfs =ListTables()
Merge_management(dbfs,outtable)

























