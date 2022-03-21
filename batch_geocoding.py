import os
import pandas as pd
import numpy as np
import json
import requests

def geocoding(address): 
    service ="https://apis.map.qq.com/ws/geocoder/v1/?address="
    output = "json"
    key = "JOZBZ-ZLKK6-ACDSR-M3LNV-I4REV-RYF6B"  
    url = service+address+'&output='+output+'&key='+key
    response = requests.get(url)
    text =  response.text
    dic = json.loads(text)
    status = dic['status']
    if status == 0:
        lng = float(dic["result"]["location"]["lng"])
        lat = float(dic["result"]["location"]["lat"])
        province = dic["result"]["address_components"]["province"]
        city = dic["result"]["address_components"]["city"]
        district = dic["result"]["address_components"]["district"]
        street = dic["result"]["address_components"]["street"]
        ad_code = dic["result"]["ad_info"]["adcode"]
        reliability = dic["result"]["reliability"]  # 大于等于7时为可信
        # lng84,lat84 = coordinate_conversion.gcj02towgs84(lng, lat)
        print(lng,lat,province,city,district,street,ad_code,reliability)
        return lng,lat,province,city,district,street,ad_code,reliability
    else:
        return np.nan,np.nan,"","","","","",""

def transform(lng,lat):
    if pd.isnull(lng) or pd.isnull(lat):
        return np.nan, np.nan
    geoconv_service = "https://apis.map.qq.com/ws/coord/v1/translate?"
    AK= "JOZBZ-ZLKK6-ACDSR-M3LNV-I4REV-RYF6B" 
    f = 1
    
    parameters = f"locations={lat},{lng}&type={f}&key={AK}"
    url = geoconv_service + parameters
    response = requests.get(url)
    s=response.text
    dic=json.loads(s)
    lat_fake = dic["locations"][0]["lat"]
    lng_fake = dic["locations"][0]["lng"]
    
    wgs_lng = lng + (lng - lng_fake)
    wgs_lat = lat + (lat - lat_fake)
    return wgs_lng, wgs_lat

df = pd.read_excel('待转换地址.xlsx','Sheet1')
df = df.dropna()
for row in df.iterrows():
    index = row[0]
    items = row[1]
    address = items['address']
    try:
        lng,lat,province,city,district,street,ad_code,reliability = geocoding(address)
        if pd.isnull(lng):
            continue
        lng_84,lat_84 = transform(lng,lat)
        df.loc[index,'lng'] = lng_84
        df.loc[index,'lat'] = lat_84
        df.loc[index,'province'] = province
        df.loc[index,'city'] = city
        df.loc[index,'district'] = district
        df.loc[index,'street'] = street
        df.loc[index,'ad_code'] = ad_code
        df.loc[index,'reliability'] = reliability
    except:
        continue

df.to_excel('地址转坐标结果.xlsx',encoding='utf8')
