import pandas as pd
import json
import requests
import re
import math

ak = 'Y1tGs5ksfGdVKXxiaHI4qPp6igOtkG65'    #ak需要去百度地图申请

def getlnglat(address):
    url = 'http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}&callback=showLocation'.format(address,ak)

    res = requests.get(url)
    results = json.loads(re.findall(r'\((.*?)\)',res.text)[0])

    x = float(results['result']['location']['lng'])#获取经度并写入
    y = float(results['result']['location']['lat'])#获取纬度并写入
    
    return 
 
def invert_geocoding(baidu_x,baidu_y):
    url = f'https://api.map.baidu.com/reverse_geocoding/v3/?ak={ak}&output=json&coordtype=bd09ll&location={baidu_y},{baidu_x}&extensions_town=true&extensions_road=true'
    print(url)


    res = requests.get(url)
    print(res.text)
    results = json.loads(res.text)

    province = results['result']['addressComponent']['province']
    city = results['result']['addressComponent']['city']
    district = results['result']['addressComponent']['district']
    town = results['result']['addressComponent']['town']
    street = results['result']['addressComponent']['street']

    return province,city,district,town,street

# 测试
invert_geocoding(121.460115,31.036755)