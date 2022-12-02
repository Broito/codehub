# %%
import pandas as pd
import os 
import numpy as np
from PIL import Image

# %%
os.chdir(r'E:\workspace\Thesis_2022_walkability_eye_tracking\analysis_part')
# 清洗修改一下总表
total_df = pd.read_excel('答案总表_v67_modified.xlsx','答案总表_v67')
# 重新构建总表的场景id，修正原有的尾端B打头照片少后缀的问题
total_df['scenario_id'] = total_df.apply(lambda row: row['scenario_id']+'_'+row['photo_name'][-1] if 'B' in row['scenario_id'] else row['scenario_id'], axis=1)
total_df['scenario_id'] = total_df['scenario_id'].apply(lambda a: a.replace('d','D'))
total_df.index = total_df['scenario_id']

# %% 读单个表
df = pd.read_excel(r'.\原始导出文件\原始数据清洗\15.xlsx','walking_environment_perception ')

# %% 筛选记录
df = df[df['Presented Media name']!='nan'] # 去除没有刺激物的
df['Presented Media name'] = df['Presented Media name'].astype('str')
df = df[df['Presented Media name'].apply(lambda a: True if ('_' in a) and ('温' not in a) else False)] # 找出有编码的街景刺激物
df = df[df['Eye movement type'] == 'Fixation'] # 找出所有的注视的记录
df = df[(df['Fixation point X']>240) & (df['Fixation point X']<1680)] # 筛选出注视图片的注视点
df['Presented Media name'] = df['Presented Media name'].apply(lambda a:a.replace('d','D'))

# %% 注视点坐标转换，将屏幕坐标转换为图片坐标
df['trans_X'] = df['Fixation point X'].apply(lambda a:int((a-512)/1920*4096))
df['trans_Y'] = df['Fixation point Y'].apply(lambda a:int(a/1080*2304))

# %% 关联图片要素
label_names = ['unlabeled','dynamic', 'ground', 'road', 'sidewalk', 'parking', 'rail track', 'building', 'wall', 'fence', 'guard rail', 'bridge', 'tunnel', 'pole', 'traffic light', 'traffic sign', 'vegetation', 'terrain', 'sky', 'person', 'rider', 'car', 'truck', 'bus', 'caravan', 'trailer', 'train', 'motorcycle', 'bicycle']
label_rgbs = [(0, 0, 0), (111, 74, 0), (81, 0, 81), (128, 64, 128), (244, 35, 232), (250, 170, 160), (230, 150, 140), (70, 70, 70), (102, 102, 156), (190, 153, 153), (180, 165, 180), (150, 100, 100), (150, 120, 90), (153, 153, 153),  (250, 170, 30), (220, 220, 0), (107, 142, 35), (152, 251, 152), (70, 130, 180), (220, 20, 60), (255, 0, 0), (0, 0, 142), (0, 0, 70), (0, 60, 100), (0, 0, 90), (0, 0, 110), (0, 80, 100), (0, 0, 230), (119, 11, 32)]
label_tuple = list(zip(label_rgbs,label_names))
df_label = pd.DataFrame(label_tuple,columns=['rgb','name'])
df_label.index = df_label['rgb'].apply(lambda a: str(a))

def rgb2label(rgb):
    return df_label.loc[str(rgb),'name']

def get_label(trans_x,trans_y,img_name):
    img = Image.open(f'.\\语义分割结果\\{img_name}.png')
    rgb = img.getpixel((trans_x,trans_y))
    return rgb2label(rgb)

# %% 写入轨迹点所对应的标签
df['photo_name'] = df['Presented Media name'].apply(lambda a: '_'.join(a.split('_')[1:-1]))
df['photo_name'] = df['photo_name'].apply(lambda a: a if "C" not in a else a.split('_')[0])
df['label'] = df.apply(lambda row: get_label(row['trans_X'],row['trans_Y'],row['photo_name']), axis=1)

# df.to_excel(r'.\原始导出文件\原始数据清洗\15_label.xlsx',encoding = 'utf8')
# df = pd.read_excel(r'.\原始导出文件\原始数据清洗\15_label.xlsx','Sheet1')

# %% 统计并写入总表
'''
需要检索的字段 ['road','sidewalk','building','wall','fence','traffic sign','vegetation','sky','person','car','motorcycle','bicycle']
总表新增字段['focus_ground','focus_building','focus_wall','focus_fence','focus_sign','focus_pole','focus_vegetation','focus_sky','focus_person','focus_car','focus_nonmotor']
'sidewalk' 和 'road' 合并为 'ground'
'motorcycle','bicycle'合并为'non-motor'
'''
# 在眼动表里构建出与总表一致的主键
df['id'] = df.apply(lambda row: row['Recording name'].replace('Recording','')+'_'+row['Presented Media name'].split('_')[0]+'_'+row['photo_name'], axis=1)
# 计算双眼平均直径
df['pupil_d'] = df['Pupil diameter left']/2+df['Pupil diameter right']/2
# 分类汇总
df_grpb_pupil = df.groupby(['id']).mean()['pupil_d'].to_frame().reset_index()
df_grpb_label = df.groupby(['id','label']).sum().reset_index()[['id','label','Gaze event duration']] 
# 筛选出要用的label
useful_label = ['road','sidewalk','building','wall','fence','traffic sign','vegetation','sky','person','car','motorcycle','bicycle']
df_grpb_label = df_grpb_label[df_grpb_label['label'].isin(useful_label)]

# %%
# 写入总表：瞳孔直径
for i in df_grpb_pupil.iterrows():
    row = i[1]
    row_id = row['id']
    pupil_d = row['pupil_d']
    total_df.loc[row_id,'pupil_avg'] = pupil_d
# 写入总表：各要素的注视时长
for i in df_grpb_label.iterrows():
    row = i[1]
    row_id = row['id']
    label = row['label']
    duration = row['Gaze event duration']
    total_df.loc[row_id,label] = duration




























# %%
