import pandas as pd

chunksize = 1000000

count = 1
for df in pd.read_csv("H:\DataHub\全国POI2020\gdpoi2020-8500W.csv", dtype={'adcode': 'str', 'citycode': 'str'}, chunksize=chunksize):
    print(count)
    cyfw = df[(df['typecode']=="080400") | (df['typecode']=="080402") ]
    cyfw.to_csv('H:\DataHub\全国POI2020\养老设施.csv', mode='a', header=False)
    count += 1
print(df.head())
