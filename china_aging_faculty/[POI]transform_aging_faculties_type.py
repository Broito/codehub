import pandas as pd
import requests
import json

def extract_type1(text):
    if "|" in text:
        body = text.split("|")[0]
    else:
        body = text
    return body.split(";")[0]

def extract_type2(text):
    if "|" in text:
        body = text.split("|")[0]
    else:
        body = text
    return body.split(";")[1]

def extract_type3(text):
    if "|" in text:
        body = text.split("|")[0]
    else:
        body = text
    return body.split(";")[2]

def calc_unique_types(df):
    df['type1'] = df["type"].apply(extract_type1)
    df['type2'] = df["type"].apply(extract_type2)
    df['type3'] = df["type"].apply(extract_type3)
    types = df.groupby(by=["type1","type2","type3"], as_index=False).first().iloc[:,:3]
    return types

df = pd.read_csv(r"H:\DataHub\全国POI2020\养老设施.csv")
for i in df.iterrows():
    index = i[0]
    row = i[1]
    lng = row[9]
    lat = row[10]
    wgs_lng, wgs_lat = transform(lng,lat)
    df.loc[index,"lon_wgs84"] = wgs_lng
    df.loc[index,"lat_wgs84"] = wgs_lat
    print(index,row[1])
    






























