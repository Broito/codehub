# -*- coding: utf-8 -*-
import arcpy,math,re,datetime
from arcpy import env
probeginTime=datetime.datetime.now()#程序开始时间
roadsh="F:\\trafficdata\\speed\\data.gdb\\road_osm"
def insert3_point():
    "首先插入前三个点"
    global alllist, infid, rightroad, maxroad, proad_id, pin_fid
    infid,alllist,rightroad,maxroad=[],[],[],[]
    infid=IN_FID[:3]
    get3_list()
    first3_road()
    get3_table()

    proad_id=rightroad[-1]
    pin_fid=infid[-1]

def get3_list():
    "获得点序列所在路段编号列表,alllist,maxroad"
    global alllist, infid, rightroad, maxroad, proad_id, pin_fid
    for i in infid:
        vlist = []
        for row in curAll:
            if row[0]==i:
                vlist.append(row[1])
        alllist.append(vlist)
        maxroad.append(vlist[-1])#当前点分数最高路段编号

def first3_road():
    "计算三个点序列连通路段列表,rightroad"
    global alllist, infid, rightroad, maxroad, proad_id, pin_fid
    roadlist=[]#拓扑连通道路组合[[6752, 6752, 6752], [6752, 6752, 13874], [6752, 6752, 14474].....]
    scorelist=[]#每个路段组合分数[0.9551395616589868, 0.9306722605873221, 0.6950509325282139....]
    for fid1 in alllist[0]:
        line1=0
        for row in curLine:
            if row[1] == fid1:
                line1 = row[0]
                break
        for fid2 in alllist[1]:
            line2=0
            for row in curLine:
                if row[1] == fid2:
                    line2 = row[0]
                    break
            if line1.touches(line2) or fid1==fid2:
                for fid3 in alllist[2]:
                    line3 = 0
                    for row in curLine:
                        if row[1] == fid3:
                            line3 = row[0]
                            break
                    if line2.touches(line3) or fid3==fid2:
                        roadlist.append([fid1,fid2,fid3])
                        scorelist.append(cal_score(fid1,fid2,fid3))
                    else:
                        continue
            else:
                continue

    if len(roadlist)==0:#没有连通组合
        rightroad=maxroad
        #print '不连通组合:',infid[-1]
    else:
        rightroad=roadlist[scorelist.index(max(scorelist))]#有多个连通路段则选择分数最高的
def cal_score(fid1,fid2,fid3):
    "计算每个候选路段组合得分,scoresum"
    global alllist, infid, rightroad, maxroad, proad_id, pin_fid
    fid=[fid1,fid2,fid3]
    scoresum=0
    for i in range(len(infid)):
        for row in curAll:
            if row[0]==infid[i] and row[1]==fid[i]:
                scoresum+=row[8]
                break
    return scoresum
def get3_table():
    "将三个点正确路段选出并插入新的表，第一次插入前三个点,后面是两个点"
    global alllist, infid, rightroad, maxroad, proad_id, pin_fid
    for i in range(len(infid)):#第一次插入前三个点,后面是两个点
        for row in curAll:
            if row[0]==infid[i] and row[1]==rightroad[i]:
                rowf=[row[0],row[1],row[2],row[3],row[8],row[5],row[6],row[7]]
                curNew.insertRow(rowf)
                break

def insert_point():
    "插入剩余的点"
    global alllist, infid, rightroad, maxroad, proad_id, pin_fid

    j=(len(IN_FID)-3)/2 #需要执行插入次数,有可能最后一个点插入不进去
    for i in range(1,j+1):
        infid,alllist,rightroad,maxroad=[],[],[],[]
        infid=IN_FID[2*i+1:2*i+3]#只有两个点

        alllist.append([proad_id])#插入前一序列的最后一点路段编号
        maxroad.append(proad_id)
        get3_list()#获得点序列所在路段编号列表,alllist,maxroad
        
        infid.insert(0, pin_fid)#插入前一序列的最后一点infid
        first3_road()

        del rightroad[0]#删除第一个点,以便只插入后两个点
        del infid[0]
        get3_table()#只插入两个点

        proad_id=rightroad[-1]
        pin_fid=infid[-1]
def create_txt():
    "从表格生成点数据"
    global curAll, curLine, curNew
    del curAll, curLine, curNew
    arcpy.MakeXYEventLayer_management(newtable, "NEAR_X", "NEAR_Y", "valayer1",arcpy.SpatialReference(3857))
    arcpy.CopyFeatures_management("valayer1", mpoint)
    arcpy.Delete_management("valayer1")  # 删除临时数据


alllist=[]#[[6752, 13570, 13899, 14090], [6752], [6752, 13874, 14474]]三个点候选路段编号列表
infid=[]#三个点序列的IN_FID [1,2,3]，注意有可能不为1,2,3使用50米做缓冲区时，前三个点有可能找不到候选路段。00202就是6、7、8
rightroad=[]#三个点形成的最优连通路段[13570,6752,6752]
maxroad=[]#三个点分数最高的路段编号[13570,6752,6752]，当rightroad为空时，rightroad=maxroad
proad_id=6752#前点序列最后一点所在路段编号,rightroad[-1]
pin_fid=3#前点序列最后一点id,infid[-1]

neartable,newtable, mpoint= 0,0,0 # 生成一个新表用于存放连通表
curAll,curLine,curNew=0,0,0
IN_FID =0  # 所有点的IN_FID

for  day in range(18,25):#运行7天的数据
    dataPath="F:\\trafficdata\\speed\\matchResult\\201504%d.gdb"%(day)
    env.workspace = dataPath
    fileName = []  # 获得数据库下所有表格数据,0005,1637
    mPoint = arcpy.ListTables()
    for list in mPoint:
        if re.match(r"[t]", list):
            fileName.append(list.split('t')[1])

    for nearFile in fileName:
        try:
            neartable = "t"+nearFile #t0005
            newtable = "r"+nearFile  # 生成一个新表用于存放连通表
            mpoint = "m"+nearFile  # 匹配点
            arcpy.CreateTable_management(dataPath, newtable, "F:\\trafficdata\\speed\\data.gdb\\template", "")
            # 按得分从小到大排列，全局只搜索一次，变成矩阵
            curAll = sorted(arcpy.da.SearchCursor(neartable, ["IN_FID","NEAR_FID","NEAR_X","NEAR_Y","NEAR_DIST","Field8","Field11","distance","road_score"]),key=lambda a_list: a_list[8])
            curLine=sorted(arcpy.da.SearchCursor(roadsh,["SHAPE@","OID@"]),key=lambda a_list: a_list[1])#搜索长宁区道路数据
            curNew=arcpy.da.InsertCursor(newtable,["IN_FID","NEAR_FID","NEAR_X","NEAR_Y","road_score","time","speed","distance"])#插入的新表

            IN_FID = []  # 所有点的IN_FID
            for row in curAll:
                if row[0] not in IN_FID:
                    IN_FID.append(row[0])
                IN_FID = sorted(IN_FID)

            insert3_point()#插入第前三个点
            insert_point()#插入剩余的点
            create_txt()#从表格生成点数据
            print nearFile
        except:
            print  nearFile,"notmatchdata"
            continue
    print day,"完成"
proendTime=datetime.datetime.now()#结束时间
print "运行时间：",proendTime-probeginTime