# -*- coding: utf-8 -*-
import arcpy
import re
from arcpy import env
road_osm="F:\\trafficdata\\changning\\data.gdb\\road_osm"#道路数据
road_node="F:\\trafficdata\\changning\\data.gdb\\road_node"#路口数据
spaWeb=arcpy.SpatialReference(3857)#web
def match_road():
    "将所有事故点匹配到路段上"
    env.workspace = "F:\\trafficdata\\nomatch\\data.gdb"
    all2015="all2016"
    near2015 = "near2016"#邻.近点表格，一个是事故对应十条记录
    match2015="match2016"#创建新表，每个事故点对应一行数据
    arcpy.CreateTable_management("F:\\trafficdata\\nomatch\\data.gdb", match2015,"F:\\trafficdata\\nomatch\\data.gdb\\template", "")

    #arcpy.JoinField_management(near2015, "IN_FID", all2015, "OBJECTID", "AFDD")
    #arcpy.JoinField_management(near2015, "NEAR_FID", road_osm, "OBJECTID", "roadname")
    curf = sorted(arcpy.da.SearchCursor(near2015, ["IN_FID","NEAR_FID","NEAR_DIST","NEAR_X","NEAR_Y","roadname","AFDD"]),key=lambda a_list: a_list[0])
    curnew = arcpy.da.InsertCursor(match2015, ["IN_FID", "NEAR_X", "NEAR_Y", "NEAR_FID"])
    index=0#以10递增，因为有10个候选路段

    for fid in range(1,16830):#2016年有16829个路段事故点
        distList=[]
        nameList=[]
        xList=[]
        yList=[]
        fidList=[]
        x=0#待插入的x坐标
        y=0#待插入的y坐标
        nearfid=0#待插入的邻近的fid
        afdd = curf[index][6].strip()#地址描述信息
        for id in range(index,index+10):
            distList.append(curf[id][2])
            nameList.append(curf[id][5].strip())
            xList.append(curf[id][3])
            yList.append(curf[id][4])
            fidList.append(curf[id][1])
        key = distList.index(min(distList))#距离最小编号
        x=xList[key]
        y=yList[key]
        nearfid=fidList[key]
        distNew=[]
        xNew=[]
        yNew=[]
        fidnew=[]
        for i in range(len(distList)):
            result=re.findall(nameList[i],afdd)
            if len(result)!=0:#事故描述信息中有此候选路段
                distNew.append(distList[i])
                xNew.append(xList[i])
                yNew.append(yList[i])
                fidnew.append(fidList[i])
        if len(distNew)!=0:#事故描述信息和候选路段路名有匹配项，可能不止一个，取距离最小的
            key=distNew.index(min(distNew))
            x=xNew[key]
            y=yNew[key]
            nearfid=fidnew[key]
        rowf=[fid,x,y,nearfid]
        curnew.insertRow(rowf)
        index+=10
        print "%d"%(fid)
    del curf,curnew

def match_node():
    "将距离路口15米的点匹配到路口上"
    env.workspace = "F:\\trafficdata\\matchdata\\node.gdb"
    nomatch_node2012 = "nomatch_node2016"
    nearnode2012 = "nearnode2016"
    nearnode20121_Layer = "Layer2016"
    node2012 = "node2016"

    arcpy.DeleteField_management(nomatch_node2012, "IN_FID;NEAR_FID")
    arcpy.GenerateNearTable_analysis(nomatch_node2012, road_node, nearnode2012, "", "LOCATION", "NO_ANGLE", "CLOSEST", "0")
    arcpy.MakeXYEventLayer_management(nearnode2012, "NEAR_X", "NEAR_Y", nearnode20121_Layer,spaWeb)
    arcpy.CopyFeatures_management(nearnode20121_Layer, node2012, "", "0", "0", "0")
    arcpy.DeleteField_management(node2012, "NEAR_DIST;NEAR_X;NEAR_Y")
    #arcpy.JoinField_management(node2012, "IN_FID", nomatch_node2012, "OBJECTID", "JQJB;BJDD;AFDD;JQNR;JJSJ;oid;roadgrade;roadname")
    arcpy.JoinField_management(node2012, "NEAR_FID", road_node, "OBJECTID", "leg_count;name1;name2")
    arcpy.Delete_management(nearnode20121_Layer)  # 删除临时数据
#match_road()
match_node()


