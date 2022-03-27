# -*- coding: utf-8 -*-
import arcpy,re,math
from arcpy import env
import  xlwt, datetime
probeginTime=datetime.datetime.now()#程序开始时间
def get_result(time1,time2,sheetName):
    "下面获得0-2时所有路段速度,7天数据均值"
    sheet = workbook.add_sheet(sheetName)#添加一个工作表
    print sheetName
    sheet.write(0, 0, "roadID"+sheetName)#路段id
    sheet.write(0, 1, "carNumber"+sheetName)#车辆数
    sheet.write(0, 2, "roadSpeed"+sheetName)#区间平均速度
    sheet.write(0, 3, "instantSpeed"+sheetName)#瞬时速度均值
    roadSpeed=[]#每个路段在0-2时间段区间速度,[[],[],[]...]共1371项，第一项是roadid为1的路段所有车辆速度
    instantSpeed=[]#每个路段在0-2时间段瞬时速度平均值
    for i in range(1,43931):
        roadSpeed.append([])
        instantSpeed.append([])
    for work in workSpace:#work是天数。18,19...
        env.workspace = "C:\\GPS\\speed\\matchResult\\0706.gdb"
        gap1="2016-07-0%d %d:00:00"%(work,time1)
        timeGap1=datetime.datetime.strptime(gap1, "%Y-%m-%d %H:%M:%S")#时间间隔
        gap2="2016-07-0%d %d:59:59"%(work,time2)
        timeGap2=datetime.datetime.strptime(gap2, "%Y-%m-%d %H:%M:%S")#时间间隔
        fileName=[]#获得数据库下所有的匹配点数据，[m0005,m00069]
        mPoint=arcpy.ListFeatureClasses()
        for list in mPoint:
            if re.match(r"[m]",list):
                fileName.append(list)
        a = 0
        for fname in fileName:
            curf = sorted(arcpy.da.SearchCursor(fname, ["IN_FID", "NEAR_FID", "time","speed","distance"]),key=lambda a_list: a_list[0])
            time0 = []#0-2内所有的数据
            for curRow in curf:
                if curRow[2]>=timeGap1 and curRow[2]<=timeGap2:
                    a = a+1
                    break
        
    print  work,"号完成"
    return a

roadID=[]#道路ID
for i in range(1,43931):
    roadID.append(i)
workSpace=[]#天数
for i in range(6,7):#1号至24号所有数据求速度均值
    workSpace.append(i)
workbook = xlwt.Workbook(encoding = 'utf-8')
allcars = []

for i in range(0,24):#执行24个时间段的
    
    sheetName="%d_%d"%(i,i+1)
    a = get_result(i,i,sheetName)#时间间隔0-2，工作表名称
    allcars.append(a)
    print "%d-%d时间段完成"%(i,i+1)
x = open('carnum24.txt','w')
for i in allcars:
    x.write(str(i))
    x.write('\n')
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime















    

