# %%
from arcpy import *
import os
from arcpy.analysis import Intersect
from arcpy.sa.Functions import ExtractByMask, ZonalStatisticsAsTable
import pandas as pd
from dbfread import DBF
import numpy as np
from datetime import datetime 
import gzip

def un_zip(file_name):
    """ungz zip file"""
    f_name = file_name.replace(".gz", "")
    #获取文件的名称，去掉
    g_file = gzip.GzipFile(file_name)
    #创建gzip对象
    open(f_name, "wb+").write(g_file.read())
    #gzip对象用read()打开后，写入open()建立的文件里。
    g_file.close()
    #关闭gzip对象
    return f_name

def get_suffix_file(path,suffix):
    result = []
    files = os.listdir(path)
    for file in files:
        if file.split('.')[-1] == suffix:
            result.append(file)
    return result

def zonal(polygon,polygon_field,raster):
    try:
        temp_zonal_table = f'temp_table.dbf'
        ZonalStatisticsAsTable(polygon,polygon_field,raster,temp_zonal_table)
        table = DBF(env.workspace+r'\\'+temp_zonal_table, encoding='utf8')
        df = pd.DataFrame(iter(table))
        Delete_management(temp_zonal_table)
    except:
        return None
    return df

os.chdir(r'I:\DataHub\ODIAC')
env.overwriteOutput = True
env.workspace = r'I:\DataHub\ODIAC'

polygon = r"I:\\DataHub\\普查数据汇总\\六七普县级常住人口-刘涛\\六七普县级常住人口-刘涛.shp"
field = 'codeF7'

gzs = get_suffix_file(r'I:\DataHub\ODIAC','gz')

for gz in gzs:
    tif = un_zip(gz)
    df = zonal(polygon,field,tif)
    df.to_csv(f'./result/{tif[:-4]}.csv',encoding = 'utf8')
    Delete_management(tif)
    print(tif)

    
















