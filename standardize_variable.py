import pandas as pd
from sklearn.preprocessing import StandardScaler

df = pd.read_excel(r"E:\workspace\Research_2021_weather_collision\data_processing\collision_weather_20210925.xls",'collision_weather_20210924_std')
ss = StandardScaler()
std_data = ss.fit_transform(df.iloc[:,-3:])
std_df = pd.DataFrame(data = std_data,columns = map(lambda a: 'std_'+a,list(df.columns[-3:])))

df2 = pd.concat([df,std_df],axis = 1)
df2.to_csv(r"E:\workspace\Research_2021_weather_collision\data_processing\collision_weather_20211005_std.csv",encoding = 'utf-8')
