import pandas as pd
import numpy as np

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
        if len(body.split(";")) < 2:
            return np.nan
    return body.split(";")[1]

def extract_type3(text):
    if "|" in text:
        body = text.split("|")[0]
    else:
        body = text
        if len(body.split(";")) < 3:
            return np.nan
    return body.split(";")[2]

list_code = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','97','99']
list_type = ['汽车服务','汽车销售','汽车维修','摩托车服务','餐饮服务','购物服务','生活服务','体育休闲服务','医疗保健服务',
              '住宿服务','风景名胜','商务住宅','政府机构及社会团体','科教文化服务','交通设施服务','金融保险服务','公司企业','道路附属设施',
              '地名地址信息','公共设施','室内设施','通行设施']

path = r'H:\\DataHub\\全国POI2020\\2020高德POI\\csv\\'
# for code,typei in zip(list_code,list_type):
#     df = pd.DataFrame(columns = ['name','type','tel','x_gcj02','y_gcj02','province','city','district','city_code',
#                                   'address_code','type_code','address','baidu_x','baidu_y','wgs84_x','wgs83_y',
#                                   'type1','type2','type3'])
#     df.to_csv(path+code+'_'+typei+".csv",mode='a')

chunksize = 1000000
count = 1
for df in pd.read_csv("H:\DataHub\全国POI2020\gdpoi2020-8500W.csv", dtype={'adcode': 'str', 'citycode': 'str','typecode':'str'}, chunksize=chunksize):
    print(count)
    
    for code,typei in zip(list_code,list_type):
        insert_df = df[df['typecode'].map(lambda g: str(g)[:2])==code]
        insert_df['type1'] = insert_df["type"].apply(extract_type1)
        insert_df['type2'] = insert_df["type"].apply(extract_type2)
        insert_df['type3'] = insert_df["type"].apply(extract_type3)

        insert_df.to_csv(path+code+'_'+typei+".csv",mode='a',header=False)
        print(f'{count}:'+code+' '+typei+"完成")
    
    count += 1
print(df.head())






























