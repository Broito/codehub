import os
from arcpy import *

os.chdir(r'I:\DataHub\SRTM3v4.1_90m\90m-NASA SRTM3 v4.1')
folders = list(os.listdir('.'))

raster_path_list = []

for folder in folders:
    print(folder)
    env.workspace = './'+folder
    rasters = list(ListRasters())[:-1]
    raster_path_list += [os.getcwd()+'\\'+folder+'\\'+i for i in rasters]

MosaicToNewRaster_management(raster_path_list,"I:\DataHub\SRTM3v4.1_90m\90m-NASA SRTM3 v4.1\China_SRTM3v4.1_90m",'China_SRTM3v4.1_90m.tif',number_of_bands=1,pixel_type = '32_BIT_UNSIGNED')












