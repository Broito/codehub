# -*- coding: utf-8 -*-
import arcpy,math
from arcpy import env
import  xlwt
import datetime

def day_time():
    "统计一天不同时间段事故发生数目，全年"
    geo_2015 = "F:\\trafficdata\\matchdata\\data.gdb\\geo2015"
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("sheet1")
    colID = 0  # 列数
    monthList=[1,3,5,7,8,10,12]#31天的月份
    for month in range(7,13):#12个月份
        dayNum=31
        date = '2015/%d/'%(month)
        if month in monthList:
            dayNum=32
        if month==2:
            dayNum=29
        for time in range(1,dayNum):#统计整个月数据
            rowID = 1  # 行数
            timeStart='2015-%d-%d 00:00:00'%(month,time)
            timeEnd='2015-%d-%d 23:59:59'%(month,time)
            sheet.write(0, colID, date+str(time))
            for i in range(1,25):
                qstr = """"accitime">=date '"""+timeStart+"""' AND  "accitime"<= date '"""+timeEnd+"""' AND "timegrade"=%d"""%(i)
                cur =arcpy.da.SearchCursor(geo_2015, ["accitime"], qstr)
                j=0
                for row in cur:
                    j+=1
                sheet.write(rowID, colID, j)
                rowID+=1
            workbook.save("F:\\trafficdata\\speed\\timeResult12.xls")  # 保存数据
            colID +=1
            print date+str(time),"完成"

def week_time():
    "统计事故一周发生次数,2015年1月1号星期四"
    monthList=[1,3,5,7,8,10,12]#31天的月份
    weekList=[[],[],[],[],[],[],[]]
    mm=4
    for month in range(1,13):#12个月份
        dayNum=31
        if month in monthList:
            dayNum=32
        if month==2:
            dayNum=29
        for time in range(1,dayNum):
            nn=mm%7
            value="%d_%d"%(month,time)
            if nn==0:
                nn=7
            weekList[nn-1].append(value)
            mm+=1

    geo_2015 = "F:\\trafficdata\\matchdata\\data.gdb\\node2015"#seg2015、node2015
    workbook = xlwt.Workbook()
    for k in range(len(weekList)):#七个周次
        rowID=0#行数
        sheet = workbook.add_sheet(str(k+1))#工作表名称
        weekList[k]
        for m in range(len(weekList[k])):
            date=weekList[k][m].split('_')
            sheet.write(rowID, 0, date[0]+"/"+date[1])
            timeStart='2015-%s-%s 00:00:00'%(date[0],date[1])
            qstr =""""newdate"=date '""" + timeStart + """'"""
            cur = arcpy.da.SearchCursor(geo_2015, ["newdate"], qstr)
            num=0
            for row in cur :
                num+=1
            sheet.write(rowID, 1, num)
            rowID+=1
        workbook.save("F:\\trafficdata\\speed\\node.xls")  # 保存数据
        print "%d周完成"%(k+1)

def month_time():
    "统计一年不同月份数据"
    geo_2015 = "F:\\trafficdata\\matchdata\\data.gdb\\geo2015"
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("sheet1")
    rowID = 0  # 行数
    for month in range(1,13):#12个月份
        sheet.write(rowID, 0, '2015/'+str(month))
        timeStart = '2015-%d-1 00:00:00' % (month)
        timeEnd = '2015-%d-1 00:00:00' % (month + 1)
        qstr = """"newdate">=date '""" + timeStart + """' AND  "newdate"< date '""" + timeEnd + """'"""
        if month==12:
            qstr = """"newdate" >= date '2015-12-01 00:00:00' AND "newdate" <= date '2015-12-31 23:59:59'"""
        cur = arcpy.da.SearchCursor(geo_2015, ["newdate"], qstr)
        j = 0
        for row in cur:
            j += 1
        sheet.write(rowID, 1, j)
        rowID+=1
        print '%d月完成'%(month)
        workbook.save("F:\\trafficdata\\speed\\monthResult.xls")  # 保存数据

def road_time():
    "统计不同道路类型不同时间段发生情况，四月份均值"
    geo_2015 = "F:\\trafficdata\\matchdata\\data.gdb\\geo2015"
    roadType=[u"快速路",u"主干道",u"次干道",u"支路"]
    workbook = xlwt.Workbook(encoding = 'utf-8')#生成一个工作簿，里面有多个工作表
    qstr = """"accitime">=date '2015-04-1 00:00:00' AND "accitime"<=date '2015-04-30 23:59:59' """
    cur = sorted(arcpy.da.SearchCursor(geo_2015, ["accitime","timegrade","roadgrade"], qstr))#符合四月份的数据
    for road in roadType :
        sheet = workbook.add_sheet(road)
        colID = 0  # 列数
        for day in range(1,31):#统计整个4月数据
            rowID = 1  # 行数
            sheet.write(0, colID, '2015/4/'+str(day))
            timeStart = '2015-4-%d 00:00:00'%(day)
            timeStart=datetime.datetime.strptime(timeStart, "%Y-%m-%d %H:%M:%S")
            timeEnd = '2015-4-%d 23:59:59'%(day)
            timeEnd=datetime.datetime.strptime(timeEnd, "%Y-%m-%d %H:%M:%S")
            for i in range(1,25):#24个时间段
                j=0
                for index in range(len(cur)):
                    if cur[index][2]==road and cur[index][0]>=timeStart and cur[index][0]<=timeEnd and cur[index][1]==i:
                        j+=1
                sheet.write(rowID, colID, j)
                rowID+=1
            workbook.save("F:\\trafficdata\\speed\\timeRoad.xls")  # 保存数据
            colID +=1
        print road,"完成"
def newroad_type():
    "统计不同道路类型不同时间段发生情况，2015年（和上面方法相比更加简洁）"
    geo_2015 = "F:\\trafficdata\\matchdata\\data.gdb\\geo2015"
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet("road2015")
    cur = sorted(arcpy.da.SearchCursor(geo_2015, ["timegrade", "roadgrade"]))
    sumRoad=[[],[],[],[]]#四种类型，24小时事故数
    for i in range(4):
        for j in range(24):
            sumRoad[i].append(0)
    for row in cur:
        if row[1]==u"快速路":
            sumRoad[0][row[0]-1]+=1
        elif row[1]==u"主干道":
            sumRoad[1][row[0] - 1] += 1
        elif row[1]==u"次干道":
            sumRoad[2][row[0] - 1] += 1
        elif row[1]==u"支路":
            sumRoad[3][row[0] - 1] += 1
    rowID=0
    for i in range(4):
        colID = 0
        for j in range(24):
            data=sumRoad[i][j]
            sheet.write(rowID, colID, data)
            colID+=1
        rowID+=1
    workbook.save("F:\\trafficdata\\speed\\timeRoad2015.xls")  # 保存数据
def newday_time():
    "统计一天不同时间段事故发生数目，全年，分路段和路口（和上面方法相比更加简洁）"
    seg_2015 = "F:\\trafficdata\\matchdata\\data.gdb\\geo2015"#node2015,seg2015
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("segnum")
    cur = sorted(arcpy.da.SearchCursor(seg_2015, ["timegrade"]))
    sum=[]#24个时段事故数
    for i in range(24):
        sum.append(0)
    for row in cur:
        sum[row[0]-1]+=1
    rowID=0
    for j in range(24):
        sheet.write(rowID, 0, sum[j])
        rowID+=1
    workbook.save("F:\\trafficdata\\speed\\geonum.xls")  # 保存数据

#day_time()
week_time()
#month_time()
#road_time()
#newroad_type()
#newday_time()









