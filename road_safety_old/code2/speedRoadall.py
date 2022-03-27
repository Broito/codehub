#-*- coding:utf-8 -*-
import arcpy,xlrd,xlwt,datetime
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间
env.workspace = "F:\\trafficdata\\speed\\data.gdb"
#将每个时段的速度链接到道路上，没有速度的路段使用相同道路名的路段速度的平均值
def excel_table():
    "24小时段excel转换成table，速度有m/s转换成km/h"
    excelPath="C:\\GPS\\speed\\speedALL24.xls"#
    speedTable = "speedTable24"#创建的表格
    excelFile = xlrd.open_workbook(excelPath)
    excelall = excelFile.sheet_names()  # excel中所有的列表的名字[u'0_1', u'1_2', u'2_3', u'3_4', u'4_5'
    arcpy.CreateTable_management(env.workspace, speedTable, "", "")
    fieldlist=[]#添加新的字段列表，也是要插入的数据字段列表
    insertrow=[]#插入一行的数据
    arcpy.AddField_management(speedTable, "roadID", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    fieldlist.append("roadID")
    insertrow.append(0)
    for nn in excelall:#速度字段，excel中有多少个工作表就插入多少个字段
        speedField="roadSpeed"+nn
        arcpy.AddField_management(speedTable, speedField, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        fieldlist.append(speedField)
        insertrow.append(0)

    tableInsert = arcpy.da.InsertCursor(speedTable, fieldlist)  # ["roadID", "roadSpeed0_1", "roadSpeed1_2",
    insertID = []  # 已插入表格的路段id
    for id  in range(1,1372):#插入1371条路段速度，都为0
        insertrow[0] = id  # 路段id
        tableInsert.insertRow(insertrow) # 插入数据
        insertID.append(id)
    del tableInsert

    for sheet in excelall:
        excelList = excelFile.sheet_by_name(sheet)  # 获取工作表
        indexL = excelall.index(sheet)  # 当前excel表数据是哪个，0,1,2...,就更新哪个速度
        nrows = excelList.nrows  # 行数
        for rowid in range(1,nrows):
            rowarray = excelList.row_values(rowid)  # 获取整行值，返回数组
            roadid = int(rowarray[0])  # 路段id
            speed = round(float(rowarray[2])*3.6,2) # 速度,km/h,保留两位小数
            qstr = """"roadID"=%d"""%(roadid)
            with  arcpy.da.UpdateCursor(speedTable, fieldlist, qstr) as tableUpdate:
                for rowu in tableUpdate:
                    rowu[indexL+1] = speed
                    tableUpdate.updateRow(rowu)
            print roadid
        print sheet,"表完成"

def speed_avg():
    "求得每种道路类型24个时段的平均速速,并插入到表格中,速度不为0的值的平均值"
    road_osm = "road_speed24"  # 道路数据,24个时间间隔
    workbook = xlwt.Workbook(encoding = 'utf-8')#
    sheet = workbook.add_sheet("roadspeed")
    colID=0#列数
    fieldList=["roadgrade"]
    sheet.write(0, colID,"roadgrade")
    colID+=1
    for i in range(24):#24个速度值
        field="roadSpeed%d_%d"%(i,i+1)
        fieldList.append(field)
        sheet.write(0, colID, field)
        colID += 1
    curLine = sorted(arcpy.da.SearchCursor(road_osm, fieldList))  # 搜索道路速度数据
    roadType=[u"快速路",u"主干道",u"次干道",u"支路"]
    rowID=1#行数
    for road in roadType :
        sheet.write(rowID, 0, road)
        colID=1
        for speedid in fieldList[1:]:#从0_1时开始,speedid=roadSpeed0_1
            speedSum=0#同种类型道路不为0的速度和
            num=0
            for row in curLine:
                roadtype=row[0]#道路类型
                indexl=fieldList[1:].index(speedid)#0代表roadSpeed0_1
                roadspeed=row[indexl+1]#速度
                if roadtype==road and roadspeed!=0:
                    speedSum+=roadspeed
                    num+=1
            avgspeed=round(speedSum/num,2)#速度均值,km/h,保留两位小数
            sheet.write(rowID, colID, avgspeed)
            colID+=1
            print speedid
        rowID+=1
        workbook.save("F:\\trafficdata\\speed\\roadTypeSpeed.xls")  # 保存数据
        print road,"完成"
def speed_all():
    "没有速度的路段使用同等道路等级平均速度代替"
    road_osm = "road_speedall24"  # 道路数据,24个时间间隔
    excelPath="F:\\trafficdata\\speed\\roadTypeSpeed.xls"#获得不同道路类型平均速度
    excelFile = xlrd.open_workbook(excelPath)
    excel = excelFile.sheet_by_name("roadspeed")
    avgSpeed=[]#[[],[],[],[]],长度为4，每项24个值。不同道路类型各时段平均速度,快速路、主干道、次干道、支路
    nrows = excel.nrows  # 行数
    for rowid in range(1, nrows):
        rowarray = excel.row_values(rowid)  # 获取整行值，返回数组
        avgSpeed.append(rowarray[1:])
    fieldList=["roadgrade"]#["roadgrade","roadSpeed0_1"...]
    for i in range(24):#24个速度值
        field="roadSpeed%d_%d"%(i,i+1)
        fieldList.append(field)
    with  arcpy.da.UpdateCursor(road_osm, fieldList) as tableUpdate:
        for rowu in tableUpdate:
            if rowu[0]==u'快速路':
                for kk in range(1,len(rowu)):
                    if rowu[kk]==0:
                        rowu[kk]=avgSpeed[0][kk-1]
                        tableUpdate.updateRow(rowu)
                        print rowu[0]
            elif rowu[0]==u'主干道':
                for kk in range(1,len(rowu)):
                    if rowu[kk]==0:
                        rowu[kk]=avgSpeed[1][kk-1]
                        tableUpdate.updateRow(rowu)
                        print rowu[0]
            elif rowu[0]==u'次干道':
                for kk in range(1,len(rowu)):
                    if rowu[kk]==0:
                        rowu[kk]=avgSpeed[2][kk-1]
                        tableUpdate.updateRow(rowu)
                        print rowu[0]
            if rowu[0]==u'支路':
                for kk in range(1,len(rowu)):
                    if rowu[kk]==0:
                        rowu[kk]=avgSpeed[3][kk-1]
                        tableUpdate.updateRow(rowu)
                        print rowu[0]
    del tableUpdate

#excel_table()
#speed_avg()
#speed_all()
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime
def speed_allold():
    "没有速度的路段使用相同道路名的路段速度的平均值，如果路段名称为nulldata则使用同等道路等级平均速度代替"
    road_osm = "road_speedall24"  # 道路数据,24个时间间隔
    excelPath="F:\\trafficdata\\speed\\roadTypeSpeed.xls"#获得不同道路类型平均速度
    excelFile = xlrd.open_workbook(excelPath)
    excel = excelFile.sheet_by_name("roadspeed")
    avgSpeed=[]#[[],[],[],[]],长度为4，每项24个值。不同道路类型各时段平均速度
    nrows = excel.nrows  # 行数
    for rowid in range(1, nrows):
        rowarray = excel.row_values(rowid)  # 获取整行值，返回数组
        avgSpeed.append(rowarray[1:])
    fieldList=["roadgrade"]#["roadgrade","roadSpeed0_1"...]
    for i in range(24):#24个速度值
        field="roadSpeed%d_%d"%(i,i+1)
        fieldList.append(field)
    #curLine = sorted(arcpy.da.SearchCursor(road_osm, fieldList))
    qstr = """"roadname"=nulldata"""#路段名称为nulldata则使用同等道路等级平均速度代替
    with  arcpy.da.UpdateCursor(road_osm, fieldList, qstr) as tableUpdate:
        for rowu in tableUpdate:
            if rowu[0]=='快速路':
                for kk in range(1,len(rowu)):
                    if rowu[kk]==0:
                        rowu[kk]=avgSpeed[0][kk-1]
                        tableUpdate.updateRow(rowu)
            elif rowu[0]=='主干道':
                for kk in range(1,len(rowu)):
                    if rowu[kk]==0:
                        rowu[kk]=avgSpeed[1][kk-1]
                        tableUpdate.updateRow(rowu)
            elif rowu[0]=='次干道':
                for kk in range(1,len(rowu)):
                    if rowu[kk]==0:
                        rowu[kk]=avgSpeed[2][kk-1]
                        tableUpdate.updateRow(rowu)
            if rowu[0]=='支路':
                for kk in range(1,len(rowu)):
                    if rowu[kk]==0:
                        rowu[kk]=avgSpeed[3][kk-1]
                        tableUpdate.updateRow(rowu)
    del tableUpdate
    qstr = """"roadname"<>nulldata"""#路段有名称的，速度为0的更新为所有同名称的道路速度均值
    fieldList.insert(1,"roadname")#添加名称字段["roadgrade","roadname","roadSpeed0_1"...]
    curLine = sorted(arcpy.da.SearchCursor(road_osm, fieldList,qstr))
    with  arcpy.da.UpdateCursor(road_osm, fieldList, qstr) as tableUpdate:
        for rowu in tableUpdate:
            roadname=rowu[1]#路名
            for line in curLine:
                if line[1]==roadname:
                    speedSum=11

            for mm in range(2,len(rowu)):
                if rowu[mm]==0:#速度为0
                    a=12