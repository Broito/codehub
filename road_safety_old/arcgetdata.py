#-*-coding:utf-8-*-
import arcpy,math,os,datetime
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间

roadsh="F:\\trafficdata\\speed\\data.gdb\\road_osm"#道路数据
changning = "F:\\trafficdata\\speed\\data.gdb\\changning_web"#长宁区范围数据，用来提取点数据
spaWeb=arcpy.SpatialReference(3857)#web
spa1984=arcpy.SpatialReference(4326)#wgs_1984

valid_txt =0#
valayer=0#临时的txt生成点数据
point1984=0  #临时的wgs1984坐标系点数据
vpoint=0  #web投影坐标系统点数据
pointsh=0  #提取在长宁区以内的点
newpoint=0 #pointsh经过删除冗余的点。
neartable=0  #生成邻近的表格,此表格会添加road_score字段

#权重得分计算公式： dir_road车头朝向、NEAR_DIST距离、angle_road历史行驶方向
weight_str="math.fabs(math.cos( !dir_road! * math.pi / 180)) +1 / !NEAR_DIST! + math.fabs(math.cos( !angle_road! * math.pi / 180)) "

def create_point():
        "从txt生成点数据"
        arcpy.MakeXYEventLayer_management(valid_txt, "Field9", "Field10", valayer,spa1984)
        arcpy.CopyFeatures_management(valayer, point1984)
        arcpy.Project_management(point1984,vpoint,spaWeb)
        arcpy.Delete_management(point1984)#删除临时数据
        arcpy.Delete_management(valayer)  # 删除临时数据

        #删除不必要字段 #Field3是是否载客，Field8是GPS测定时间时间，Field11是速度，Field12是方向
        dropFields = ["Field2","Field4", "Field5", "Field6","Field7","Field9","Field10","Field13"]
        arcpy.DeleteField_management(vpoint, dropFields)
        arcpy.Clip_analysis(vpoint, changning, pointsh, "")
        arcpy.Delete_management(vpoint)#删除临时数据
def add_angle(x1,y1,x2,y2):
        "添加角度字段"
        a=math.atan2(x2-x1,y2-y1)
        if a>=0:
                return a*(180/math.pi)
        else:
                return (math.pi+a)*(180/math.pi)
def get_dis():
        "删除冗余点和更新距离字段和角度字段"
        arcpy.AddField_management(pointsh, "distance", "DOUBLE")#添加距离字段
        arcpy.AddField_management(pointsh, "angle", "DOUBLE")#添加角度字段,GPS点和前一个点连线和正北方向夹角
        cur=arcpy.da.UpdateCursor (pointsh,["SHAPE@XY","Field11","distance","angle","Field8","Field3"])#Field11速度,Field3是是否载客
        validrow=cur.next()
        for row in cur:#从第二行开始
                x1=validrow[0][0]
                y1=validrow[0][1]
                validtime=validrow[4]
                x2=row[0][0]
                y2=row[0][1]
                time=row[4]#当前点时间
                timeInter=(time-validtime).seconds#两个点时间间隔
                dis=math.sqrt(math.pow(x2-x1,2)+math.pow(y2-y1,2))
                len=25*timeInter#默认在上海时速25m/s
                if  dis<5 or dis>len or row[5]==1: #dis<5  删除在时间间隔内两点距离明显大于一般上海车辆时速下的距离,或者没有载客的点
                        cur.deleteRow()
                        continue
                else:
                        validrow=row
                        row[2]=dis
                        row[3]=add_angle(x1,y1,x2,y2)# 添加角度字段
                        cur.updateRow(row)#更新距离字段值和角度
        del cur
        curf=arcpy.da.UpdateCursor (pointsh,["OID@"])
        sum=0
        for row in curf:
                sum+=1
        if sum<21:#剩余点的个数小于21，则删除此数据
                arcpy.Delete_management(pointsh)  # 删除临时数据
                del curf
        else:
                curf.reset()#将游标重新置为起始位置
                curf.next()
                curf.deleteRow()#删除第一个点数据
                del curf
                arcpy.CopyFeatures_management(pointsh, newpoint)#删除行后生成新的要素，以便OID按顺序排序
                arcpy.Delete_management(pointsh)#删除临时数据

                search_road()  # 搜索缓冲区里的候选路段缓冲区为50米
                calculate_angle()  # 计算角度值
def search_road():
        "搜索缓冲区里的候选路段缓冲区为50米,设置最多候选路段为5"
        arcpy.GenerateNearTable_analysis(newpoint, roadsh, neartable, "50 Meters", "LOCATION", 'NO_ANGLE', "ALL", "5")
        #将表和newpoint join操作angle，angle字段
        arcpy.JoinField_management(neartable, "IN_FID", newpoint, "OBJECTID", ["angle","Field8","Field11","Field12","distance"])#Field12是GPS点航向角
        #将表和roadangle join操作CompassA字段
        arcpy.JoinField_management(neartable, "NEAR_FID", roadsh, "OBJECTID", ["CompassA"])#compassA是道路角度
def calculate_angle():
        "计算角度值dir_road是车头朝向和路段角度差、angle_road是GPS点和前一个点连线相对路段角度差"
        arcpy.AddField_management(neartable, "direction", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(neartable, "direction", "!Field12!-180 if !Field12!>180 else !Field12!", "PYTHON_9.3", "")
        arcpy.AddField_management(neartable, "angle_road", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(neartable, "dir_road", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(neartable, "angle_road", "math.fabs( !angle! - !CompassA! )", "PYTHON_9.3", "")
        arcpy.CalculateField_management(neartable, "dir_road", "math.fabs( !direction! - !CompassA! )", "PYTHON_9.3", "")
        arcpy.AddField_management(neartable, "road_score", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(neartable, "road_score", weight_str, "PYTHON_9.3", "")
        #将得分为null的road_score赋值为10000
        arcpy.CalculateField_management(neartable, "road_score", "cal_score( !road_score! )", "PYTHON_9.3", "def cal_score(score):\\n  if score is None:\\n    return 10000\\n  else:\\n    return score\\n")

        # dropFields = ["Field12","angle","CompassA","direction","angle_road","dir_road"]
        # arcpy.DeleteField_management(neartable, dropFields)

for day in range(18,19):#运行18
        env.workspace = "F:\\trafficdata\\speed\\matchResult\\201504%d.gdb"%(day)
        txtPath="F:\\trafficdata\\speed\\201504%d"%(day)  #txt所在路径
        allTxt=[]#所有txt文件,005,0006
        for  files in os.listdir(txtPath):
                try:
                        if files.split('.')[1]=='txt':
                                allTxt.append(files.split('.')[0])
                except:
                        continue
        for txt1 in allTxt:
                try:
                        valid_txt = txtPath+"\\" + txt1 + ".txt"
                        valayer = "va" + txt1  # 临时的txt生成点数据
                        point1984 = "po" + txt1  # 临时的wgs1984坐标系点数据
                        vpoint = "vp" + txt1  # web投影坐标系统点数据
                        pointsh = "sh" + txt1  # 提取在长宁区以内的点
                        newpoint = "p" + txt1  # pointsh经过删除冗余的点。
                        neartable = "t" + txt1  # 生成邻近的表格,此表格会添加road_score字段
                        create_point()#生成点
                        get_dis()#删除冗余点
                        print txt1
                except:
                        print txt1,"notmatchdata"
                        continue
        print day,"完成"
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime


        
                


        
        
        
        
        
        
        
        



