from numpy import size
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.axislines import Subplot

plt.rcParams["font.family"] = "SimHei"

gdf = gpd.read_file(r"E:\workspace\Research_2022_rural_settlement\work_space\村落验证一张表\村落验证一张表\rural_settlement_total_point_v3.shp")

# %% 分类别
y_fields = ['ner_esa','ner_esri','ner_ghsl','ner_wsf','ner_gaia','ner_gisa2','ner_gisd30','ner_glc30']
i = 1

fig = plt.figure(figsize = (30,15),dpi=300)

for y_field in y_fields:

    ax = Subplot(fig, 2,4,i)
    ax.set_xlabel('真实值')
    ax.set_ylabel(y_field.split('_')[-1]+'预测值')
    fig.add_subplot(ax)

    df = gdf[gdf['ur_code'] == 220]
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'yellow',label = 'village')

    df = gdf[gdf['ur_code'] == 112]
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'red',label = 'urban fringe')

    df = gdf[gdf['ur_code'] == 122]
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'green',label = 'town fringe')

    df = gdf[gdf['ur_code'] == 210]
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'blue',label = 'township')

    ax.legend()
    i = i+1

plt.show()

# %% 分区域
y_fields = ['ner_esa','ner_esri','ner_ghsl','ner_wsf','ner_gaia','ner_gisa2','ner_gisd30','ner_glc30']
i = 1

fig = plt.figure(figsize = (30,15),dpi=300)

for y_field in y_fields:

    ax = Subplot(fig, 2,4,i)
    ax.set_xlabel('真实值')
    ax.set_ylabel(y_field.split('_')[-1]+'预测值')
    fig.add_subplot(ax)

    df = gdf[(gdf['district'] == 'Eastern China') |(gdf['district'] == 'Northeastern China') ]
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'green',label = 'Eastern China')

    df = gdf[gdf['district'] == 'Western China']
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'red',label = 'Western China')

    df = gdf[gdf['district'] == 'Central China']
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'blue',label = 'Central China')

    ax.legend()
    i = i+1

plt.show()

# %% 分城市群
# %% 分区域
y_fields = ['ner_esa','ner_esri','ner_ghsl','ner_wsf','ner_gaia','ner_gisa2','ner_gisd30','ner_glc30']
i = 1

fig = plt.figure(figsize = (30,15),dpi=300)

for y_field in y_fields:

    ax = Subplot(fig, 2,4,i)
    ax.set_xlabel('真实值')
    ax.set_ylabel(y_field.split('_')[-1]+'预测值')
    fig.add_subplot(ax)

    df = gdf[gdf['urbanagg'] == None]
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'gray',label = 'Others')

    df = gdf[gdf['urbanagg'] == 'Chengdu-Chongqing']
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'orange',label = 'Chengdu-Chongqing')

    df = gdf[gdf['urbanagg'] == 'Beijing-Tianjin-Hebei' ]
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'green',label = 'Beijing-Tianjin-Hebei')

    df = gdf[gdf['urbanagg'] == 'Yangtze River Delta']
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'red',label = 'Yangtze River Delta')

    df = gdf[gdf['urbanagg'] == 'Middle-Yangtze']
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'blue',label = 'Middle-Yangtze')

    df = gdf[gdf['urbanagg'] == 'Pearl River Delta']
    x = df['ntr_esa']
    y = df[y_field]
    ax.scatter(x,y,s = 3,c = 'black',label = 'Pearl River Delta')

    ax.legend()
    i = i+1

plt.show()

# %%
