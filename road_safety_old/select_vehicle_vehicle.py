from arcpy import *

env.workspace = r"E:\\FloatVehicle2019\\accident.gdb"

cur_search_pedestrain = da.SearchCursor('pedestrain2014','IN_FID')
cur_update_total = da.UpdateCursor('vehicle2014','IN_FID')

pedes_fid = []
for i in cur_search_pedestrain:
    pedes_fid.append(i[0])

for cur in cur_update_total:
    if cur[0] in pedes_fid:
        cur_update_total.deleteRow()

del cur_search_pedestrain
del cur_update_total




