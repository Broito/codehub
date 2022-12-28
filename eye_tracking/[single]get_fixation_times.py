# %%
import pandas as pd
import os 
import numpy as np

# %%
os.chdir(r'E:\workspace\Thesis_2022_walkability_eye_tracking\analysis_part\原始导出文件\原始数据清洗')
df_total = pd.read_excel('../../答案总表_v67_眼动语义汇总_回归版_像元统计.xlsx','Sheet1')
df_total.index = df_total['scenario_id']

for number in range(1,68):
    df = pd.read_excel(f'walking_environment_perception Recording{number}.xlsx','Sheet1')
    # 构建主键与主表连接
    df['id'] = df.apply(lambda row: row['Recording name'].replace('Recording','')+'_'+row['Presented Media name'].split('_')[0]+'_'+row['photo_name'], axis=1)
    
    # 计算注视次数 
    categories = ['road','sidewalk','building','wall','fence','traffic sign','vegetation','sky','person','car','motorcycle','bicycle']
    ids = list(df['id'].unique())
    for id in ids:
        df_id = df[df['id'] == id]
        id = df_id['id'].values[0]
        label_first = df_id['label'].values[0]
        for category in categories:
            # 计算注视次数
            category_fc = 'fc_'+category
            fixation_count = len(df_id[df_id['label'] == category]['Eye movement type index'].unique())
            df_total.loc[id,category_fc] = fixation_count
        for category in categories: 
            # 计算第一次看见的东西
            category_first = '1st_'+category
            if category == label_first:
                df_total.loc[id,category_first] = 1
            else:
                df_total.loc[id,category_first] = 0
        print(id)

    # 计算第一次注视内容
























