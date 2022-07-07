import geopandas as gpd
gdf = gpd.read_file(r"E:\\workspace\\【獭獭】\\养老机构\\带街道的养老机构.shp",encoding="utf8")
gdf.to_file(r"E:\\workspace\\【獭獭】\\养老机构\\带街道的养老机构.json", driver='GeoJSON',encoding="utf8") 
