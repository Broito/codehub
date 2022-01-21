from arcpy import *
from arcpy import da
import os

os.chdir(r'E:\workspace\Research_2021_weather_collision\data_processing')
# env.workspace = r'E:\workspace\Research_2021_weather_collision\data_processing\images_changning'

def find_image(lon,lat):
    lon = str(lon)[:9]
    lat = str(lat)[:8]
    for image in images:
        if lon in image and lat in image:
            return image

    return None 


images = list(os.walk(r'.\images_changning'))[0][2]
vector = r'E:\workspace\Research_2021_weather_collision\data_processing\street_view.mdb\changning_cat'
fields = ['POINT_X','POINT_Y','image_name']

upd_cur = da.UpdateCursor(vector,fields)
# upd_cur = da.SearchCursor(vector,fields)
for field_value in upd_cur:
    lon = field_value[0]
    lat = field_value[1]
    raster = find_image(lon,lat)
    if raster != None:
        field_value[2] = raster
        upd_cur.updateRow(field_value)
        print('add success')
    else:
        print('no match')
        continue

del upd_cur
