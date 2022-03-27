# -*- coding: utf-8 -*-
import arcpy
from arcpy import env
env.workspace="F:\\trafficdata\\changning\\data.gdb"

def cut_line():
    "在道路上每隔500米生成一个点"
    curline=arcpy.da.SearchCursor("road_lane",["SHAPE@"])
    curpoint=arcpy.da.InsertCursor("cutpoint",["SHAPE@"])
    for row in curline:
        line=row[0]
        leng=line.length#线的长度
        cutlen=500#截取线的长度
        while (leng>500 and leng>600):#若最后长度小于600米则保留
            pt=line.positionAlongLine(cutlen)
            curpoint.insertRow([pt])
            leng=leng-500#剩余长度
            cutlen=cutlen+500

cut_line()


