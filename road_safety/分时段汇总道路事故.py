import arcpy,datetime,math,xlwt
from arcpy import env

env.workspace = r"E:\workspace\Research_2021_weather_collision\data_processing\accident_leaf.gdb"
features = arcpy.ListFeatureClasses()
for collisions in features:
    arcpy.env.overwriteOutput = True
    cutRoad=r"E:\workspace\Research_2021_weather_collision\data_processing\road_data.gdb\road_OSM_sim200"#路段数据
    # collisions="vehicle_pedestrian_1216_纯多云"
    accifield = collisions.split('_')[0]+'_'+collisions.split('_')[-1]
    arcpy.AddField_management(cutRoad, accifield, "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    neartable="neartable"
    fretable="fretable"
    arcpy.GenerateNearTable_analysis(collisions, cutRoad, neartable, "", "NO_LOCATION", "NO_ANGLE", "CLOSEST", "0")
    arcpy.Frequency_analysis(neartable, fretable, "NEAR_FID", "")
    arcpy.JoinField_management(cutRoad, "OBJECTID", fretable, "NEAR_FID", "FREQUENCY")
    arcpy.CalculateField_management(cutRoad, accifield, "!FREQUENCY!", "PYTHON_9.3", "")
    arcpy.DeleteField_management(cutRoad, ["FREQUENCY"])
    arcpy.Delete_management(neartable)
    arcpy.Delete_management(fretable)
    print accifield