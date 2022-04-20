import geopandas as gpd
import os

os.chdir(r'E:\workspace\Research_2022_rural_settlement\work_space\partial_processing\original_settlement_province')
gdf = gpd.GeoDataFrame.from_file(r"E:\workspace\Research_2022_rural_settlement\work_space\whole_data.gdb",
                                 driver='OpenFileGDB',
                                 layer="行政村_dem")
gdf.rename(columns={'RASTERVALU':'dem'},inplace=True)


provinces = gdf['省份'].unique()
# gdf['prov_code'] = gdf['城市代码'].apply(lambda a: str(a)[:2])
for prov in provinces:
    out_name = f'{prov}_settlement.shp'
    gdf_prov = gdf.loc[gdf['省份']==prov]
    gdf_prov.to_file(out_name,encoding = 'GB18030')
    print(f'{prov}完成！')