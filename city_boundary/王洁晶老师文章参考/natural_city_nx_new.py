import arcpy
import os
from scipy.sparse import lil_matrix
import timeit
from datetime import datetime
import cPickle as pickle
import itertools
import networkx as nx
import numpy as np


arcpy.env.overwriteOutput = True

# 创建geodatabase
def CreateGeoDB(gdb_name):
    if not os.path.exists(gdb_name):
        print "Creating Geodabase {}".format(gdb_name)
        arcpy.CreateFileGDB_management(".", gdb_name)
    else:
        print "Geodabase {} exists".format(gdb_name)
    return './{}'.format(gdb_name)

# 备份一个新的原始数据至操作空间（geodatabase）

def CopyDataInto(shp_file):
    gdb_name = "urban.gdb"
    gdb_name = CreateGeoDB(gdb_name)
    file_name = os.path.splitext(os.path.basename(shp_file))[0]
    new_shp_file = '{}/{}'.format(gdb_name,file_name)
    
    if not arcpy.Exists(new_shp_file):
        print "Copy data to {}".format(new_shp_file)
        arcpy.CopyFeatures_management(shp_file, new_shp_file)
    else:
        print "file {} exists".format(new_shp_file)
    return new_shp_file

# 把面积小于某个面积阈值的小斑块去除
def RemoveSmall(shp_file,area_threshold,dist_threshold = 0):
    gdb_name = "filter.gdb"
    gdb_name = CreateGeoDB(gdb_name)
    file_name = os.path.splitext(os.path.basename(shp_file))[0]
    new_shp_file = '{}/{}_ar{}_r{}'.format(gdb_name,file_name,area_threshold,
                                           dist_threshold)
    if not arcpy.Exists(new_shp_file):
        print "Remove polygons smaller than {} m2".format(area_threshold)
        
        arcpy.MakeFeatureLayer_management(shp_file, "lyr")
        where_clause = '"Shape_Area" > {}'.format(area_threshold)
        arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION",
                                                where_clause)
        
        print "Add polygons within a distance of {} m".format(dist_threshold)
        # 按最短距离聚类（用intersect设置buffer）        
        arcpy.SelectLayerByLocation_management('lyr', 'intersect', 'lyr',
                                               search_distance = dist_threshold)

        arcpy.CopyFeatures_management("lyr", new_shp_file)
    else:
        print "{} already exists".format(new_shp_file)
    return new_shp_file                                                 

def CalcDistanceMatrix(shp_file,distance):
    print "Calculating Distance Matrix...."
    arcpy.MakeTableView_management(shp_file, "table_view")
    num_polys = int(arcpy.GetCount_management("table_view").getOutput(0))
    
    dis_mtx = lil_matrix((num_polys+1, num_polys+1))
    arcpy.MakeFeatureLayer_management(shp_file, "lyr")

    oid_fieldname = arcpy.Describe(shp_file).OIDFieldName
    cursor = arcpy.da.SearchCursor(shp_file,[oid_fieldname,"SHAPE@"])
    for row in cursor:
        this_id = row[0]
        this_poly = row[1]
        if int(this_id) % (num_polys/20) == 0:
            print int(this_id) / (num_polys/20)
        linear_unit = "{} Meters".format(distance)
        # 求斑块的距离矩阵，但是只选中相距50000m之内的斑块（做一个初步筛选）
        arcpy.SelectLayerByLocation_management('lyr', 'intersect', this_poly,
                                               linear_unit)

        # 求当前斑块对50000m内每个斑块的距离，写入矩阵
        sel_cursor = arcpy.da.SearchCursor("lyr", [oid_fieldname,"SHAPE@"])
        
        for sel_row in sel_cursor:
            sel_id = sel_row[0]
            sel_poly = sel_row[1]
            if this_id < sel_id:
                temp = this_poly.distanceTo(sel_poly)
                if temp < 1e-6:
                    temp = 1e-6
                dis_mtx[this_id,sel_id] = temp
        del sel_cursor

    del cursor
    
    return dis_mtx

def SaveSparseMatrix(file_name,dis_mtx):
    with open(file_name, 'wb') as outfile:
        pickle.dump(dis_mtx, outfile, pickle.HIGHEST_PROTOCOL)
    return True

def LoadSparseMatrix(file_name):
    with open(file_name, 'rb') as infile:
        dis_mtx = pickle.load(infile)
    return dis_mtx


def GetClusterDict(dis_mtx,distance):
#depricated
    cluster_dict = {}
    num_rows = dis_mtx.shape[0]
    for i in range(1,num_rows):
        tmp = []
        cx = dis_mtx[:,i].tocoo()
        for j,v in itertools.izip(cx.row, cx.data):
            if v < distance:
                tmp.append(j)
        cx = dis_mtx[i,].tocoo()
        for j,v in itertools.izip(cx.col, cx.data):
            if v < distance:
                tmp.append(j)
        
        cluster_dict[i] = tmp
    return cluster_dict

