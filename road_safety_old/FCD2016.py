#-*- coding:utf-8 -*-
import datetime,os
beginTime=datetime.datetime.now()#程序开始时间

def get_newHT1603():
    "将一天所有的长宁区点提出放入到一个txt中"
    dayList=["01","02","03","04","05","06","07"]#7天数据
    for day in dayList:
        filePath = "D:\\FCD2016\\HT1603%s\\%s\\"%(day,day)  # 每天的原始数据
        writePath="D:\\FCD2016\\newHT1603\\1603%s.txt"%(day)
        writeFile = open(writePath, "a")#一天24小时的txt夹写入一个txt,160301.txt
        hourList=[]#24个小时文件夹
        for i in range(24):
            if i<10:
                hourList.append("0"+str(i))
            else:
                hourList.append(str(i))
        for hour in hourList:
            txtPath=filePath+'%s\\'%(hour)
            allTxt=[]#所有00时的txt文件,1603010000,1603010001
            for  files in os.listdir(txtPath):
                try:
                    if files.split('.')[1]=='txt':
                        allTxt.append(files.split('.')[0])
                except:
                    continue
            for txt in allTxt:
                taxiFile =open(txtPath+txt+".txt","r")#打开1603010000.txt
                for readRow in taxiFile:
                    line = readRow[:-1].split('|')  # 去除\n,按照|分割
                    newLine=[]#获得想要的字段，和2015年数据相匹配
                    newLine.append(line[0])
                    newLine.extend(line[2:7])
                    newLine.extend(line[8:15])
                    if float(newLine[8])>121.318787 and float(newLine[8])<121.443404 and float(newLine[9])>31.168242 and float(newLine[9])<31.253409:
                        writeFile.write(','.join(newLine)+"\n")
                taxiFile.close()
                print txt
            print hour,"完成"
        writeFile.close()

def get_carNum():
    "获得车辆编号文件,500辆即可"
    dayList = ["01", "02", "03", "04", "05", "06", "07"]  # 7天数据
    for day in dayList:
        filePath = "D:\\FCD2016\\newHT1603\\1603%s.txt"%(day)
        writePath = "D:\\FCD2016\\newHT1603\\1603%scarNo.txt"%(day)  #车辆编号文件
        openFile = open(filePath, "r")  # 打开
        carNum=[]#车辆编号,字符串，长度为500即停止
        for readRow in openFile:
            num=readRow[:-1].split(',')[0]#车辆编号
            if num not in carNum:
                carNum.append(num)
            if len(carNum)==500:
                break
        writeFile=open(writePath,"a")
        for car in carNum:
            writeFile.write(car+"\n")
        openFile.close()
        writeFile.close()
def get_eachCar():
    "按车辆编号分别生成txt"
    dayList = ["01", "02", "03", "04", "05", "06", "07"]  # 7天数据
    for day in dayList:
        taxiPath="D:\\FCD2016\\newHT1603\\1603%scarNo.txt"%(day)
        allPath="D:\\FCD2016\\newHT1603\\1603%s.txt"%(day)
        writePath = "D:\\FCD2016\\Car1603%s\\"%(day)  # 写入文件路径
        taxiFile = open(taxiPath, "r")  # 车辆编号文件
        allFile = open(allPath, "r")  # 所有车辆数据
        taxiList = []  # 车辆编号 500辆，为字符串类型
        for row in taxiFile:
            taxiList.append(row[:-1])  # 每一行最后一项为\n
        taxiFile.close()
        j = 1  # 读取总文件行数
        for readRow in allFile:
            line = readRow[:-1]  # 去除\n
            nIndex = line.index(',')  # 第一个逗号位置，前面为车辆ID
            carID = line[:nIndex]  # 车辆编号
            if carID in taxiList:
                writeFile = open(writePath + carID + ".txt", "a")
                writeFile.write(readRow)
                writeFile.close()
            if j % 10000 == 0:
                print j
            j += 1
        allFile.close()


def sort_time():
    "按时间排序每个txt"
    dayList = ["01", "02", "03", "04", "05", "06", "07"]  # 7天数据
    for day in dayList:
        txtPath = "D:\\FCD2016\\Car1603%s"%(day)  # 未按时间排序文件夹
        newPath = "D:\\FCD2016\\sort1603%s"%(day)  # 按时间排序数据文件夹
        allTxt = []  # 所有txt文件,005,0006
        for files in os.listdir(txtPath):
            try:
                if files.split('.')[1] == 'txt':
                    allTxt.append(files.split('.')[0])
            except:
                continue
        for txt in allTxt:
            openFile = open(txtPath + "\\" + txt + ".txt", "r")
            writeFile = open(newPath + "\\" + txt + ".txt", "a")
            newData = []  # 按时间排序的数据
            for readRow in openFile:
                data = []
                line = readRow[:-1]
                time = line.split(',')[7]  # 按第二个时间排序
                newTime = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                tIn = line.index(time)
                data.append(line[:tIn])
                data.append(newTime)
                data.append(line[tIn + len(time):])
                newData.append(data)
            newData = sorted(newData, key=lambda a_list: a_list[1])
            for data in newData:
                writeData = data[0] + str(data[1]) + data[2] + "\n"
                writeFile.write(writeData)
            openFile.close()
            writeFile.close()
            print txt, "txt完成"

#get_newHT1603()
#get_carNum()
#get_eachCar()
#sort_time()

endTime=datetime.datetime.now()#结束时间
print "运行时间：",endTime-beginTime