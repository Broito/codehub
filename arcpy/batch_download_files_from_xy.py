import geopandas as gpd
import os
import urllib.request

os.chdir(r'I:\DataHub\Landuse_GAIA')
gdf = gpd.read_file(r'GAIA_nameID_China.shp')

for row in gdf.iterrows():
    index = row[0]
    item = row[1]
    grid_id = item['fName_ID']
    lat,lon = grid_id.split('_')
    if len(lon) == 2:
        lon = '0'+lon
    elif len(lon) == 1:
        lon = '00' + lon
    url = f'http://data.ess.tsinghua.edu.cn/data/GAIA/GAIA_1985_2018_{lat}_{lon}.tif'
    f = urllib.request.urlopen(url)
    data = f.read()
    with open(f"GAIA_1985_2018_{lat}_{lon}.tif",'wb') as code:
        code.write(data)
        print(url)
