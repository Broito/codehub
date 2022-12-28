# %%
import pandas as pd
import os 
import numpy as np
from PIL import Image
from datetime import datetime

# %%
os.chdir(r'E:\workspace\Thesis_2022_walkability_eye_tracking\analysis_part')
total_df = pd.read_excel('答案总表_v67_眼动语义汇总_回归版.xlsx','Sheet1')

select_names = ['building', 'fence',
       'person', 'road', 'sidewalk', 'vegetation', 'bicycle', 'motorcycle',
       'car', 'wall', 'traffic sign', 'sky']
label_names = ['unlabeled','dynamic', 'ground', 'road', 'sidewalk', 'parking', 'rail track', 'building', 'wall', 'fence', 'guard rail', 'bridge', 'tunnel', 'pole', 'traffic light', 'traffic sign', 'vegetation', 'terrain', 'sky', 'person', 'rider', 'car', 'truck', 'bus', 'caravan', 'trailer', 'train', 'motorcycle', 'bicycle']
label_rgbs = [[0, 0, 0], [111, 74, 0], [81, 0, 81], [128, 64, 128], [244, 35, 232], [250, 170, 160], [230, 150, 140], [70, 70, 70], [102, 102, 156], [190, 153, 153], [180, 165, 180], [150, 100, 100], [150, 120, 90], [153, 153, 153],  [250, 170, 30], [220, 220, 0], [107, 142, 35], [152, 251, 152], [70, 130, 180], [220, 20, 60], [255, 0, 0], [0, 0, 142], [0, 0, 70], [0, 60, 100], [0, 0, 90], [0, 0, 110], [0, 80, 100], [0, 0, 230], [119, 11, 32]]
label_tuple = list(zip(label_rgbs,label_names))
df_label = pd.DataFrame(label_tuple,columns=['rgb','name'])
df_label.index = df_label['name']
df_label = df_label.loc[select_names,:]
df_label.index = df_label['rgb'].apply(lambda a: str(a))

photo_df = pd.DataFrame(columns=['photo_name']+list(i+'_px' for i in select_names))

photo_names = total_df['scenario_id'].apply(lambda a: '_'.join(a.split('_')[2:])).unique()
for photo_name in photo_names:
    img = Image.open(f'E:\\workspace\\Thesis_2022_walkability_eye_tracking\\analysis_part\\语义分割结果\\{photo_name}.png').convert('RGB')
    matrix = np.array(img)
    colours, counts = np.unique(matrix.reshape(-1,3), axis=0, return_counts=1)
    colours,counts = list(list(i) for i in colours),list(counts)
    items = [photo_name]
    for i in df_label['rgb']:
        try:
            items.append(counts[colours.index(i)]/7077888)
        except:
            items.append(0)
            continue
    new_row = pd.Series(items,index=['photo_name']+list(i+'_px' for i in select_names))
    photo_df = photo_df.append(new_row, ignore_index = True)
    print(photo_name)
    
photo_df.index = photo_df['photo_name']
total_df['photo_key'] = total_df['scenario_id'].apply(lambda a: '_'.join(a.split('_')[2:]))
output_df = total_df.join(photo_df,on = 'photo_key', lsuffix='_left', rsuffix='_right')    
output_df.to_excel('答案总表_v67_眼动语义汇总_回归版_像元统计.xlsx',encoding = 'utf8')















