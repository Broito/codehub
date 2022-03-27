# -*- coding: utf-8 -*-
import arcpy
from arcpy import env
import datetime
probeginTime=datetime.datetime.now()#程序开始时间

def earse():
    "依次读取缓冲区进行earse操作"
    env.workspace = "F:\\trafficdata\\changning\\dsmresult.gdb"
    bufferSmall="F:\\trafficdata\\changning\\dsm.gdb\\buffer_small" #路宽一半距离缓冲区
    bufferLarge="F:\\trafficdata\\changning\\dsm.gdb\\buffer_large"#路宽一半距离+10米缓冲区
    curSmall=sorted(arcpy.da.SearchCursor(bufferSmall,["SHAPE@","oid"]),key=lambda a_list: a_list[1])
    curLarge=sorted(arcpy.da.SearchCursor(bufferLarge,["SHAPE@","oid"]),key=lambda a_list: a_list[1])
    for id in range(1,1372):#共1371条缓冲区
        earseName="buffer%d"%(id)
        arcpy.Erase_analysis(curLarge[id-1][0], curSmall[id-1][0],earseName, '#')
        if id%100==0:
            print id

def get_buffer():
    "将零散的缓冲区数据合并成一个"
    env.workspace = "F:\\trafficdata\\changning\\dsmresult.gdb"
    bufferAll = "F:\\trafficdata\\changning\\dsm.gdb\\buffer_all"  # 合并的缓冲区数据
    curNew = arcpy.da.InsertCursor(bufferAll, ["SHAPE@","oid"])  # 插入的新表
    mPoint = arcpy.ListFeatureClasses()# 获得数据库下所有缓冲区数据["buffer1","buffer2"...]
    for list in mPoint:
        oid=int(list[6:])#缓冲区数据,oid
        cursear=arcpy.da.SearchCursor(list,["SHAPE@"],""""OBJECTID"=1""")
        poly=cursear.next()[0]#多边形
        rowf=[poly,oid]
        curNew.insertRow(rowf)
        del cursear
        print list
    del curNew
#earse()
#get_buffer()
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime

