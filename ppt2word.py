# -*- coding: utf-8 -*-
"""
Created on Mon May 14 19:10:14 2018

@author: 王宁诚
"""

#r"E:\sophomore_year_2\计算机综合实践\小程序\第一讲(2).ppt"
#'select.txt'
import win32com
import win32com.client
import time
import os

def ppt_to_txt(inputpath,outputpath):
	#打开进程
    ppt = win32com.client.Dispatch('PowerPoint.Application')
	#后台运行，不显示，不警告
    ppt.Visible = 1
	#打开新的文件
    pptSel = ppt.Presentations.Open(inputpath)
    win32com.client.gencache.EnsureDispatch('PowerPoint.Application')
	#创建txt文件以待写入
    f = open(outputpath,"w",encoding = 'utf-8')
	#总共多少ppt页数
    slide_count = pptSel.Slides.Count
	#遍历每页ppt
    for i in range(1,slide_count + 1):
      shape_count = pptSel.Slides(i).Shapes.Count
	  #遍历每页ppt里的各元素
      for j in range(1,shape_count + 1):
	  #如果ppt元素中含有文本内容
        if pptSel.Slides(i).Shapes(j).HasTextFrame:
		#获取文本内容
          s = pptSel.Slides(i).Shapes(j).TextFrame.TextRange.Text
		  #写入文本文件
          f.write(s)
          f.write('\n')
    f.close()
	#关闭ppt
    ppt.Quit()

#上面代码的方法版
def parse(inputpath):
    ppt = win32com.client.Dispatch('PowerPoint.Application')
    ppt.Visible = 1
    pptSel = ppt.Presentations.Open(inputpath)
    win32com.client.gencache.EnsureDispatch('PowerPoint.Application')
    slide_count = pptSel.Slides.Count
    for i in range(1,slide_count + 1):
      shape_count = pptSel.Slides(i).Shapes.Count
      for j in range(1,shape_count + 1):
        if pptSel.Slides(i).Shapes(j).HasTextFrame:
          s = pptSel.Slides(i).Shapes(j).TextFrame.TextRange.Text
          myRange.InsertAfter(s) 
          myRange.InsertAfter('\n')
    ppt.Quit()
    
    
def ppt_to_word(inputpath,outpath):
    #使用启动独立的进程
    win32com.client.gencache.EnsureDispatch('Word.Application')
    w = win32com.client.Dispatch('Word.Application')
    # 后台运行，不显示，不警告
    w.Visible = 0
    w.DisplayAlerts = 0
    # 打开新的文件
    try:
        output = open(outpath,'w')
        output.close()
        doc = w.Documents.Open(outpath)
    #输入文字
        global myRange
        time.sleep(1)
        myRange = doc.Range(0,0) 
        parse(inputpath)
    #退出并保存word文档
    except PermissionError as reason:
        print(str(reason))
    finally:
        w.Quit()

os.chdir('E:\workspace\【獭獭】\zlf\ppt')
ppts = os.listdir()

for ppt in ppts:
    out_word = r'E:\\workspace\\【獭獭】\\zlf\\word\\' + ppt.split('.')[0] + '.docx'
    input_ppt = r'E:\\workspace\\【獭獭】\\zlf\\ppt\\' + ppt
    ppt_to_word(input_ppt,out_word)
    print(ppt)









