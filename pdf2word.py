# -*- coding: utf-8 -*-
"""
Created on Mon May 21 18:19:22 2018

@author: 王宁诚
"""

from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams,LTTextBox
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import win32com
                    
'''
 解析pdf 文本，保存到txt文件中
'''

#path = r'E:\sophomore_year_2\计算机综合实践\小程序\第一章 绪论-2.pdf'
def parse(path):
    fp = open(path, 'rb') # 以二进制读模式打开
    #用文件对象来创建一个pdf文档分析器
    praser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    praser.set_document(doc)
    doc.set_parser(praser)

    # 提供初始化密码
    # 如果没有密码 就创建一个空的字符串
    doc.initialize()

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # 循环遍历列表，每次处理一个page的内容
        for page in doc.get_pages(): # doc.get_pages() 获取page列表
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，  
            for x in layout:
                #如果是x文字类型
                if (isinstance(x, LTTextBox)):
                    #插入文字
                    myRange.InsertAfter(x.get_text()) 
            myRange.InsertAfter('\n') 


def pdf_to_word(inputpath,outpath):
    #使用启动独立的进程
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
        myRange = doc.Range(0,0) 
        parse(inputpath)
    #退出并保存word文档
    except PermissionError as reason:
        print(str(reason))
    finally:
        w.Quit()
