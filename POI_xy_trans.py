from arcpy import *
import requests
import json

# 坐标转换
# env.workspace = r"I:\finished_project\Research_2020_GWR_Collision\work_space\completed_data\POI_2014changning_2level\poi_level2.mdb"
# features = ListFeatureClasses()
# for feature in features:
#     wgs84_path = r'E:\\workspace\\Research_2021_weather_collision\\data_processing\\Changning_POI_2014new\\poi_level2\\'
#     proj_file = r"E:\workspace\Research_2021_7thCencus_AgingPeople\data_processing\长三角官方养老院数据\沪苏浙粤养老机构20210822\Shapefile\江苏省养老机构2017.prj"
#     Project_management(feature,wgs84_path+feature+'.shp',proj_file)
#     print(feature)

def gcj2wgs(x,y):
    geoconv_service = "https://apis.map.qq.com/ws/coord/v1/translate?"
    output = "json"
    AK= "JOZBZ-ZLKK6-ACDSR-M3LNV-I4REV-RYF6B" 

    lng = x
    lat = y
    f = 1

    parameters = "locations="+str(lat)+","+str(lng)+"&type="+str(f)+"&key="+str(AK)
    url = geoconv_service + parameters
    response = requests.get(url)
    s=response.text
    dic=json.loads(s)
    lat_fake = dic["locations"][0]["lat"]
    lng_fake = dic["locations"][0]["lng"]

    wgs_lng = lng + (lng - lng_fake)
    wgs_lat = lat + (lat - lat_fake)
    return wgs_lng,wgs_lat

env.workspace = r'E:\workspace\Research_2021_weather_collision\data_processing\Changning_POI_2014new\poi_level1'
features = ListFeatureClasses()

for feature in features[15:]:
    # feature = features[0]
    fields = ['SHAPE@']
    upd_cur = da.UpdateCursor(feature,fields)
    i = 1
    for row in upd_cur:
        i = i+1
        point = row[0]
        org_x = point.firstPoint.X
        org_y = point.firstPoint.Y
        new_x, new_y = gcj2wgs(org_x,org_y)
        new_point = PointGeometry(Point(new_x,new_y))
        print(new_point)
        row[0] = new_point
        upd_cur.updateRow(row)
        print(feature+str(features.index(feature))+'//18:'+str(i))
    del upd_cur










