import pandas as pd
import requests
import json

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

df = pd.read_excel(r"E:\workspace\Research_2021_7thCencus_AgingPeople\data_processing\aging_faculties\china_aging_faculties.xls","Sheet1")
for i in df.iterrows():
    index = i[0]
    row = i[1]
    lng = row[9]
    lat = row[10]
    wgs_lng, wgs_lat = transform(lng,lat)
    df.loc[index,"lon_wgs84"] = wgs_lng
    df.loc[index,"lat_wgs84"] = wgs_lat
    print(index,row[1])
    






























