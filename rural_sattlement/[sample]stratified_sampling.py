from contextlib import redirect_stderr
from numpy import unravel_index
import geopandas as gpd
import pandas as pd
import random
import os
from dbfread import DBF
import numpy as np

os.chdir(r'E:\workspace\Research_2022_rural_settlement\work_space\空间分层抽样\result')
gdf = gpd.GeoDataFrame.from_file(r"E:\workspace\Research_2022_rural_settlement\work_space\地级市空间分层.gdb",
                                 driver='OpenFileGDB',
                                 layer="china_rural_settlement_with_region")
gdf.rename(columns={'城乡分':'ur_code'},inplace=True)
df = pd.read_csv('调整后各层分配数.csv')

out_gdf = gdf.drop(gdf.index)

for ref_row in df.iterrows():
    items = ref_row[1]
    region_id = items['district_i']
    Nh112_adj = items['Nh112_adj']
    Nh122_adj = items['Nh122_adj']
    Nh210_adj = items['Nh210_adj']
    Nh220_adj = items['Nh220_adj']

    ur_code = [112,122,210,220]
    ur_n = [Nh112_adj,Nh122_adj,Nh210_adj,Nh220_adj]
    
    for code,n in zip(ur_code,ur_n):
        cdd_gdf = gdf[(gdf['ur_code']==code)&(gdf['district_id']==region_id)]
        cdd_index = list(cdd_gdf.index)
        selected_index = np.random.choice(cdd_index,int(n),replace=False)
        random_gdf = cdd_gdf.loc[selected_index]
        out_gdf = out_gdf.append(random_gdf)
        print(f'region_id:{region_id},code:{code},n:{n}. ')

out_gdf.to_file('样本点2386.shp',encoding = 'gb18030')

    





















