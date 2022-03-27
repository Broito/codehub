# -*- coding: utf-8 -*-
import arcpy,datetime,math,xlwt
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间
def cut_line():
    "在道路上每隔10米生成一个点"
    env.workspace = "F:\\trafficdata\\cluster\\cluster.gdb"
    curline=arcpy.da.SearchCursor("road_osm",["SHAPE@"])
    curpoint=arcpy.da.InsertCursor("cutpoint",["SHAPE@"])
    for row in curline:
        line=row[0]
        leng=line.length#线的剩余长度
        cutlen=10#截取线的长度
        while (leng>10 and leng>15):#如果剩余路段小于15米则不分割
            pt=line.positionAlongLine(cutlen)
            curpoint.insertRow([pt])
            leng=leng-10 #剩余长度
            cutlen=cutlen+10

def get_service():
    "计算2012至2015所有年份密度"
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("cluster")
    sheet.write(0, 0, "newoid")
    sheet.write(0, 1, "density2012")
    sheet.write(0, 2, "density2013")
    sheet.write(0, 3, "density2014")
    sheet.write(0, 4, "density2015")
    rowID=1
    env.workspace = "F:\\trafficdata\\cluster\\cluster.gdb"
    arcpy.CheckOutExtension("Network")
    networkND = "network\\network_ND"#网络数据集
    centerRoad = "center_road"#中心点数据
    seardis=500 #真实的搜索半径
    bandWidth = "500"  # 在服务区工具里，85米搜索半径相当于100米
    curCenter = sorted(arcpy.da.SearchCursor(centerRoad, ["SHAPE@", "newoid"],""""newoid" >29900 AND "newoid"<30000"""), key=lambda a_list: a_list[1])  # 搜索道路中心点数据
    for point in curCenter:
        try:
            facility=point[0]
            #outLine = "outline%d"%(point[1])  #输出的线
            serviceName = "serviceN%d"%(point[1])  # 服务区名称
            Lines = "%s\\Lines" % (serviceName)  # 服务区里面的线图层
            join_line_point="join_line_point%d"%(point[1])#路线和中心点关联的数据，最后是一个线数据
            arcpy.MakeServiceAreaLayer_na(networkND, serviceName, "Length", "TRAVEL_FROM", bandWidth, "NO_POLYS", "NO_MERGE", "RINGS","TRUE_LINES", "NON_OVERLAP", "NO_SPLIT", "", "", "ALLOW_UTURNS", "", "NO_TRIM_POLYS","", "NO_LINES_SOURCE_FIELDS", "NO_HIERARCHY", "")
            arcpy.AddLocations_na(serviceName, "Facilities", facility, "", "")
            arcpy.Solve_na(serviceName, "SKIP", "TERMINATE", "")
            #arcpy.CopyFeatures_management(Lines, outLine, "", "0", "0", "0")
            arcpy.SpatialJoin_analysis(Lines, centerRoad, join_line_point)
            curJoin = sorted(arcpy.da.SearchCursor(join_line_point, ["ToCumul_Length","newoid","acci2012","acci2013","acci2014","acci2015"],""""newoid" IS NOT null"""))
            if len(curJoin)!=0:
                sheet.write(rowID, 0, point[1])  # 写入newoid
                for yearNum in range(4):#执行四个年份
                    sumKernel = 0 # 当前点的密度值
                    nowID = 0  # 用于记录当前点是否有事故数
                    for row  in curJoin:
                        dis = float(math.pow(row[0], 2)) / (2 * math.pow(seardis, 2))  # 使用高斯密度函数
                        if row[1]== point[1] and nowID==1:#表示当前事故已经计算过
                            continue
                        if  row[1]== point[1] :  # 说明当前点有事故数，关联表中有两条记录，只使用一条，并且距离不能使用ToCumul_Length，应该为0,
                            dis=0
                            nowID=1
                        kernel=(1.0/math.sqrt(2*math.pi))*math.exp(-dis)#当前点的一个密度值
                        kernel=kernel*row[2+yearNum]#有多少事故点就计算多少次
                        sumKernel+=kernel
                    sumKernel=sumKernel/seardis#除以搜索半径
                    colID=1+yearNum
                    sheet.write(rowID, colID, sumKernel)  # 写入密度
            rowID+=1
            arcpy.Delete_management(serviceName, "")#删除临时的服务图层
            arcpy.Delete_management(join_line_point)  # 删除临时数据
            del curJoin
            print point[1]
            workbook.save("F:\\trafficdata\\cluster500.xls")  # 保存数据
        except:
            print point[1],"data_wrong"#当前点没有获得值
    del curCenter
get_service()

proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime
