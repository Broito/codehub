import csv
import random
import math
import arcpy,xlrd,xlwt,datetime
def getroadgrade(path):
    A = open(path,'r')
    roadgrade = []
    for line in A:
        a,b,c,d = line.split(',')
        roadgrade.append(b)
    return roadgrade
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
    return allList
def main():
    allList= openexcel()
    print len(allList)
    path = 'c:\\GPS\\xls\\roadtable.csv'
    rg = getroadgrade(path)
    x = []
    y = []
    for i in range(0,4):
        y.append([])
    for i in range(0,len(allList)):
        zz = rg[int(allList[i][0]-1)]
        if zz == '快速路':
            y[0].append(allList[i][2])
        elif zz == '主干道':
            y[1].append(allList[i][2])
        elif zz == '次干道':
            y[2].append(allList[i][2])
        elif zz == '支路':
            y[3].append(allList[i][2])
        else:
            pass
    for i in y:
        print mean(i),len(i)
main()
