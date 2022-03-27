# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import math
import os
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
##import matplotlib.pyplot as plt
from treeinterpreter import treeinterpreter as ti
'''
每棵树的构建都是基于训练集中有放回的样本（bootstrap sample）；
在每棵树构建过程中的节点分割时，不是在全部特征中去找最佳分割，而是在所有特征的一个随机子集中找最佳分割；
因为随机性，所以每棵树的偏差会有稍许增加（相对于单个非随机树的偏差），但是平均来看，会降低模型的方差，所以模型整体上会比较好
'''

'''
参数说明
    n_estimator: 随机森林中初始化树的数量，n_estimators is the number of trees in the forest, the default is 10;
    criterion: 评价节点分割的质量，criterion is to measure the quality of split,
        分类："gini": Gini impurity; "entropy": information gain (tree-specific)
        回归："mse": mean squared error; "mae": mean absolute error，the default is 'MSE'
    max_features: 当找到最佳节点分割时，所需的最大特征数量
    max_depth: 树的最大深度
'''

def demoRFRegr():
    from sklearn.datasets import make_regression
    X, y = make_regression(n_features=4, n_informative=2, random_state=0, shuffle=False)   # 构建用于回归的训练样本
    regr = RandomForestRegressor(max_depth=2, random_state=0)   # 构建一个随机森林回归器
    regr.fit(X, y)   # 用训练集对初始化的随机森林回归器进行训练
    print regr.feature_importances_   # 特征的重要性，所以随机森林可用于特征选取

def irisRFRegr():
    from sklearn.datasets import load_iris
    iris = load_iris()   # 加载sklearn自带的iris样例数据

    rfr = RandomForestRegressor()
    rfr.fit(iris.data[:150], iris.target[:150])
    print rfr.score(iris.data[:150], iris.target[:150])   # 预测的决定系数（coefficient of determination）R^2


def random_sample(df_data, labelColName, trainSize=0.75):
    '''
    根据随机数随机获取训练样本的索引和验证样本的索引（随机采样）
    params:
        sampleSum: 总的样本数
        sampleSize: 训练样本的比例，如0.75
    '''
    import random
    indice = range(df_data.shape[0])
    trainSampleIndex = random.sample(indice, int(math.ceil(len(indice)*trainSize)))    
    testSampleIndex = [i for i in indice if i not in trainSampleIndex]
    return trainSampleIndex, testSampleIndex

def extractSampleData(df_data, featureColumns, labelColumn, sampleIndex):
    '''
    根据DataFrame类型数据、特征列名（切片索引）、标签列名（索引）、样本行来获取数据，并返回特征列和标签列
    '''
    X = np.array(df_data.loc[sampleIndex, featureColumns])
    y = np.array(df_data.loc[sampleIndex, labelColumn])
    return X, y

def lqydRFRegr(train_data, train_label, test_data, test_label):
    '''
    根据训练数据训练随机森林回归模型，并将验证数据进行验证，同时给出各个指标的重要性
    '''
    regr = RandomForestRegressor(n_estimators=50, criterion='mse')
    regr.fit(train_data, train_label)
    feature_importances_ = regr.feature_importances_
    test_score = regr.score(test_data, test_label)   # 考虑将feature_importances作为指标重要性放入到预测中？
    return feature_importances_, test_score

def extractBestMTrees(train_data, train_label, labelColumn):
    estimator_err = np.zeros((300, 2))   # 训练300次
    n_estimators = range(1,301,1)
    plt.axis([1, 300, 0, 1])
    plt.ion()
    for i in n_estimators:
        print i 
        clfier = RandomForestClassifier(n_estimators=i, criterion='entropy', bootstrap=True, oob_score=True)
        clfier.fit(train_data, train_label)
        oob_score = clfier.oob_score_   # 袋外样本分类误差
        err_score = 1 - oob_score
        plt.scatter(i, err_score)
        plt.pause(0.1)
        estimator_err[i-1][0] = i
        estimator_err[i-1][1] = err_score
    df_estimator_err = pd.DataFrame(estimator_err, columns=['n_estimators', 'oob_error'])
    df_estimator_err.to_csv('n_estimators_{0}.csv'.format(labelColumn), index=False)
    
    
