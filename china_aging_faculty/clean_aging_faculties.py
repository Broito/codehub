import os
import pandas as pd
import requests
import json
import math
import numpy as np
import time
# import coordinate_conversion

def geocoding(address,n): # n为最大递归次数
    if n>5:
        print(f"{address}:达到最大递归次数，请手动操作")
        return np.nan,np.nan,"","","","",""
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
        ad_code = dic["result"]["ad_info"]["adcode"]
        reliability = dic["result"]["reliability"]  # 大于等于7时为可信
        # lng84,lat84 = coordinate_conversion.gcj02towgs84(lng, lat)
        print(lng,lat,province,city,district,ad_code,reliability)
        return lng,lat,province,city,district,ad_code,reliability
    else:
        print(f"{address}:地理编码不成功,再次尝试")
        return geocoding(faculty_name,n+1)

def extract_price(text):
    if text == "暂无价格":
        return np.nan,np.nan
    price_type = text.split('元')[1]
    if price_type == '起/月':  #存在一些，是5800元起/月 这种格式
        return float(text.split('元')[0]),np.nan
    elif '-' not in text:  # 存在一些，最高最低价一样的，这种格式
        return float(text.split('元')[0]),float(text.split('元')[0])
    else:
        price_list = text.split('元')[0].split('-')
        bottom = float(price_list[0])
        top = float(price_list[1])
        if bottom < 500:  # 若出现1元的，就直接当np.nan
            bottom = np.nan
        return bottom, top

def extract_year(text):
    if text is np.nan:
        return np.nan
    if len(text) >= 4 and text[:4].isdigit() == True :
        return float(text[:4])
    else:
        return np.nan
    

def extract_bed(text):
    if text == '-':
        return np.nan
    return float(text.replace("张",""))

def extract_nurse_level(text):
    if "专护" in text:
        return 5
    if "特护" in text:
        return 4
    if "全护" in text:
        return 3
    if "半护" in text:
        return 2
    else:
        return 1

os.chdir(r"E:\workspace\Research_2021_7thCencus_AgingPeople\data_processing\aging_faculties")
csvs = [i for i in os.walk('.')][0][-1]

full_columns = ['faculty_name',
                'full_address',
                    'province','province_code','city','city_code','district','district_code',
                    'longitude','latitude','coding_reliability',
                'price_floor','price_ceil',
                'manage_type','faculty_type',
                'install_year',
                'number_bed',
                'top_nurse_level']
# top_nurse_level表示该养老院收住对象的最高护理水平。12345级分别为 自理 半护 全护 特护 专护
total_df = pd.DataFrame(columns = full_columns)

for csv in csvs[10:]:
    print(csv)
    try:
        df = pd.read_csv(csv)
        for i in df.iterrows():
            row = i[1]
            faculty_name = row[0]
            address = row[1]
            price_floor, price_ceil = extract_price(row[2])
            manage_type = row[3]
            faculty_type = row[4]
            install_year = extract_year(row[5])
            number_bed = extract_bed(row[6])
            top_nurse_level = extract_nurse_level(row[7])
            full_address = address+faculty_name
            longitude, latitude, province, city, district, ad_code, coding_reliability = geocoding(full_address,1)
            province_code, city_code, district_code = ad_code[:2], ad_code[:4], ad_code
            
            insert_row = {"faculty_name":faculty_name,
                        "full_address":full_address,
                            "province":province,"province_code":province_code,"city":city,
                            "city_code":city_code,"district":district,"district_code":district_code,
                            "longitude":longitude,"latitude":latitude,"coding_reliability":coding_reliability,
                        "price_floor":price_floor,"price_ceil":price_ceil,
                        "manage_type":manage_type,"faculty_type":faculty_type,
                        "install_year":install_year,
                        "number_bed":number_bed,
                        "top_nurse_level":top_nurse_level}
            total_df = total_df.append(insert_row,ignore_index = True)
    except:
        df = pd.read_csv(csv,encoding = 'gbk')
        for i in df.iterrows():
            row = i[1]
            faculty_name = row[0]
            address = row[1]
            price_floor, price_ceil = extract_price(row[2])
            manage_type = row[3]
            faculty_type = row[4]
            install_year = extract_year(row[5])
            number_bed = extract_bed(row[6])
            top_nurse_level = extract_nurse_level(row[7])
            full_address = address+faculty_name
            longitude, latitude, province, city, district, ad_code, coding_reliability = geocoding(full_address,1)
            province_code, city_code, district_code = ad_code[:2], ad_code[:4], ad_code
            
            insert_row = {"faculty_name":faculty_name,
                        "full_address":full_address,
                            "province":province,"province_code":province_code,"city":city,
                            "city_code":city_code,"district":district,"district_code":district_code,
                            "longitude":longitude,"latitude":latitude,"coding_reliability":coding_reliability,
                        "price_floor":price_floor,"price_ceil":price_ceil,
                        "manage_type":manage_type,"faculty_type":faculty_type,
                        "install_year":install_year,
                        "number_bed":number_bed,
                        "top_nurse_level":top_nurse_level}
            total_df = total_df.append(insert_row,ignore_index = True)

    
    






















