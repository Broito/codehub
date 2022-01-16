import pandas as pd
import requests
import json
geoconv_service = "https://apis.map.qq.com/ws/coord/v1/translate?"
output = "json"
AK= "JOZBZ-ZLKK6-ACDSR-M3LNV-I4REV-RYF6B" 

lng = 121.394805
lat = 31.207418
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
print(wgs_lng,wgs_lat)