def crimeRFClfier(train_data, train_label, test_data, test_label):
    '''
    根据训练数据训练随机森林回归模型，并将验证数据进行验证，同时给出各个指标的重要性
    '''
    clfier = RandomForestClassifier(n_estimators=500, criterion='gini', bootstrap=True, oob_score=True)
    clfier.fit(train_data, train_label)
    feature_importances_ = clfier.feature_importances_
    test_score = clfier.score(test_data, test_label)   # 考虑将feature_importances作为指标重要性放入到预测中？
    oob_score = clfier.oob_score_   # 袋外样本分类得分
    return feature_importances_, test_score, oob_score, clfier

def crimeRFRegr(train_data, train_label, test_data, test_label):
    '''
    根据训练数据训练随机森林回归模型，并将验证数据进行验证，同时给出各个指标的重要性
    '''
    regr = RandomForestRegressor(n_estimators=500, criterion='mse', bootstrap=True, oob_score=True, max_features=0.33)
    regr.fit(train_data, train_label)
    feature_importances_ = regr.feature_importances_
    Rsq = regr.score(test_data, test_label)   # Returns the coefficient of determination R^2 of the prediction.
    oob_score = regr.oob_score_   # 袋外样本分类得分
    return feature_importances_, Rsq, oob_score, regr

def cross_validate(df_data, featureColumns, labelColumn, iterations=10, train_size=0.75):
    '''
    随机森林交叉验证，根据给定的数据集进行交叉验证
    '''
    from sklearn import model_selection   # 自0.20版本之后都将cross_validation下的类和函数都移到model_selection下面，新的CV iterator与原先也有变化
    X = df_data.loc[:, featureColumns]   # 根据特征列名提取出所有特征列
    y = df_data.loc[:, labelColumn]   # 根据标签列名提取出标签列
    estimator = RandomForestRegressor(n_estimators=50, criterion='mse')
    cv_generator = model_selection.ShuffleSplit(n_splits = iterations, train_size = train_size, random_state = 0)   # n_splits为分割次数
    # 对于cross_val_score中的cv决定了交叉验证的样本分割策略，cv可以有None/integer/cross-validation generator
    # 注：cv取None或者integer时，如果estimator是一个分类器（classifier）且标签是二分或多分类变量，则用StratifiedKFold；其他（如regressor）的情况用KFold
    scores = model_selection.cross_val_score(estimator, X, y, cv=cv_generator, scoring='r2')   # scoring's value in ['explained_variance', 'neg_mean_absolute_error', 'neg_mean_squared_error', 'neg_mean_squared_log_error', 'neg_median_absolute_error', 'r2']
    return scores


if __name__ == '__main__':
    filepath = r'../class1_kd.csv'
    df_data = pd.read_csv(filepath)
    trainSize = 0.1

    # 特征列    
    RSDQ_col = [10,22,24,25,32,33,34,35,36,37,38,39,40,41,42]
    FRSDQ_col = [5,10,22,24,25,30,32,33,34,35,37,39,40,41,42]
    LQ_col = [10,22,25,30,31,32,33,34,35,36,38,39,40,41,42,43]
    SQ_col = [10,15,22,31,32,33,34,35,36,37,38,39,40,41,42,43]
    WROD_col = [9,22,30,31,32,33,34,35,36,37,38,39,40,42,43]
    BL_col = [1,5,22,30,31,32,33,34,35,36,37,38,39,40,42]
    dict_columns = {'RSDQ_kd':RSDQ_col, 'FRSDQ_kd':FRSDQ_col, 'LQ_kd':LQ_col, 'SQ_kd':SQ_col, 'WROD_kd':WROD_col, 'BL_kd':BL_col}

    for labelColumn in dict_columns:
        # 标签列
        print labelColumn
        filterFeatureColumns = dict_columns[labelColumn]
        col = [str(i) for i in filterFeatureColumns]
        col_feats = ["X"+str(i) for i in filterFeatureColumns]

        # 随机采样并训练，获取模型特征重要性
        trainSampleIndex, testSampleIndex = random_sample(df_data, labelColumn, trainSize)
        allData = df_data.loc[:, col]; allLabel = df_data.loc[:, labelColumn]
        trainData, trainLabel = extractSampleData(df_data, col, labelColumn, trainSampleIndex)
        testData, testLabel = extractSampleData(df_data, col, labelColumn, testSampleIndex)
        feature_importances_, Rsq, oob_score, regr = crimeRFRegr(trainData, trainLabel, testData, testLabel)
        print oob_score, Rsq

        # 特征重要性输出
        imp = zip(filterFeatureColumns, feature_importances_)
        print "The importance of variables"
        df_imp = pd.DataFrame(imp)
        df_imp.columns = ["feats", "importance"]
##        df_imp.to_csv("importance//imp_{0}.csv".format(labelColumn), index = False)    


    ##    计算Contributions
        print "Calculating residual and contributions of training data"
        OID = np.array(df_data.OID[trainSampleIndex])
        pre, bias, contri = ti.predict(regr, trainData)
        residual = pre - trainLabel   # 计算残差
        df_resid = pd.DataFrame(np.vstack((OID, pre, trainLabel, residual)).T, columns = ['FID', 'Pre', labelColumn, 'residual'])
##        df_resid.to_csv("residual//resid_{0}1.csv".format(labelColumn), index = False)

        columns = [str(i) for i in filterFeatureColumns]
        columns.insert(0, 'FID')
        columns.insert(1, 'Pre')
        columns.insert(2, labelColumn)
        columns.insert(3, 'Bias')
        columns.extend(col_feats)
        oid_pre_bias = np.vstack((OID, trainLabel, pre, bias)).T
        oid_pre_bias_contri = np.append(oid_pre_bias, contri, axis = 1)
        oid_pre_bias_contri_feats = np.append(oid_pre_bias_contri, trainData, axis = 1)
        df_contri = pd.DataFrame(oid_pre_bias_contri_feats, columns = columns)
##        df_contri.to_csv("Figures//contri_{0}1.csv".format(labelColumn), index = False)

    ##  计算检验样本预测值与残差
        print "Calculating residual of test data"
        tOID = np.array(df_data.OID[testSampleIndex])
        tpre, tbias, tcontri = ti.predict(regr, testData)
        tresidual = tpre - testLabel   # 计算残差
        df_resid = pd.DataFrame(np.vstack((tOID, tpre, testLabel, tresidual)).T, columns = ['FID', 'Pre', labelColumn, 'residual'])
##        df_resid.to_csv("residual//resid_{0}2.csv".format(labelColumn), index = False)

    ##  计算所有样本的Contributions
        print "Calculating residual and contributions of all data"
        aOID = np.array(df_data.OID)
        apre, abias, acontri = ti.predict(regr, allData)
        aresidual = apre - allLabel   # 计算残差
        df_resid = pd.DataFrame(np.vstack((aOID, apre, allLabel, aresidual)).T, columns = ['FID', 'Pre', labelColumn, 'residual'])
##        df_resid.to_csv("residual//resid_{0}0.csv".format(labelColumn), index = False)

        columns = [str(i) for i in filterFeatureColumns]
        columns.insert(0, 'FID')
        columns.insert(1, 'Pre')
        columns.insert(2, labelColumn)
        columns.insert(3, 'Bias')
        columns.extend(col_feats)
        oid_pre_bias = np.vstack((aOID, allLabel, apre, abias)).T
        oid_pre_bias_contri = np.append(oid_pre_bias, acontri, axis = 1)
        oid_pre_bias_contri_feats = np.append(oid_pre_bias_contri, allData, axis = 1)
        df_contri = pd.DataFrame(oid_pre_bias_contri_feats, columns = columns)
##        df_contri.to_csv("Figures//contri_{0}0.csv".format(labelColumn), index = False)
        print '\n'

    ## 随机森林特征数
##    Xcol = []
##    for i in col:
##        Xcol.append(i)
##        print "\n Important variables: ", Xcol
##        trainSampleIndex, testSampleIndex = random_sample(df_data, labelColumn, trainSize)
##        trainData, trainLabel = extractSampleData(df_data, Xcol, labelColumn, trainSampleIndex)
##        testData, testLabel = extractSampleData(df_data, Xcol, labelColumn, testSampleIndex)
##        feature_importances_, test_score, oob_score, clfier = crimeRFClfier(trainData, trainLabel, testData, testLabel)
##        print "oob_score: ", oob_score
##        print "test_score: ", test_score
