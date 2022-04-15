import pandas as pd
import numpy as np
df = pd.read_excel(r"E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\commuting_baidu\通勤数据.xlsx","Sheet1")



# Some example data
# df = pd.DataFrame({"from": np.random.randint(0, 10, (1000,)), "to": np.random.randint(0, 10, (1000,))})
# Remove examples where from == to
# df = df.loc[df["from"] != df["to"]].copy()

# The key operation
matrix = (
    df.assign(value = lambda x:x.通勤人数)
    .pivot_table(index="出发点区域编号", columns="目的地区域编号", values="value")
    .fillna(0)
    .astype(int)
)

matrix.to_excel('E:\workspace\Research_2022_city_boundary\commuting_buffer_merge\commuting_baidu\commuting_matrix.xlsx')                                                                                                                                                                                             



















