# -*- coding: utf-8 -*-
import arcpy,datetime
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间
import numpy as np
def get_data():
    env.workspace = "F:\\zmydata\\"
    datashp = "regular_building.shp"#原始建筑物数据
    building_new="building_new.shp"#新数据
    spa=arcpy.SpatialReference("F:\\zmydata\\regular_building.prj")
    arcpy.CreateFeatureclass_management(env.workspace, building_new, "POLYGON", datashp, "DISABLED", "DISABLED",spa)
    curShp = sorted(arcpy.da.SearchCursor(datashp, ["SHAPE@","GROUPID","CONTOUR","Height"]), key=lambda a_list: a_list[1])
    curNew=arcpy.da.InsertCursor(building_new,["SHAPE@","GROUPID","CONTOUR","Height"])
    curShp=np.array(curShp)#ndarry数组
    fistLine=list(curShp[:,1])#取第一列
    groupID=sorted(set(fistLine))#获取编号列表

    for id in groupID:
        start=fistLine.index(id)#此编号开始位置
        end=start+fistLine.count(id)#此编号结束位置
        sortdata=sorted(curShp[start:end,:],key=lambda a_list: a_list[3],reverse=True)#从大到小
        rowf=sortdata[0]
        curNew.insertRow(rowf)

    #print groupID

get_data()
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime