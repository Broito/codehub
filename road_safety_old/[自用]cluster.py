# -*- coding: utf-8 -*-
import arcpy,datetime,math,xlwt
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间

def select_centerpoint():
    "在道路上每隔10米生成一个点"
    env.workspace = r"E:\FloatVehicle2019\cluster.mdb"
    curline=arcpy.da.SearchCursor("road_osm200",["SHAPE@",'roadid','acci18_20','acci20_24','acci24_6'])
    curpoint=arcpy.da.InsertCursor("center_road_18_20_24_6",["SHAPE@",'roadid','acci18_20','acci20_24','acci24_6','newoid'])
    for row in curline:
        line=row[0]
        roadid = row[1]
        leng=line.length#线的剩余长度
        cutlen=leng/2#截取线的长度
        pt=line.positionAlongLine(cutlen)
        curpoint.insertRow([pt,roadid,row[2],row[3],row[4],roadid])


def get_geodata():
    "将2015年12个不同时间段事故数添加到路段上，每两小时一个时间"
env.workspace = r"E:\\FloatVehicle2019\\cluster.mdb"
arcpy.env.overwriteOutput = True
cutRoad="road_osm200"#路段数据
geo2015="geo2015"
    # for i in range(0,24,2):
accifield="acci%d_%d"%(24,6)#添加的字段
arcpy.AddField_management(cutRoad, accifield, "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
qstr="""[timegrade] >%d AND [timegrade] <%d"""%(0,7)
selectgeo="selectgeo"
arcpy.Select_analysis(geo2015, selectgeo, qstr)
neartable="neartable"
fretable="fretable"
arcpy.GenerateNearTable_analysis(selectgeo, cutRoad, neartable, "", "NO_LOCATION", "NO_ANGLE", "CLOSEST", "0")
arcpy.Frequency_analysis(neartable, fretable, "NEAR_FID", "")
arcpy.JoinField_management(cutRoad, "OBJECTID", fretable, "NEAR_FID", "FREQUENCY")
arcpy.CalculateField_management(cutRoad, accifield, "!FREQUENCY!", "PYTHON_9.3", "")
arcpy.DeleteField_management(cutRoad, ["FREQUENCY"])
arcpy.Delete_management(neartable)
arcpy.Delete_management(fretable)
arcpy.Delete_management(selectgeo)
print accifield

def get_service():
    "计算2015年12个不同时间段密度"
env.workspace = r"E:\FloatVehicle2019\cluster.mdb"
workbook = xlwt.Workbook()
sheet = workbook.add_sheet("clusteraltime")
sheet.write(0, 0, "newoid")
# acciFiled=[]#center_road 中各时间段事故数字段,共12个
# col=1
# for i in range(0,24,2):
#     den="density%d_%d"%(i,i+2)
#     sheet.write(0,col, den)
#     acci="acci%d_%d"%(i,i+2)
#     acciFiled.append(acci)
#     col+=1
sheet.write(0,1,'density18_6')
rowID=1
searchFiled= ["ToCumul_Length","newoid"]
searchFiled.extend(['density18_6'])

arcpy.CheckOutExtension("Network")
networkND = "network\\network_ND"#网络数据集
centerRoad = "center_road_18_6"#中心点数据
seardis = 200 #真实的搜索半径
bandWidth = "200"  # 在服务区工具里，85米搜索半径相当于100米
curCenter = sorted(arcpy.da.SearchCursor(centerRoad, ["SHAPE@", "newoid"],"""[newoid] >0 AND [newoid]<2300"""), key=lambda a_list: a_list[1])  # 搜索道路中心点数据
for point in curCenter[5]:
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
        curJoin = sorted(arcpy.da.SearchCursor(join_line_point, searchFiled,""""newoid" IS NOT null"""))
        if len(curJoin)!=0:
            sheet.write(rowID, 0, point[1])  # 写入newoid
            for yearNum in range(len(acciFiled)):#执行时间段，共3个
                sumKernel = 0 # 当前点的密度值
                nowID = 0  # 用于记录当前点是否有事故数
                for row in curJoin:
                    dis = float(math.pow(row[0], 2)) / (2 * math.pow(seardis, 2))  # 使用高斯密度函数
                    if row[1]== point[1] and nowID==1:#表示当前事故已经计算过
                        continue
                    if  row[1]== point[1] :  # 说明当前点有事故数，关联表中有两条记录，只使用一条，并且距离不能使用ToCumul_Length，应该为0,
                        dis=0
                        nowID=1
                    kernel=(1.0/math.sqrt(2*math.pi))*math.exp(-dis)#当前点的一个密度值
                    kernel=kernel*row[2+yearNum]#有多少事故点就计算多少次
                    sumKernel+=kernel
                sumKernel=sumKernel/seardis *1000 #除以搜索半径,密度值为每千米
                colID=1+yearNum
                sheet.write(rowID, colID, sumKernel)  # 写入密度
        rowID+=1
        arcpy.Delete_management(serviceName, "")#删除临时的服务图层
        arcpy.Delete_management(join_line_point)  # 删除临时数据
        del curJoin
        print point[1]
        workbook.save("E:\\FloatVehicle2019\\cluster_18_6.xls")  # 保存数据
    except:
        print point[1],"data_wrong"#当前点没有获得值
del curCenter

#get_geodata()
get_service()

proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime
