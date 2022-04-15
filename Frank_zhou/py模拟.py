# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 09:27:20 2022

@author: Frank
"""

import random


N = 10000  #总人数
R0 = 3     #R0
positive = 1 #初始病人数
nt = positive #当前筛出病人数
nt_left=1 #未筛出来
incub = []  #潜伏期不同天数的病人
incubation = [1,2,2,2,3,3,3,4,5,6,7] #潜伏期，需要一个分布
day = 0  #时间
screen = [1,2,4,6,10,13,15] #筛查频次
power_s = 0.15 #筛查效率
n = 999  #模拟次数
period = 30 #模拟周期天数
p_fluc = [] #每天病人数变化
result = []

# incub_d 当天新生成的潜伏期病人

for t in range(n):
    
    for i in range(period):
        print(incub)
        p_fluc.append(nt)
        day_n = i
        incub = [x-1 for x in incub]  #潜伏期减少一天
    
    #数潜伏期变为病人数
        for x in incub:
            if x == 0:
                nt_left = nt_left + 1
        if day_n in screen:
            incub_dn =  int(nt_left*R0)
            for ii in range(incub_dn):
                incub.append(random.sample(incubation, 1))
        
        nt_left = int(nt*(power_s)+1)
        nt = nt - nt_left
    result.append(p_fluc)


    
    
    
            
    
    
            
            
            