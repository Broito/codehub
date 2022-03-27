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
        env.workspace = "C:\\GPS\\speed\\matchResult\\07%s.gdb"%(work)
        gap1="2016-07-%s %d:00:00"%(work,time1)
        timeGap1=datetime.datetime.strptime(gap1, "%Y-%m-%d %H:%M:%S")#时间间隔
        gap2="2016-07-%s %d:59:59"%(work,time2)
        timeGap2=datetime.datetime.strptime(gap2, "%Y-%m-%d %H:%M:%S")#时间间隔
        fileName=[]#获得数据库下所有的匹配点数据，[m0005,m00069]
        mPoint=arcpy.ListFeatureClasses()
        for list in mPoint:
            if re.match(r"[m]",list):
                fileName.append(list)
        allcars = []
        for i in range(0,24):
            allcars.append(0)
        for fname in fileName:
            curf = sorted(arcpy.da.SearchCursor(fname, ["IN_FID", "NEAR_FID", "time","speed","distance"]),key=lambda a_list: a_list[0])
            time0 = []#0-2内所有的数据
            for curRow in curf:
                if curRow[2]>=timeGap1 and curRow[2]<=timeGap2:
                    time0.append(curRow)
            if len(time0)>0:
                allcars[time1-1] = allcars[time1-1]+1
                for roadid in roadID:
                    roadTime = []  # 某个路段所有在0-2内的数据
                    for row in time0:
                        if row[1]==roadid:
                            roadTime.append(row)
                    if len(roadTime)>1:#至少有2个点落入路段才计算速度
                        startTime=roadTime[0][2] #初始点时间
                        endTime=roadTime[-1][2]#结束点时间
                        timeInter=(endTime-startTime).seconds
                        if timeInter!=0:
                            distance=0
                            for dis in roadTime[1:]:
                                distance+=dis[4]
                            roadv=float(distance)/timeInter#距离和时间比值
                            instaneS=0
                            for mm in roadTime:
                                instaneS+=mm[3]
                            roads=float(instaneS)/len(roadTime)#瞬时速度均值
                            if roadv<22 and roadv>3:#如果单车速度大于3小于22才放入数据中
                                roadSpeed[roadid - 1].append(roadv)
                                instantSpeed[roadid - 1].append(roads)
            else:
                continue
        print  work,"号完成"
    rowID=1#表格行数
    for i in range(len(roadSpeed)):#i=0代表路段id为1
        carNum=len(roadSpeed[i])#id为i+1的路段所有车辆数
        if carNum>0:#车辆数至少3辆才有说服力
            speedAvg=(math.fsum(roadSpeed[i]))/carNum#区间速度
            speedIns=(math.fsum(instantSpeed[i]))/carNum#瞬时速度
            sheet.write(rowID, 0, i+1)#路段id
            sheet.write(rowID, 1, carNum)#车辆数
            sheet.write(rowID, 2, speedAvg)#区间平均速度
            sheet.write(rowID, 3, speedIns)#瞬时速度均值
            rowID += 1
            saveFile="C:\\GPS\\speed\\speedALL24_6-10.xls"
            workbook.save(saveFile)  # 保存数据

roadID=[]#道路ID
for i in range(1,43931):
    roadID.append(i)
workSpace=[]#天数
for i in range(6,11):#1号至24号所有数据求速度均值  统计工作日
    if i<10:
        z = '0'+ str(i)
    else:
        z = str(i)
    workSpace.append(z)
workbook = xlwt.Workbook(encoding = 'utf-8')
for i in range(0,24):#执行24个时间段的
    sheetName="%d_%d"%(i,i+1)
    get_result(i,i,sheetName)#时间间隔0-2，工作表名称
    print "%d-%d时间段完成"%(i,i+1)
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime
















    

