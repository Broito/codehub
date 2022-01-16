import os
import pandas as pd
import numpy as np
import requests
import json
import geopandas as gpd
from shapely.geometry import Point

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
        return geocoding('上海市'+name,n+1)

def transform(lng,lat):
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

def strip_n(df,column):
    return df[column].map(lambda a : a.strip('\n') if a is not np.nan else np.nan)

os.chdir(r'E:\workspace\Research_2021_7thCencus_AgingPeople\data_processing\长三角官方养老院数据')
df = pd.read_csv('上海.csv')

categories = ['社区养老','助餐服务点','综合为老服务中心','老年日间照护机构','长者照护之家','养老机构','护理站\\院']

# df_sqyl = df[df['类型']=="社区养老"]
# df_sqyl = df_sqyl.loc[:,['名称','类型','成立时间','咨询电话','长护险定点','办公地址','服务内容']]
# df_sqyl['办公地址'] = df_sqyl['办公地址'].map(lambda a : a.strip('\n') if a is not np.nan else np.nan)
# df_sqyl['服务内容'] = df_sqyl['服务内容'].map(lambda a : a.strip('\n') if a is not np.nan else np.nan)
# df_sqyl['full_address'] = df_sqyl['办公地址'].map(lambda a: '上海市'+a.strip('\n')) + df_sqyl['名称']
# for row in df_sqyl.iterrows():
#     index = row[0]
#     items = row[1]
#     full_address = items['full_address']
#     global name
#     name = items['名称']
#     address = items['办公地址']
#     lng,lat,province,city,district,ad_code,reliability = geocoding(full_address,1)
#     lng_84,lat_84 = transform(lng,lat)
#     df_sqyl.loc[index,'lng'] = lng_84
#     df_sqyl.loc[index,'lat'] = lat_84
#     df_sqyl.loc[index,'province'] = province
#     df_sqyl.loc[index,'city'] = city
#     df_sqyl.loc[index,'district'] = district
#     df_sqyl.loc[index,'ad_code'] = ad_code
#     df_sqyl.loc[index,'reliability'] = reliability
#     print(index)
# df_sqyl['geometry'] = list(zip(df_sqyl['lng'],df_sqyl['lat']))
# df_sqyl['geometry'] = df_sqyl['geometry'].map(lambda a: Point(a))
# gdf = gpd.GeoDataFrame(df_sqyl,columns=df_sqyl.columns,crs="EPSG:4326")
# gdf.to_file("社区养老服务中心_final.shp",encoding='GB18030') 

def generate_shp(type_name,columns):
    df_sqyl = df[df['类型']==type_name]
    df_sqyl = df_sqyl.loc[:,columns]
    # strip /n for all columns
    for column_name in columns:
        df_sqyl[column_name] = strip_n(df_sqyl, column_name)
    df_sqyl['full_address'] = df_sqyl['机构地址'].map(lambda a: '上海市'+a.strip('\n')) + df_sqyl['名称']
    print("strip success")
    for row in df_sqyl.iterrows():
        index = row[0]
        items = row[1]
        full_address = items['full_address']
        global name
        name = items['名称']
        lng,lat,province,city,district,ad_code,reliability = geocoding(full_address,1)
        lng_84,lat_84 = transform(lng,lat)
        df_sqyl.loc[index,'lng'] = lng_84
        df_sqyl.loc[index,'lat'] = lat_84
        df_sqyl.loc[index,'province'] = province
        df_sqyl.loc[index,'city'] = city
        df_sqyl.loc[index,'district'] = district
        df_sqyl.loc[index,'ad_code'] = ad_code
        df_sqyl.loc[index,'reliability'] = reliability
        print(index)
    df_sqyl['geometry'] = list(zip(df_sqyl['lng'],df_sqyl['lat']))
    df_sqyl['geometry'] = df_sqyl['geometry'].map(lambda a: Point(a))
    df_sqyl.to_csv(f"{type_name}.csv",encoding='GB18030')
    gdf = gpd.GeoDataFrame(df_sqyl,columns=df_sqyl.columns,crs="EPSG:4326")
    try:
        gdf.to_file(f"{type_name}.shp",encoding='GB18030')
    except:
        pass

types = ['综合为老服务中心','老年日间照护机构','长者照护之家','养老机构','护理站\\院']
columnses = [['名称','类型','成立时间','咨询电话','机构地址','长者照护之家','助餐服务','日间照料服务','卫生服务中心或站点服务'],
             ['名称','类型','成立时间','咨询电话','托位数','建设主体','参考价格','机构地址'],
             ['名称','类型','成立时间','咨询电话','内设医疗机构','床位总数','参考价格','机构地址','提供保基本床位'],
             ['名称','类型','机构等级','日常监测','成立时间','建筑面积', '咨询电话','内设医疗机构','床位总数','可用床位', '参考价格','机构地址','提供保基本床位'],
             ['名称','类型','发证机关', '经营性质', '机构类别','机构地址']]

for aging_type,columns in zip(types,columnses):
    generate_shp(aging_type,columns)
    print(aging_type)






















