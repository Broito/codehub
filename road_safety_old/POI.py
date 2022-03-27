# -*- coding: utf-8 -*-
import arcpy,datetime,re
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间

#"获得每个路口的POI点个数"
def get_poi():
    env.workspace = "F:\\trafficdata\\changning\\POI500.gdb"
    road_osmbuffer500 = "F:\\trafficdata\\changning\\data.gdb\\road_nodebuffer500"
    fileName = []  # 获得数据库下所有点数据["P01clip","P02clip"...]
    mPoint = arcpy.ListFeatureClasses()
    for list in mPoint:
        if re.search("clip",list):
            fileName.append(list)
    joinTarget=road_osmbuffer500
    for point in fileName:
        P01join = point+"join"
        fieldname=point[:-4]#去除clip
        arcpy.SpatialJoin_analysis(joinTarget, point, P01join, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", "", "")
        arcpy.AddField_management(P01join, fieldname, "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(P01join, fieldname, "!Join_Count!", "PYTHON_9.3", "")
        joinTarget=P01join
        arcpy.DeleteField_management(P01join, "Join_Count;TARGET_FID")
        print point

def poi05():
    "针对公交车站数据的处理，删除重复点"
    env.workspace = "F:\\trafficdata\\changning\\POI500.gdb"
    P05clip_new="P05clip_new"
    curNew = arcpy.da.UpdateCursor(P05clip_new, ["SHAPE@XY", "NAME"])
    datalist=[]
    for row in curNew:
        data=[row[0][0],row[0][1],row[1]]
        if data in datalist:
            curNew.deleteRow()
            continue
        else:
            datalist.append(data)

poi05()
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime