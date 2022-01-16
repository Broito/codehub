import pandas as pd

# chunksize = 1000000

# count = 1
# for df in pd.read_csv('F:\\数据存储\\基础地理数据\\gdpoi2020-8500W-CSV\\gdpoi2020-8500W.csv', dtype={'adcode': 'str', 'citycode': 'str'}, chunksize=chunksize):
#     print(count)
#     cyfw = df[df['pname'].str.contains('山东省',na=False)]
#     cyfw.to_csv('F:\\数据存储\\基础地理数据\\gdpoi2020-8500W-CSV\\山东省.csv', mode='a', header=False)
#     count += 1
# print(df.head())

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

# df = pd.read_csv("H:\DataHub\全国POI2020\gdpoi2020-8500W.csv",nrows = 1000,encoding = "utf-8")
# result = calc_unique_types(df)

chunksize = 1000000
count = 1
total_types = pd.DataFrame(columns = ["type1","type2","type3"])

for df in pd.read_csv("H:\DataHub\全国POI2020\gdpoi2020-8500W.csv", dtype={'adcode': 'str', 'citycode': 'str'}, chunksize=chunksize):
    print(count)
    chunk
























