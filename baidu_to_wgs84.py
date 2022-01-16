import pandas as pd
import requests
import json
geoconv_service = "http://api.map.baidu.com/geoconv/v1/?"
output = "json"
AK= "q7VjBC8m6tZItpRifBHi7B4V"

def transform(x,y,f,t):
    parameters = f"coords={x},{y}&from={f}&to={t}&ak={AK}"
    url = geoconv_service + parameters
    response = requests.get(url)
    s=response.text
    dic=json.loads(s)
    x = dic["result"][0]["x"]
    y = dic["result"][0]["y"]
    return (x,y) 

lng = 121.364598
lat = 31.215845

new_lng,new_lat = transform(lng,lat,1,5)
wgs_lng = lng + (lng - new_lng)
wgs_lat = lat + (lat - new_lat)
print(wgs_lng,wgs_lat)