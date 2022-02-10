# %%
from unicodedata import category
from arcpy import *
import os

os.chdir(r'I:\\DataHub\\中国100万基础地理数据2021\\分区GDB\\')
env.overwriteOutput = True

gdbs = list(os.listdir('.'))

# 创建初始分类gdb
# example = gdbs[0]
# env.workspace = f'./{example}'
# names = ListFeatureClasses()
# for name in names:
#     CreateFileGDB_management(r'../分类GDB',f'{name}.gdb')

# 将各分区域gdb中的各类要素复制进分类gdb中
for gdb in gdbs:
    suffix = gdb[:-4]
    env.workspace = f'./{gdb}'
    features = ListFeatureClasses()
    for feature in features:
        new_name = feature+'_'+suffix
        new_category = feature
        out_path = f'../分类GDB/{new_category}.gdb/{new_name}'
        CopyFeatures_management(feature,out_path)
        print(gdb,feature)


# <<<<<< -----------------------------------------------------
# 合并分类GDB
os.chdir(r'I:\\DataHub\\中国100万基础地理数据2021\\分类GDB\\')
env.overwriteOutput = True

gdbs = list(os.listdir('.'))
for gdb in gdbs:
    env.workspace = f'./{gdb}'
    features = ListFeatureClasses()
    output = f'../2021_100万中国基础数据合并版.gdb/{gdb[:-4]}'
    Merge_management(features,output)
    print(gdb)





# %%
