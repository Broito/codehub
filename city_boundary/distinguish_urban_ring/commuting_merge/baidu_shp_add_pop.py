import geopandas as gpd

gdf = gpd.read_file(r"E:\workspace\Research_2022_city_boundary\distinguish_ring\result_folder\China_urban_v3_2018\Shapefile\China_urban_v3_2018_no_hole.shp")
gdf.index = gdf['ORIG_FID']

f = open(r"E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\commuting_baidu\指定区域工作及常住人口数量-0.txt")
for row in f:
    item = row.split('\t')
    id = int(item[0])
    pop_type = item[1]
    pop = int(item[2].strip('\n'))
    
    print(id,pop_type,pop)
    if pop_type == '居住':
        gdf.loc[id,'居住'] = pop
    elif pop_type == '工作':
        gdf.loc[id,'工作'] = pop
    print(id)

del gdf['ORIG_FID']
gdf.to_file(r'E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\commuting_baidu\China_urban_2018_with_pop_v2.shp',encoding = 'utf8')



























