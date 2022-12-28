# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# import os
# import os.path as osp

# path = r"E:\workspace\Thesis_2022_walkability_eye_tracking\work_space\3_拍摄点\前三次\labels\label_running"
# files = os.listdir(path)

# for i in files:
#     full_name = osp.join(path, i)
#     if full_name.endswith(".json"):
#         os.system("labelme_json_to_dataset.exe %s" % full_name)
#     print(full_name)
# print ("转换完成.")

# %% 手动版

# 导入各种库
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import os.path as osp
import cv2 as cv
import numpy as np
import json

# %%
# 生成标签图像
# json_file: json 文件
# categories: 类别列表
# color_table: label_viz 颜色索引表
# 返回三张图像, 分别是 原始图, label 和 label_viz, 这样主要是为了和 Labelme 对应起来方便以后处理
def get_label(json_file, categories, color_table = None):
    # 打开 json 文件
    with open(json_file, 'r', encoding = "utf-8") as f:
        jsn = f.read()        
        js_dict = json.loads(jsn)
        
        img_path = js_dict["imagePath"]
        ext_name = osp.splitext(img_path)[1]
        
        img_src = cv.imread(json_file.replace(".json", ext_name)) # 这一步假设 json 和原始图像同名
        src_shape = img_src.shape
    
        label = np.zeros((src_shape[0], src_shape[1]), np.uint8)
        label_viz = np.zeros((src_shape[0], src_shape[1], src_shape[2]), np.float32)
    
        shapes = js_dict["shapes"] # 取出所有图形

        for shape in shapes:
            if shape["label"] in categories:
                cat = categories.index(shape["label"]) # 类别序号
                color = [0, 0, 0]
                
                if color_table:
                    color = color_table[cat]
                    color.reverse() # 因为 opencv 的数据是 BGR 排列, 所以 color 要反一下通道顺序
                
                # 这里只写了 rectangle 和 polygon 其他你自己写
                if shape["shape_type"] == "rectangle":
                    pts = shape["points"]
                    top_left = (round(pts[0][0]), round(pts[0][1]))
                    bottom_right = (round(pts[1][0]), round(pts[1][1]))
                    
                    cv.rectangle(label, top_left, bottom_right, (cat, cat, cat), cv.FILLED)
                    cv.rectangle(label_viz, top_left, bottom_right, color, cv.FILLED)
                    
                elif shape["shape_type"] == "polygon":
                    pts = []
                    pts_float = shape["points"]
                    
                    for pt in pts_float:
                        pts.append((round(pt[0]), round(pt[1])))
                        
                    cv.fillPoly(label, [np.array(pts)], (cat, cat, cat))                    
                    cv.fillPoly(label_viz, [np.array(pts)], color)
                    
                color.reverse() # 还原颜色, 如果不这么做, 会破坏颜色表
        
        gray = cv.cvtColor(img_src, cv.COLOR_BGR2GRAY)
        gray_3 = cv.merge([gray, gray, gray])
        
        # 除以 2 是为了防止溢出和突出显示标注图形
        label_viz /= 2
        label_viz += (gray_3 / 2)
        
        return img_src, label, label_viz

# %%
# 类别列表, 这个表 back_ground 一定要排在最开始, 表示背景
categories = ["back_ground", "sidewalk"]
# label_viz 颜色索引表, 这里我只写了 4 个类别, 其他你自己添加
color_table = [[0, 0, 0], [244, 35,232]]

# json 文件路径, 上面有讲到我的放到了 D 盘, 所以改成你自己的路径
json_file = r"E:\\workspace\\Thesis_2022_walkability_eye_tracking\\work_space\\3_拍摄点\\前三次\\labels\\label_running\\北新泾_A33E5288-AADE-4CD4-80AD-752499A2D0FA_20220926121313_0.json"
img, label, label_viz = get_label(json_file, categories, color_table)

# %%
