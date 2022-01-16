from arcpy import *

env.workspace = r'E:\\workspace\\Research_2021_7thCencus_AgingPeople\\【数读城事】分享：行政区划2020\\'
org_shp = '省.shp'

# SHAPE@是几何对象，不要动，后面的是要提取出来的字段
fields = ['SHAPE@','省','省代码']
cur = da.SearchCursor(org_shp,fields)
for row in cur:
    


















