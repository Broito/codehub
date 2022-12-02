# %%
import pandas as pd
import os

os.chdir(r'E:\workspace\Thesis_2022_walkability_eye_tracking\analysis_part')
df = pd.read_csv(r'.\原始导出文件\walking_environment_perception Metrics 67.csv')
df['id'] = df['Recording'].apply(lambda a:a.replace('Recording',''))
df_out = pd.read_excel(r'./答案表/template.xlsx','Sheet1')
df_ref = pd.read_excel(r'timeline与图片对应表.xlsx','Sheet1')

# %%
def extract_info(group,media):
    items = media.split('_')
    col = items[0]
    photo = '_'.join(items[1:-1])
    suffix = items[-1]
    # 定位出行目的
    if group[-1] == '1' and col[0] == 'G':
        aim = 'commute'
    elif group[-1] == '2' and col[0] == 'G':
        aim = 'shopping'
    elif col[0] == 'L':
        aim = 'Leisure'
    else:
        aim = 'not_aim'
    # 定位问题与答案
    if "熟悉" in media:
        ans_col = 'familiarity'
    elif "安全" in media and "1" in suffix:
        ans_col = 'safety_car'
    elif "安全" in media and "2" in suffix:
        ans_col = 'safety_bicycle'
    elif "安全" in media and "3" in suffix:
        ans_col = 'safety_self'
    elif "舒适" in media:
        ans_col = 'comfort'
    elif "吸引" in media and "1" in suffix:
        ans_col = 'attract_walk'
    elif "吸引" in media and "2" in suffix:
        ans_col = 'attract_run'
    elif "吸引" in media and "3" in suffix:
        ans_col = 'attract_dog'
    else:
        ans_col = 'not_ans'
    # 定位图片所处的条件
    if col == "G4" or col == "L4":
        condition = 'noise_low'
    elif col == "G8" or col == "L8":
        condition = 'noise_high'
    elif photo[0] == 'B' and photo[-1] == '1':
        condition = 'sign_pedes'
    elif photo[0] == 'C' and photo[-1] == '1':
        condition = 'hint_school'
    elif photo[0] == 'C' and photo[-1] == '2':
        condition = 'hint_hospital'
    elif photo[0] == 'C' and photo[-1] == '3':
        condition = 'hint_commercal'
    elif photo[0] == 'C' and photo[-1] == '4':
        condition = 'hint_park'
    elif photo[0] == 'C' and photo[-1] == '5':
        condition = 'hint_residential'
    else:
        condition = None
    return aim,condition,photo,ans_col

# %%
# 找到所有的场景索引
df_bare = df[df['Media'].apply(lambda a: True if "裸图" in a and ',' not in a else False)]
df_bare['scenario_id'] = df_bare["id"].apply(lambda a:a+'_')+df_bare['Media'].apply(lambda a: '_'.join(a.split('_')[:2]))
for i in df_bare.iterrows():
    index = i[0]
    item = i[1]
    scenario_id = item['scenario_id']
    df_out.loc[index,'scenario_id'] = scenario_id

df_out.index = df_out['scenario_id']
# %% 
for i in df.iterrows():

    index = i[0]
    item = i[1]
    p_id = item['id']
    media = item['Media']
    scenario_id =  p_id+'_'+'_'.join(media.split('_')[:2])
    answer = item['Last_key_press']

    group = item['Timeline']
    participate_id = p_id
    bicycle_time = item['bicycle_time']
    exercise_time = item['exercise_time']
    gender = item["gender"]
    major = item["major"]
    run_time = item["run_time"]
    walking_time = item["walking_time"]

    # 判断是否为问题答案
    if "_" not in media or ',' in media or '温' in media:
        continue
    # 提取条件、图名和问题答案
    aim,condition,photo,ans_col = extract_info(group,media)

    # 写入
    df_out.loc[scenario_id,"group"]= group
    df_out.loc[scenario_id,"participate_id"]= participate_id
    df_out.loc[scenario_id,"bicycle_time"]= bicycle_time
    df_out.loc[scenario_id,"exercise_time"]= exercise_time
    df_out.loc[scenario_id,"gender"]= gender
    df_out.loc[scenario_id,"major"]= major
    df_out.loc[scenario_id,"run_time"]= run_time
    df_out.loc[scenario_id,"walking_time"]= walking_time
    df_out.loc[scenario_id,"photo_name"]= photo
    df_out.loc[scenario_id,"condition_aim"]= aim
    df_out.loc[scenario_id,"condition_addi"]= condition
    df_out.loc[scenario_id,ans_col]= answer

    print(scenario_id)

df_out.to_excel("答案提取_67v_a-12替换.xlsx",encoding = 'utf8')

      




    


    


























# %%
