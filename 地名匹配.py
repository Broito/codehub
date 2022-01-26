import os
import pandas as pd

os.chdir(r'C:\Users\NingchengWang\Desktop')

ref_df = pd.read_csv(r'2020中国地级市.csv')
df = pd.read_excel(r'text-#test郑州市委书记徐立毅被问责#-21-test.xls','Sheet2')

for i in df.iterrows():
    index = i[0]
    row = i[1]

    content = []
    content += row['content1'].split(' ')
    content += row['content2'].split(' ')
    content += row['content3'].split(' ')
    # print(content)

    candidate = []
    for text in content:
        
        selected = ref_df[ref_df['市'].map(lambda a : text in a )]
        if selected['市'].values.shape == (0,):
            pass
        else:
            match = selected['市'].values[0]
            candidate.append(match)
        
        selected = ref_df[ref_df['省'].map(lambda a : text in a )]
        if selected['省'].values.shape == (0,):
            pass
        else:
            match = selected['省'].values[0]
            candidate.append(match)

    print(candidate)
        

    prov = []
    pref = []
    for a in candidate:
        if "省" in a:
            prov.append(a)
        else:
            pref.append(a)
    if pref == [] and prov != []:
        result = prov[0]
    elif pref != []:
        result = pref[0]
    else:
        result = None
    
    df.loc[index,'地区'] = result