def FindConnnectClusters(cluster_dict,city_id):
#depricated
    city_set = []
    city_set.append(city_id)
    checked_city = []
    while city_set:
        this_city = city_set.pop()
        checked_city.append(this_city)
        for city in cluster_dict[this_city]:
            if not city in checked_city:
                city_set.append(city)
    return checked_city


def Clustering(cluster_dict):
#depricated
    which_cluster = {}
    num_rows = len(cluster_dict.keys())
    num_clusters = 0
    for i in range(1,num_rows+1):
        if not i in which_cluster.keys():
            num_clusters +=1
            this_cluster = FindConnnectClusters(cluster_dict,i)
            #print i,this_cluster
            for city_id in this_cluster:
                which_cluster[city_id] = num_clusters
    return which_cluster

def Clustering_nx(dis_mtx,distance):
    G = nx.Graph()
    cx = dis_mtx.tocoo()
    for i,j,v in itertools.izip(cx.row,cx.col,cx.data):
        if v < distance:
            G.add_edge(i,j)
    
    which_cluster = np.zeros((dis_mtx.shape[0]), dtype=np.int)

    num_cluster = 0
    # 求整个非连通图中的连通分量（即有多少个都连着的聚类）
    for this_group in sorted(nx.connected_components(G),
                             key = len, reverse=True):
        num_cluster += 1
        for i in this_group:
            which_cluster[i] = num_cluster

    for i in range(1,len(which_cluster)):
        if which_cluster[i] == 0:
            num_cluster += 1
            which_cluster[i] = num_cluster
    
    #print num_cluster

    return which_cluster
    # 返回一个列表，index是斑块id，value是所在聚类

def AddNewField(shp_file,distance):
    field_name = 'R{}'.format(distance)
    desc = arcpy.Describe(shp_file)
    if not field_name in desc.fields:
        print "Add Field {} to {}".format(field_name, shp_file)
        arcpy.AddField_management(shp_file, field_name, "LONG")
    else:
        print("Field {} already exists!".format(field_name))
    return True

def StoreIntoFile(shp_file,distance,which_cluster):
#depricated
    AddNewField(shp_file,distance)
    field_name = 'R{}'.format(distance)
    oid_fieldname = arcpy.Describe(shp_file).OIDFieldName
    print "Storing into field {}".format(field_name)
    cursor = arcpy.da.UpdateCursor(shp_file,[oid_fieldname,field_name])
    for row in cursor:
        row[1] = which_cluster[row[0]];
        cursor.updateRow(row)
    del cursor
    return True

# 把聚类结果写入shp中
def StoreIntoFile_nx(shp_file,distance,which_cluster):
    AddNewField(shp_file,distance)
    field_name = 'R{}'.format(distance)
    oid_fieldname = arcpy.Describe(shp_file).OIDFieldName
    print "Storing into field {}".format(field_name)
    cursor = arcpy.da.UpdateCursor(shp_file,[oid_fieldname,field_name])
    for row in cursor:
        row[1] = which_cluster[row[0]];
        cursor.updateRow(row)
    del cursor
    return True                               


area_threshold = 50000
dist_threshold = 0
sample_data = True
stop_after_selection = False

#shp_file = r".\urban_2010\urban.gdb\Urbanland_2010"
shp_file = r"C:\360��ȫ����ͬ����\Research\2020 ȫ���˿�Ǩ��\������ϵ�ĵ���߶Ƚ綨\Data\GIS\beijing_urban_1978-2017.shp"


shp_file = CopyDataInto(shp_file)
if sample_data:
    shp_file = RemoveSmall(shp_file,area_threshold,dist_threshold)
if stop_after_selection:
    sys.exit()

#---------------------------calculation -----------------------

file_name = '{}_dis_matrix.dat'.format(os.path.splitext(os.path.basename(shp_file))[0])
if not os.path.exists(file_name):
    print datetime.now()
    start = timeit.default_timer()
    dis_mtx = CalcDistanceMatrix(shp_file,50000)
    stop = timeit.default_timer()
    print stop - start
    SaveSparseMatrix(file_name,dis_mtx)
else:
    print "Skip Calculating, Load Matrix from {}.".format(file_name)
    dis_mtx = LoadSparseMatrix(file_name)

distances = [100,500,1000,2000,10000]
for distance in distances:
    print "Clustering City at {} meters".format(distance)
##    start = timeit.default_timer()
##    cluster_dict = GetClusterDict(dis_mtx,distance)
##    stop = timeit.default_timer()
##    print stop - start
    
    start = timeit.default_timer()
    #which_cluster = Clustering(cluster_dict)
    which_cluster = Clustering_nx(dis_mtx,distance)
    stop = timeit.default_timer()
    print stop - start
    
    StoreIntoFile(shp_file,distance,which_cluster)
