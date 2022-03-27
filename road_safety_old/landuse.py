# -*- coding: utf-8 -*-
import arcpy,datetime,re
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间

def segland_use():
    "给路段添加土地利用面积字段，并赋予值"
    env.workspace = "F:\\trafficdata\\changning\\landuse.gdb"
    road_osm="road_osm"
    titable="segti500"
    field=[]#["landuse5001","landuse5002"..]
    for i in range(1,8):
        fi="landuse500%d"%(i)
        field.append(fi)
        #arcpy.AddField_management(road_osm, fi, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        #arcpy.CalculateField_management(road_osm, fi, "0", "PYTHON_9.3", "")
    curroad = arcpy.da.UpdateCursor(road_osm, field)
    j=1#共1371项
    for uprow in curroad:
        qstr=""""oid"=%d"""%(j)
        cur = sorted(arcpy.da.SearchCursor(titable, ["landtype","AREA"],qstr))
        if len(cur)!=0:
            for row in cur:
                uprow[row[0]-1]=row[1]
            curroad.updateRow(uprow)
        j+=1
        #print j

def nodeland_use():
    "给路口添加土地利用面积字段，并赋予值"
    env.workspace = "F:\\trafficdata\\changning\\landuse.gdb"
    road_osm = "road_node"
    titable = "nodeti500"
    field = []  # ["landuse5001","landuse5002"..]
    for i in range(1, 8):
        fi = "landuse500%d" % (i)
        field.append(fi)
        #arcpy.AddField_management(road_osm, fi, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        #arcpy.CalculateField_management(road_osm, fi, "0", "PYTHON_9.3", "")

    curroad = arcpy.da.UpdateCursor(road_osm, field)
    j = 1  # 共657项
    for uprow in curroad:
        qstr = """"oid"=%d""" % (j)
        cur = sorted(arcpy.da.SearchCursor(titable, ["landtype", "AREA"], qstr))
        if len(cur)!=0:
            for row in cur:
                uprow[row[0] - 1] = row[1]
            curroad.updateRow(uprow)
        j += 1
        print j
#segland_use()
nodeland_use()

