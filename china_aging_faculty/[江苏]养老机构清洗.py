import os
import pandas as pd
import numpy as np
import requests
import json
import geopandas as gpd
from shapely.geometry import Point

def geocoding(address,n): # n为最大递归次数，address为含有省市名称的完整地址，例如上海市闵行区东川路500号华东师范大学
    # 尝试5次，有些网络问题可以解决
    if n>5:
        print(f"{address}:达到最大递归次数，请手动操作")
        # 返回字段自行修改
        return np.nan,np.nan,"","","","",""
    # key为腾讯位置服务，我自己用企业账号申请的，每日5w次配额，尽量勿外传。
    service ="https://apis.map.qq.com/ws/geocoder/v1/?address="
    output = "json"
    key = "JOZBZ-ZLKK6-ACDSR-M3LNV-I4REV-RYF6B"  
    url = service+address+'&output='+output+'&key='+key
    response = requests.get(url)
    text =  response.text
    dic = json.loads(text)
    status = dic['status']
    if status == 0:
        # 字段自行修改
        lng = float(dic["result"]["location"]["lng"])
        lat = float(dic["result"]["location"]["lat"])
        province = dic["result"]["address_components"]["province"]
        city = dic["result"]["address_components"]["city"]
        district = dic["result"]["address_components"]["district"]
        ad_code = dic["result"]["ad_info"]["adcode"]
        reliability = dic["result"]["reliability"]  # 大于等于7时为可信，小于5的需要手动查验
        # lng84,lat84 = coordinate_conversion.gcj02towgs84(lng, lat)
        print(lng,lat,province,city,district,ad_code,reliability)
        return lng,lat,province,city,district,ad_code,reliability
    else:
        print(f"{address}:地理编码不成功,再次尝试")
        # 若是找不到该地址，则直接用省市+名称（不加地址了），如 上海市华东师范大学。 name为外面的全局变量，可以自行修改至方法参数中
        return geocoding('上海市'+name,n+1)

# 地理编码返回的是gcj02坐标，用该方法返回准确的wgs84坐标。 该方法反向调用腾讯位置服务的坐标转换，比用数学公式硬转要准确得多。
# 同样，key勿外传，每日5w次配额。
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

os.chdir(r'E:\workspace\Research_2021_7thCencus_AgingPeople\data_processing\长三角官方养老院数据\江苏养老机构')
df = pd.read_csv('江苏.csv')

df['full_address'] = df['地址'].map(lambda a: '江苏省'+a.strip('\n')) + df['机构名称']
for row in df.iterrows():
    index = row[0]
    items = row[1]
    full_address = items['full_address']
    name = items['机构名称']
    address = items['地址']
    lng,lat,province,city,district,ad_code,reliability = geocoding(full_address,1)
    lng_84,lat_84 = transform(lng,lat)
    df.loc[index,'lng'] = lng_84
    df.loc[index,'lat'] = lat_84
    df.loc[index,'province'] = province
    df.loc[index,'city'] = city
    df.loc[index,'district'] = district
    df.loc[index,'ad_code'] = ad_code
    df.loc[index,'reliability'] = reliability
    print(index)
df['geometry'] = list(zip(df['lng'],df['lat']))
df['geometry'] = df['geometry'].map(lambda a: Point(a))
df.to_csv("江苏养老机构2017.csv",encoding='GB18030')   
gdf = gpd.GeoDataFrame(df,columns=df.columns,crs="EPSG:4326")
gdf.to_file("江苏养老机构2017.shp",encoding='GB18030') 

# 江苏的有很多为reliability为1和3的，需要手动添加地级市县级市后再重新跑。 另外是大部分都重复了三遍，需要去重
df2 = pd.read_csv(r'江苏养老机构2017.csv',encoding = 'GB18030')
df2 = df2.drop_duplicates(['机构名称'])
# df2_rlb = df2[df2['reliability']==1]
df2_rlb = df2[df2['province']=='上海市']
for row in df2_rlb.iterrows():
    index = row[0]
    items = row[1]
    full_address = items['full_address']
    name = items['机构名称']
    address = items['地址']
    lng,lat,province,city,district,ad_code,reliability = geocoding(full_address,1)
    lng_84,lat_84 = transform(lng,lat)
    df2_rlb.loc[index,'lng'] = lng_84
    df2_rlb.loc[index,'lat'] = lat_84
    df2_rlb.loc[index,'province'] = province
    df2_rlb.loc[index,'city'] = city
    df2_rlb.loc[index,'district'] = district
    df2_rlb.loc[index,'ad_code'] = ad_code
    df2_rlb.loc[index,'reliability'] = reliability
    print(index)
df2_rlb.to_csv("江苏养老机构2017_低信度地理编码修改.csv",encoding='GB18030')  

pd.to_csv(r"C:\Users\NingchengWang\Desktop\长宁历史天气.csv",encoding = 'GB18030',mode = 'a',)







