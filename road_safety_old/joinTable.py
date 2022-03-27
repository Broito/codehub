# -*- coding: utf-8 -*-
import arcpy
from arcpy import env
spaWeb=arcpy.SpatialReference(3857)
env.workspace="F:\\trafficdata\\nomatch\\data.gdb"
road_osm="F:\\trafficdata\\changning\\data.gdb\\road_osm"#道路数据
def join_table():
    "由最近点表格生成点事故"
    match2014 = "match2016"
    all2014 = "all2016"
    match2014_Layer = "match2016_Layer"
    geo2014 = "geo2016"

    arcpy.MakeXYEventLayer_management(match2014, "NEAR_X", "NEAR_Y", match2014_Layer,spaWeb, "")
    arcpy.CopyFeatures_management(match2014_Layer, geo2014, "", "0", "0", "0")
    arcpy.JoinField_management(geo2014, "IN_FID", all2014, "OBJECTID", "JCZZT;JDBH;JQBH;JQMC;JQLB;JQJB;BJDD;AFDD;JQNR;CJYXM;JJSJ;X;Y;AJLB;SFCDW")
    arcpy.JoinField_management(geo2014, "NEAR_FID", road_osm, "OBJECTID","roadgrade;roadname")
    arcpy.Delete_management(match2014_Layer)  # 删除临时数据

join_table()
