#-*- coding:utf-8 -*-
import datetime,os
beginTime=datetime.datetime.now()#程序开始时间
def taxi_extract():
    "从长宁区，每天原始文件中按车辆编号提取txt，提取后的txt并没有按照时间排序.注意20150424P.txt是指包括长宁区内的数据"
    taxiFile =open("F:\\trafficdata\\taxi\\data\\20150424carNo.txt","r")#车辆编号文件
    allFile=open("F:\\trafficdata\\taxi\\data\\20150424P.txt","r")#18号所有车辆数据
    writePath="F:\\trafficdata\\taxi\\data20150424\\"#写入文件路径,里面的txt并没有按照时间排序
    taxiList=[]#车辆编号.400辆，为字符串类型
    for row in taxiFile:
        taxiList.append(row[:-1])#每一行最后一项为\n
    taxiList=taxiList[101:501]
    taxiFile.close()
    j=1#读取总文件行数
    for readRow in allFile:
        line=readRow[:-1]#去除\n
        nIndex=line.index(',')#第一个逗号位置，前面为车辆ID
        carID=line[:nIndex]#车辆编号
        if carID in taxiList:
            writeFile = open(writePath+carID+".txt", "a")
            writeFile.write(readRow)
            writeFile.close()
        if j%10000==0:
            print j
        j+=1
    allFile.close()

def sort_byTime():
    "从上一步骤，长宁区每个车辆txt中，按照时间排序生成新的txt"
    txtPath="F:\\trafficdata\\taxi\\data20150418"#未按时间排序数据
    newPath="F:\\trafficdata\\taxi\\sort20150418"#按时间排序数据文件夹
    allTxt=[]#所有txt文件,005,0006
    for  files in os.listdir(txtPath):
        try:
            if files.split('.')[1]=='txt':
                allTxt.append(files.split('.')[0])
        except:
            continue
    for txt in allTxt:
        openFile=open(txtPath+"\\"+txt+".txt","r")
        writeFile=open(newPath+"\\"+txt+".txt","a")
        newData = []#按时间排序的数据
        for readRow in openFile:
            data = []
            line=readRow[:-1]
            time=line.split(',')[7]#按第二个时间排序
            newTime=datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            tIn=line.index(time)
            data.append(line[:tIn])
            data.append(newTime)
            data.append(line[tIn+len(time):])
            newData.append(data)
        newData=sorted(newData,key=lambda a_list: a_list[1])
        for data in newData:
            writeData=data[0]+str(data[1])+data[2]+"\n"
            writeFile.write(writeData)
        openFile.close()
        writeFile.close()
        print txt,"txt完成"

def get_taxiID():
    "从最大的原始文件中获取一共有多少车辆编号，包括全上海的数据。只获取1000辆车编号"
    allFile = open("D:\\lunwen\\shanghai\\taxidata\\20\\20\\part00000\\part00000.txt", "r")  # 20号上海所有车辆数据
    IDFile = open("D:\\lunwen\\shanghai\\taxidata\\20\\20\\part00000\\taxiID.txt", "a")#用于存储车辆编号的txt
    IDlist=[]#车辆编号列表
    rowid=0
    for readRow in allFile:
        try:
            line=readRow[:-1]#去除\n
            nIndex=line.index(',')#第一个逗号位置，前面为车辆ID
            carID=line[:nIndex]#车辆编号
            if carID not in IDlist:
                IDlist.append(carID)
            rowid+=1
            if rowid%100000==0:
                print rowid,len(IDlist)
            if len(IDlist)>=10000:#只获取10000辆车
                break
        except:
            continue
    allFile.close()
    print "总共车辆数：",len(IDlist)
    IDlist=sorted(IDlist)#从小到大排序
    for id in IDlist:
        IDFile.write(id + "\n")
    IDFile.close()

def get_Alldata():
    "从最大的原始文件中按编号提取txt，提取后并没有按时间排序，包括全上海的数据"
    allFile=open("D:\\lunwen\\shanghai\\taxidata\\20\\20\\part00000\\part00000.txt", "r")#20号上海所有车辆数据
    taxiFile = open("D:\\lunwen\\shanghai\\taxidata\\20\\20\\part00000\\taxiID.txt", "r")  # 用于存储车辆编号的txt
    writePath="D:\\lunwen\\shanghai\\taxidata\\20\\20\\part00000\\data20\\"#写入文件路径,里面的txt并没有按照时间排序
    taxiList=[]#车辆编号,为字符串类型
    for row in taxiFile:
        taxiList.append(row[:-1])#每一行最后一项为\n
    taxiList=taxiList[:100]#只取100辆
    taxiFile.close()
    j=1#读取总文件行数
    for readRow in allFile:
        try:
            line=readRow[:-1]#去除\n
            nIndex=line.index(',')#第一个逗号位置，前面为车辆ID
            carID=line[:nIndex]#车辆编号
            if carID in taxiList:
                writeFile = open(writePath+carID+".txt", "a")
                writeFile.write(readRow)
                writeFile.close()
            j += 1
            if j%100000==0:#读取总文件100000行即结束
                break
        except:
            continue
    allFile.close()

if __name__=="__main__":
    get_taxiID()
    #get_Alldata()
endTime=datetime.datetime.now()#结束时间
print "运行时间：",endTime-beginTime

