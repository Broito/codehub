# -*- coding: utf-8 -*-
import arcpy
import  xlwt
from arcpy import env
env.workspace="F:\\trafficdata\\matchdata\\data.gdb"
def differ_road():
    "不同道路类型事故统计，2012至2015"
    geoData=["geo2012","geo2013","geo2014","geo2015"]
    roadType=["快速路","主干道","次干道","支路"]
    workbook = xlwt.Workbook(encoding='utf-8')#生成一个工作簿，里面有多个工作表
    sheet = workbook.add_sheet("data")
    sheet.write(1, 0, "快速路")
    sheet.write(2, 0, "主干道")
    sheet.write(3, 0, "次干道")
    sheet.write(4, 0, "支路")
    colID=1
    for geo in geoData:
        sheet.write(0, colID, geo)
        rowID=1
        for road in roadType:
            qstr = """"roadgrade"= '%s'"""%(road)
            cur = arcpy.da.SearchCursor(geo, ["roadgrade"], qstr)
            j = 0
            for row in cur:
                j += 1
            sheet.write(rowID, colID, j)
            rowID+=1
        colID+=1
        workbook.save("F:\\trafficdata\\speed\\factor.xls")  # 保存数据
        print "%s完成"%(geo)

def differ_node():
    "统计不同分支交叉口事故数"
    nodeData ="count_node"
    workbook = xlwt.Workbook()  # 生成一个工作簿，里面有多个工作表
    sheet = workbook.add_sheet("data")
    sheet.write(1, 0, "type1")
    sheet.write(2, 0, "type2")
    sheet.write(3, 0, "type3")
    sheet.write(4, 0, "type4")
    freListt=["fre2012","fre2013","fre2014","fre2015"]
    legCount=[3,4,5,6]
    colID = 1
    for fre in freListt:
        sheet.write(0, colID, fre)
        rowID = 1
        for leg in  legCount:
            qstr = """"leg_count"= %d""" % (leg)
            cur = arcpy.da.SearchCursor(nodeData, [fre], qstr)
            sum = 0
            for row in cur:
                sum+=row[0]
            sheet.write(rowID, colID, sum)
            rowID += 1
        colID += 1
        workbook.save("F:\\trafficdata\\speed\\factor.xls")  # 保存数据
        print "%s完成" % (fre)

def differ_weather():
    "不同天气事故统计，2015年"
    geoData = "geo2015"
    workbook = xlwt.Workbook(encoding = 'utf-8')  # 生成一个工作簿，里面有多个工作表
    sheet = workbook.add_sheet("data")
    weaList=["晴","晴转多云","多云","阴","雾","雷雨","中雨","中雪"]
    colID = 0
    for wea in weaList:
        sheet.write(0, colID, wea)
        rowID = 1
        qstr = """"weather"= '%s'""" % (wea)
        cur = arcpy.da.SearchCursor(geoData, ["weather"], qstr)
        j = 0
        for row in cur:
            j += 1
        sheet.write(1, colID, j)
        colID += 1
        workbook.save("F:\\trafficdata\\speed\\factor.xls")  # 保存数据
        print "%s完成" % (wea)

#differ_road()
differ_node()
#differ_weather()

