import arcpy,datetime,math,xlwt
from arcpy import env

env.workspace = r"E:\\FloatVehicle2019\\cluster.mdb"
arcpy.env.overwriteOutput = True
cutRoad="road_osm200"#路段数据
geo2015="geo2015"
    # for i in range(0,24,2):
accifield="acci%d_%d"%(1,24)#添加的字段
arcpy.AddField_management(cutRoad, accifield, "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
qstr="""timegrade >= %d AND timegrade <%d"""%(1,25)
selectgeo="selectgeo"
arcpy.Select_analysis(geo2015, selectgeo, qstr)
neartable="neartable"
fretable="fretable"
arcpy.GenerateNearTable_analysis(selectgeo, cutRoad, neartable, "", "NO_LOCATION", "NO_ANGLE", "CLOSEST", "0")
arcpy.Frequency_analysis(neartable, fretable, "NEAR_FID", "")
arcpy.JoinField_management(cutRoad, "OBJECTID", fretable, "NEAR_FID", "FREQUENCY")
arcpy.CalculateField_management(cutRoad, accifield, "!FREQUENCY!", "PYTHON_9.3", "")
arcpy.DeleteField_management(cutRoad, ["FREQUENCY"])
arcpy.Delete_management(neartable)
arcpy.Delete_management(fretable)
arcpy.Delete_management(selectgeo)
print accifield