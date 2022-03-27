# -*- coding: utf-8 -*-
import arcpy,re,datetime
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间

def road_number(sTime,eTime):
    """
    获得每条道路在某一时间段有多少车辆
    :param sTime: 开始时间
    :param eTime: 结束时间
    """
    env.workspace = "F:\\trafficdata\\FCD20150420\\20150420.gdb"
    road_osm="F:\\trafficdata\\FCD20150420\\data.gdb\\road_osm"
    qstr = """"time">date'2015-04-20 %d:00:00' AND "time"< date'2015-04-20 %d:00:00'""" % (sTime, eTime)
    if sTime > eTime:#超过24点
        qstr = """"time">date'2015-04-20 %d:00:00' OR "time"< date'2015-04-20 %d:00:00'""" % (sTime, eTime)

    roadNum=[]
    for i in range(1371):
        roadNum.append(0)
    mPoint = arcpy.ListFeatureClasses()
    mp=0#共11060个出租车数据
    for point in mPoint:
        try:
            curPoint = sorted(arcpy.da.SearchCursor(point, ["NEAR_FID"],qstr),key=lambda a_list: a_list[0])
            curPoint=sorted(set(curPoint))#去重
            for cur in curPoint:
                index=cur[0]
                roadNum[index-1]+=1
            print mp
            mp+=1
        except:
            continue
    #将每条路段此时间段出租车辆数量附加到线数据上
    roadCur=arcpy.da.UpdateCursor(road_osm, ["carNum17_19"])
    k=0
    for rowu in roadCur:
        rowu[0] =roadNum[k]
        roadCur.updateRow(rowu)
        k+=1

road_number(17,19) #计算 22-4点车流量
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime
