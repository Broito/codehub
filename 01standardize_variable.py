import pandas as pd

df = pd.read_excel(r"E:\workspace\Research_2021_weather_collision\data_processing\collision_weather_20210925.xls",'collision_weather_20210924_std')


def std01(var_name):
    var_name = var_name
    var_01 = var_name+'_01'
    df[var_01] = df[var_name].apply(lambda a: (a-min(df[var_name]))/(max(df[var_name])-min(df[var_name])))


name_list = ['tree_area','avg_height','Avg_VEGETATION','Avg_BUILDING']
for i in name_list:
    std01(i)

df['div_tree'] = df['tree_area_01']/df['Avg_VEGETATION_01']
df['div_building'] = df['avg_height_01']/df['Avg_BUILDING_01']

new_table = df.loc[:,['roadid_sim','name','roadgrade','road_width','div_tree','div_building']]


































