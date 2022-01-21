from arcpy import *
from arcpy import da
import os

os.chdir(r'E:\workspace\Research_2021_weather_collision\data_processing')
env.workspace = r'E:\workspace\Research_2021_weather_collision\data_processing\streetview.mdb'

def find_image(lon,lat):
    lon = str(lon).replace('.','_')
    lat = str(lat).replace('.','_')
    for image in images:
        if lon in image and lat in image:
            return Raster(image)
            # return r'E:\\workspace\\Research_2021_weather_collision\\data_processing\\images_changning\\'+image

    return None 


# images = list(os.walk(r'.\images_changning'))[0][2]
images = ListDatasets()
vector = r'E:\workspace\Research_2021_weather_collision\data_processing\street_view.mdb\changning_cat'
fields = ['POINT_X','POINT_Y','photo']

upd_cur = da.UpdateCursor(vector,fields)
# upd_cur = da.SearchCursor(vector,fields)
for field_value in upd_cur:
    lon = field_value[0]
    lat = field_value[1]
    raster = find_image(lon,lat)
    if type(raster) == Raster:
        print(type(raster))
        # MakeFeatureLayer_management(raster, "lyr_raster")
        # field_value[2] = "lyr_raster"
        field_value[2] = raster
        upd_cur.updateRow(field_value)
        print('add success')
    else:
        print('no match')
        continue

del upd_cur








