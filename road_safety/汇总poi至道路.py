import arcpy,datetime,math,xlwt
from arcpy import env

env.workspace = r"E:\\workspace\\Research_2021_weather_collision\\data_processing\\Changning_POI_2014new\\poi_collision"
features = arcpy.ListFeatureClasses()
names = ['num_entertain','num_hospital','num_clinic','num_estate','num_villa','num_school','num_convstore','num_commercial','num_supermarket','num_park']
for poi,name in zip(features,names):
    arcpy.env.overwriteOutput = True
    cutRoad=r"E:\workspace\Research_2021_weather_collision\data_processing\road_data.gdb\road_OSM_sim200_buffer500"#路段数据
    # collisions="vehicle_pedestrian_1216_纯多云"
    accifield = name
    arcpy.AddField_management(cutRoad, accifield, "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    intersected="intersected"
    fretable="fretable"
    arcpy.Intersect_analysis([poi, cutRoad], intersected)
    arcpy.Frequency_analysis(intersected, fretable, "roadid_sim", "")
    arcpy.JoinField_management(cutRoad, "roadid_sim", fretable, "ROADID_SIM", "FREQUENCY")
    arcpy.CalculateField_management(cutRoad, accifield, "!FREQUENCY!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(cutRoad, ["FREQUENCY"])
    arcpy.Delete_management(intersected)
    arcpy.Delete_management(fretable)
    print accifield