# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 10:44:08 2021

@author: Frank
"""


import pandas as pd
import json
import requests
import re

ak = 'Y1tGs5ksfGdVKXxiaHI4qPp6igOtkG65'    #ak需要去百度地图申请
 
def getlnglat(address):
    url = 'http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}&callback=showLocation'.format(address,ak)

    res = requests.get(url)
    results = json.loads(re.findall(r'\((.*?)\)',res.text)[0])
    
    #json_data = res.text
    return results
 
inpath=r'D:\py_test\data.xlsx'
outpath=r'D:\py_test\Baidu.xlsx'
df = pd.read_excel(inpath)
df['lng'] = 'collng'#创建新列存放经度
df['lat'] = 'collat'#创建新列存放纬度
for i in df.values:
    b = i[2]  #第一列的地址
    print(b)
    ind=i[0]-1
    json_data = getlnglat(b)
    print(json_data)
    print(type(json_data))
    x = json_data['result']['location']['lng']#获取经度并写入
    y = json_data['result']['location']['lat']#获取纬度并写入
    df['lng'][ind]=float(x)
    df['lat'][ind]=float(y)

df
df.to_excel(outpath)