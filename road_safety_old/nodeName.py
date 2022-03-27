# -*- coding: utf-8 -*-
import arcpy
def node_name():
    "交叉点赋予道路名称字段"
    nodeJoin = "F:\\trafficdatanew\\changning\\data.gdb\\node_join"
    roadNode="F:\\trafficdatanew\\changning\\data.gdb\\road_node"
    curnode = arcpy.da.UpdateCursor(roadNode, ["name1", "name2"])
    fid=1
    for uprow in curnode:#共657个交叉点
        qstr = """"TARGET_FID"=%d""" % (fid)
        curjoin = arcpy.da.SearchCursor(nodeJoin,["name"],qstr)
        #name=[]#长度最多为3，可能值为["nulldata/长安路"],["nulldata","长安路"]，["长安路","虹桥路"],
        # ["nulldata","长安路","虹桥路"],["洪安路","长安路","虹桥路"]
        name1="nulldata"
        name2="nulldata"
        nameList=[]
        for row in curjoin:
            if (row[0]!="nulldata") and (row[0] not in nameList):
                nameList.append(row[0])
        if len(nameList)==1:
            name2=nameList[0]
        elif len(nameList)>=2:
            name1=nameList[0]
            name2=nameList[1]
        uprow[0]=name1
        uprow[1]=name2
        curnode.updateRow(uprow)
        print fid
        fid+=1
def node_speed():
    "获得路口速度，是相交的所有路段均值"
    nodeJoin = "F:\\trafficdata\\changning\\data.gdb\\node_join"
    roadNode = "F:\\trafficdata\\changning\\data.gdb\\road_node"#需要更新的路口数据
    speedList=["roadSpeed0_6"]#, "roadSpeed8_10","roadSpeed12_14","roadSpeed17_19"
    curnode = arcpy.da.UpdateCursor(roadNode, speedList)
    fid = 1
    for uprow in curnode:  # 共657个交叉点
        qstr = """"TARGET_FID"=%d""" % (fid)
        curjoin = arcpy.da.SearchCursor(nodeJoin, speedList, qstr)
        speedAll=[]#[[],[]...],列表长度代表有几个路段
        for row in curjoin:
            speedAll.append(row)
        for listID in range(len(speedList)):
            sumSpeed=0
            for id in range(len(speedAll)):
                sumSpeed+=speedAll[id][listID]
            sp1=round(float(sumSpeed)/len(speedAll),2)#保留两位小数
            uprow[listID]=sp1
        curnode.updateRow(uprow)
        print fid
        fid += 1

def node_lane():
    "获得路口车道数，是相交的所有分支车道数总和"
    nodeJoin = "F:\\trafficdata\\changning\\data.gdb\\node_join"
    roadNode = "F:\\trafficdata\\changning\\data.gdb\\road_node"  # 需要更新的路口数据
    speedList = ["MIN_LANES"]
    curnode = arcpy.da.UpdateCursor(roadNode, speedList)
    fid = 1
    for uprow in curnode:  # 共657个交叉点
        qstr = """"TARGET_FID"=%d""" % (fid)
        curjoin = arcpy.da.SearchCursor(nodeJoin, speedList, qstr)
        speedAll = []  # [[],[]...],列表长度代表有几个路段
        for row in curjoin:
            speedAll.append(row)
        for listID in range(len(speedList)):
            sumSpeed = 0
            for id in range(len(speedAll)):
                sumSpeed += speedAll[id][listID]
            uprow[listID] = sumSpeed
        curnode.updateRow(uprow)
        print fid
        fid += 1
#node_name()
#node_speed()
#node_lane()

