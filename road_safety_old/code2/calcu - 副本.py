#-*- coding:utf-8 -*-
import arcpy,xlrd,xlwt,datetime
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间
#统计道路平均速度和通行次数
env.workspace = "C:\\GPS\\speed\\data.gdb"
def excel_table():
    "24小时段excel转换成table，速度有m/s转换成km/h"
    excelPath="C:\\GPS\\speed\\speedALL24_6-10.xls" #
    roadId = []
    avaspeed = []
    instanspeed = []
    carnum = []
    for i in range(0,43930):
        roadId.append(i+1)
        avaspeed.append(0)
        instanspeed.append(0)
        carnum.append(0)
    excelFile = xlrd.open_workbook(excelPath)
    excelall = excelFile.sheet_names()  # excel中所有的列表的名字[u'0_1', u'1_2', u'2_3', u'3_4', u'4_5'
    for i in range(0,24):
        excelList = excelFile.sheet_by_name(excelall[i])  # 获取工作表
        nrows = excelList.nrows  # 行数
        for rowid in range(1,nrows):            
            rowarray = excelList.row_values(rowid)  # 获取整行值，返回数组          
            roadid = int(rowarray[0])  # 路段id
            aspeed = round(float(rowarray[2])*3.6,4) # 速度,km/h,保留两位小数
            inspeed = round(float(rowarray[3]),4)        
            cnum = int(rowarray[1])
            if avaspeed[roadid]!= 0:
                avaspeed[roadid-1] = (avaspeed[roadid-1]+aspeed)/2
                instanspeed[roadid-1] = (instanspeed[roadid-1]+inspeed)/2
            else:
                avaspeed[roadid-1]=aspeed
                instanspeed[roadid - 1] = inspeed
            carnum[roadid-1] = carnum[roadid-1] + cnum
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('allroadspeed')  # 添加一个工作表
    sheet.write(0, 0, "roadID" )  # 路段id
    sheet.write(0, 1, "carNumber" )  # 车辆数
    sheet.write(0, 2, "roadSpeed" )  # 区间平均速度
    sheet.write(0, 3, "instantSpeed" )  # 瞬时速度均值
    for i in range(0,len(carnum)):
        sheet.write(i+1, 0, i + 1)  # 路段id
        sheet.write(i+1, 1, carnum[i])  # 车辆数
        sheet.write(i+1, 2, avaspeed[i])  # 区间平均速度
        sheet.write(i+1, 3, instanspeed[i])  # 瞬时速度均值
    saveFile = "C:\\GPS\\xls\\speedALL6-10.xls"
    workbook.save(saveFile)  # 保存数据
    print sheet, "表完成"
excel_table()
#speed_avg()
#speed_all()
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime
