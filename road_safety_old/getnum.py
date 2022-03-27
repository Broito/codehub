# -*- coding: utf-8 -*-
import arcpy,re,math
from arcpy import env
def create():
    env.workspace = "F:\\trafficdata\\matchResult\\20150419.gdb"
    writeFile=open("F:\\trafficdata\\taxi\\data\\19num.txt","a")
    fileName=[]#获得文件夹下所有的匹配点数据
    mPoint=arcpy.ListFeatureClasses()
    for list in mPoint:
        if re.match(r"[m]",list):
            list.split('m')[1]
            fileName.append(list.split('m')[1])
            writeFile.write(list.split('m')[1]+"\n")
def new():
    openFile=open("F:\\trafficdata\\taxi\\data\\19.txt","r")
    writeFile=open("F:\\trafficdata\\taxi\\data\\19new.txt","a")
    carID=[]
    for row in openFile:
        carID.append(row[:-1])
    carID=sorted(carID)
    for id in carID:
        writeFile.write(id+"\n")
create()
new()