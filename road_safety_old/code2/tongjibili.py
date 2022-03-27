import csv
import random
import math
import arcpy,xlrd,xlwt,datetime
def getroadgrade(path):
    A = open(path,'r')
    roadgrade = []
    roadlen = []
    for line in A:
        a,b,c,d = line.split(',')
        e = d.split('\n')[0]
        roadgrade.append(b)
        roadlen.append(float(e))
    return roadgrade,roadlen
def mean(numbers):
    return sum(numbers) / float(len(numbers))
def openexcel():
    excelPath = 'C:\\GPS\\xls\\3.20\\speedALL.xls' #
    excelFile = xlrd.open_workbook(excelPath)
    excelall = excelFile.sheet_names()
    allList = []
    unallList = []
    for sheet in excelall:
        excelList = excelFile.sheet_by_name(sheet)
        nrows = excelList.nrows
        for i in range(1,nrows):
            rowarray = excelList.row_values(i)
            rowid = int(rowarray[0])
            carnum = float(rowarray[1])
            speed = float(rowarray[2])
            if carnum !=0:               
                allList.append([rowid,carnum,speed])
            else:
                unallList.append([rowid,carnum,speed])
    return allList,unallList
def main():
    allList,unallList= openexcel()
    print len(allList)
    path = 'c:\\GPS\\xls\\roadtable.csv'
    rg,rglen = getroadgrade(path)
    print rg[1]
    x = []
    y = [0,0,0,0]
    yl = [0,0,0,0]
    for i in range(0,len(allList)):
        zz = rg[int(allList[i][0]-1)]
        zz1 = rglen[int(allList[i][0]-1)]
        if zz == '快速路':
            y[0]  = y[0]+ 1
            yl[0] = yl[0] + zz1            
        elif zz == '主干道':
            y[1]= y[1]+ 1
            yl[1] = yl[1] + zz1
        elif zz == '次干道':
            y[2]= y[2]+ 1
            yl[2] = yl[2] + zz1
        elif zz == '支路':
            y[3]= y[3]+ 1
            yl[3] = yl[3] + zz1
        else:
            pass
    sumlen = [0,0,0,0]
    for i in range(0,43930):
        zz = rg[i]
        zz1 = rglen[i]
        
        if zz == '快速路':
            sumlen[0] = sumlen[0]+zz1           
        elif zz == '主干道':
            sumlen[1] = sumlen[1]+zz1
        elif zz == '次干道':
            sumlen[2] = sumlen[2]+zz1
        elif zz == '支路':
            sumlen[3] = sumlen[3]+zz1
        else:
            pass
    print yl,sumlen
    for i in range(0,4):
        print yl[i]/sumlen[i]
main()
