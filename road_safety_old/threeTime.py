# -*- coding: utf-8 -*-
import arcpy
import  xlwt
def three_time():
    "生成三个时间段的2015年事故点"
    geo_2015 = "F:\\trafficdata\\changning_acci\\accidentData.gdb\\geo_2015"
    geo_2015_8 =geo_2015+"_8"#时间段8-10
    arcpy.Select_analysis(geo_2015, geo_2015_8, "\"timegrade\" = 9 OR \"timegrade\" = 10")

    geo_2015_17 =geo_2015+"_17"#时间段17-19
    arcpy.Select_analysis(geo_2015, geo_2015_17, "\"timegrade\" = 18 OR \"timegrade\" = 19")

    geo_2015_3 =geo_2015+"_3"#时间段3-6
    arcpy.Select_analysis(geo_2015, geo_2015_3, "\"timegrade\" = 4 OR \"timegrade\" = 5 OR \"timegrade\" = 6")
three_time()


