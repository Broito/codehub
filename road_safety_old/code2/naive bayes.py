# Example of Naive Bayes implemented from Scratch in Python
import csv
import random
import math
import arcpy,xlrd,xlwt,datetime
def mean(numbers):
    return sum(numbers) / float(len(numbers))

def stdev(numbers):
    avg = mean(numbers)
    variance = sum([pow(x - avg, 2) for x in numbers]) / float(len(numbers) - 1)
    return math.sqrt(variance)
def openexcel():
    excelPath = 'C:\\GPS\\xls\\hour\\speedALL.xls' #
    excelFile = xlrd.open_workbook(excelPath)
    excelall = excelFile.sheet_names()
    allList = []
    unallList = []
    n = 3
    for sheet in excelall:
        excelList = excelFile.sheet_by_name(sheet)
        nrows = excelList.nrows
        for i in range(1,nrows):
            rowarray = excelList.row_values(i)
            rowid = int(rowarray[0])
            carnum = float(rowarray[1])
            speed = float(rowarray[2])
            if carnum!= 0:
                allList.append([rowid,carnum,speed])
            else:
                unallList.append([rowid, carnum, speed])
    if len(allList)%n == 0:
        length = len(allList)/n
    else:
        length = len(allList)//n+1
    speedList = sorted(allList,key=lambda a_list: a_list[2])
    speed = []
    times = []
    for i in range(0,n):
        speed.append([])
        times.append([])
    for i in range(0,len(speedList)):
        if i<= length:
            speed[0].append(speedList[i][2])
        elif i<=2*length:
            speed[1].append(speedList[i][2])
        else:
            speed[2].append(speedList[i][2])
    timesList = sorted(allList, key=lambda a_list: a_list[1])
    for i in range(0,len(timesList)):
        if i<= length:
            times[0].append(timesList[i][1])
        elif i<=2*length:
            times[1].append(timesList[i][1])
        else:
            times[2].append(timesList[i][1])
    return speed,times,allList,unallList


def calculateProbability(x, mean, stdev):
    exponent = math.exp(-(math.pow(x - mean, 2) / (2 * math.pow(stdev, 2))))
    return (1 / (math.sqrt(2 * math.pi) * stdev)) * exponent

def calculateClassProbabilities(summaries, inputVector):
    probabilities = {}
    for classValue, classSummaries in summaries.iteritems():
        probabilities[classValue] = 1
        for i in range(len(classSummaries)):
            mean, stdev = classSummaries[i]
            x = inputVector[i]
            probabilities[classValue] *= calculateProbability(x, mean, stdev)
    return probabilities

def predict(summaries, inputVector):
    probabilities = calculateClassProbabilities(summaries, inputVector)
    bestLabel, bestProb = None, -1
    for classValue, probability in probabilities.iteritems():
        if bestLabel is None or probability > bestProb:
            bestProb = probability
            bestLabel = classValue
    return bestLabel

def getPredictions(summaries, testSet):
    predictions = []
    for i in range(len(testSet)):
        result = predict(summaries, testSet[i])
        predictions.append(result)
    return predictions

def getroadgrade(path):
    A = open(path,'r')
    roadgrade = []
    for line in A:
        a,b,c = line.split(',')
        roadgrade.append(b)
    return roadgrade
def main():
    speed,times,allList,unallList = openexcel()
    path = 'c:\\GPS\\xls\\roadtable.csv'
    rg = getroadgrade(path)
##    Summary = {0: [(mean(speed[0]), stdev(speed[0])), (mean(times[0]), stdev(times[0]))],
##            1: [(mean(speed[1]), stdev(speed[1])), (mean(times[1]), stdev(times[1]))],
##               2: [(mean(speed[2]), stdev(speed[2])), (mean(times[2]), stdev(times[2]))]}
##    print Summary
    Summary = {0: [(17.546379451255778, 4.568615088196603), (1.4860621595642423, 0.6533061146723533)],
     1: [(32.12660486740256, 4.481031941261179), (7.873076923076923, 3.936565721931155)],
     2: [(54.07442150788375, 9.858515401623876), (134.67564966313762, 232.1552927167413)]}
    print len(allList),len(unallList)
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('allroadspeed')
    sheet.write(0, 0, "roadID")
    sheet.write(0, 1, "carNumber")
    sheet.write(0, 2, "roadSpeed")
    sheet.write(0, 3, "class")
    x = []
    for i in range(0,3):
        x.append(0)
    y = [0,0,0,0]
    for i in range(0,len(allList)):
        testSet  = []
        testSet.append(allList[i][2])
        testSet.append(allList[i][1])
        predictions = predict(Summary, testSet)
        if predictions == 2:
            zz = rg[int(allList[i][0]-1)]
            if zz == '快速路':
                y[0] = y[0]+1
            elif zz == '主干道':
                y[1] = y[1]+1
            elif zz == '次干道':
                y[2] = y[2]+1
            elif zz == '支路':
                y[3] = y[3]+1
            else:
                pass
        x[int(predictions)] = x[int(predictions)] + 1
        sheet.write(i + 1, 0, allList[i][0])
        sheet.write(i + 1, 1, allList[i][1])
        sheet.write(i + 1, 2, allList[i][2])
        sheet.write(i + 1, 3, predictions)
    for i in range(0,len(unallList)):
        sheet.write(i + 1+len(allList), 0, unallList[i][0])
        sheet.write(i + 1+len(allList), 1, unallList[i][1])
        sheet.write(i + 1+len(allList), 2, unallList[i][2])
        sheet.write(i + 1+len(allList), 3, -1)
    print y
    for i in y:
        print float(i)/sum(y)
    saveFile = "C:\\GPS\\xls\\hour1\\bayesALL1.xls"
    workbook.save(saveFile)
    print x
    for i in range(0,3):
        print float(x[i])/sum(x)
    # splitRatio = 0.67
    # dataset = loadCsv(filename)
    #
    #
    # trainingSet, testSet = splitDataset(dataset, splitRatio)
    # print('Split {0} rows into train={1} and test={2} rows').format(len(dataset), len(trainingSet), len(testSet))
    # # prepare model
    # summaries = summarizeByClass(trainingSet)
    # # test model
    # predictions = getPredictions(summaries, testSet)
    # accuracy = getAccuracy(testSet, predictions)
    # print('Accuracy: {0}%').format(accuracy)
main()
