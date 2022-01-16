import pandas as pd
import os

os.chdir(r'E:\workspace\Research_2022_resilient_city')
df = pd.read_excel('work_index_20211016.xlsx','Sheet8')
df.index = df['city_code']
