import pandas as pd

df = pd.read_csv(r"C:\Users\NingchengWang\Desktop\上海历史天气.csv",encoding = 'GB18030')
df['date'] = df['date'].map(lambda a: a.replace('/','-'))
df['weather'] = df['weather'].map(lambda a: a.replace('~','转'))

df.to_csv(r"C:\Users\NingchengWang\Desktop\上海历史天气.csv",encoding = 'GB18030')
