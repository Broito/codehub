from arcpy import *
from arcpy.sa import *

# 工作空间路径，写想要输出的文件夹
env.workspace = r"C:\Users\NingchengWang\Desktop\CGSS"
# 被统计栅格的路径+文件名
raster = r"I:\DataHub\WorldPop_proj\chn_ppp_2015.tif"
# 统计至该polygon
polygon = r"C:\Users\NingchengWang\Desktop\CGSS\CGSS2015_1000.shp"
# 输出table的名字，输出到工作空间
outtable = r'zonal_result.dbf'
# 新建一个临时文件夹，存放临时工作表，运行完删除该文件夹即可。不用手动新建，写入路径即可。
dbf_folder = r"C:\Users\NingchengWang\Desktop\CGSS\dbf_folder"
if not os.path.exists(dbf_folder):
    os.mkdir(dbf_folder)

# polygon的统计字段，即按哪个字段区分polygon单元
fields = ['FID']
cur = da.SearchCursor(polygon,fields)
for i in cur:
    objid = i[0]
    print ("{0} is being processed".format(objid))
    lyr = "Zone {0}".format(objid)
    lyr = MakeFeatureLayer_management(polygon,lyr,'"{0}" = {1}'.format(fields[0],objid))
    tempTable = "{0}\\DBF_{1}.dbf".format(dbf_folder, objid)
    ZonalStatisticsAsTable(lyr, "{0}".format(fields[0]), raster, tempTable, "DATA")
    print(objid)

dbfs =ListTables()
Merge_management(dbfs,outtable)

























