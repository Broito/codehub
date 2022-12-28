# %%
import pandas as pd
import os 
import numpy as np
from PIL import Image
from datetime import datetime

# %%
os.chdir(r'E:\workspace\Thesis_2022_walkability_eye_tracking\analysis_part')
total_df = pd.read_excel('答案总表_v67_眼动语义汇总_回归版.xlsx','Sheet1')
toi_df = pd.read_csv('./原始导出文件/walking_environment_perception Metrics 67.csv')

df_bare = toi_df[toi_df['Media'].apply(lambda a: True if '裸图' in a and  ',' not in a else False)]
df_bare['scenario_id'] = df_bare.apply(lambda row: row['Recording'][9:]+'_'+'_'.join(row['Media'].split('_')[:-1]),axis=1)
df_bare['scenario_id'] = df_bare['scenario_id'].apply(lambda a: a.replace('d','D'))
df_bare['scenario_id'] = df_bare['scenario_id'].apply(lambda a: '_'.join(a.split('_')[:-1]) if "C" in a and len(a.split('_')) == 4 else a)


df_bare = df_bare.loc[:,['scenario_id','Total_duration_of_whole_fixations',
       'Average_duration_of_whole_fixations', 'Number_of_whole_fixations',
       'Duration_of_first_whole_fixation',
       'Average_whole-fixation_pupil_diameter', 'Number_of_saccades',
       'Average_peak_velocity_of_saccades',
       'Minimum_peak_velocity_of_saccades',
       'Maximum_peak_velocity_of_saccades',
       'Standard_deviation_of_peak_velocity_of_saccades',
       'Average_amplitude_of_saccades', 'Minimum_amplitude_of_saccades',
       'Maximum_amplitude_of_saccades', 'Total_amplitude_of_saccades']]

df_bare.index = df_bare['scenario_id']
output_df = total_df.join(df_bare,on = 'scenario_id', lsuffix='_left', rsuffix='_right')    

output_df.to_excel('答案总表_v67_眼动语义汇总_回归版_带基础指标.xlsx', encoding='utf8')









