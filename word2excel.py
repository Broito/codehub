import os
from docx import Document
from xlrd import open_workbook
from xlutils.copy import copy

# 这里是存放word的文件夹路径
os.chdir(r'C:\Users\NingchengWang\Desktop\word转excel\广元路（宛平路-余庆路）南侧-（90400507S001）-（17）棵')
# 报错记录文件，结束后请查阅。
log = open(r'C:\Users\NingchengWang\Desktop\word转excel\log.txt','a')
docs = list(os.walk('.'))[0][2]
for file in docs:
    try:
        doc = Document(file)
        # 这是excel文件路径
        r_xls = open_workbook(r"C:\Users\NingchengWang\Desktop\word转excel\导出数据.xls") # 读取excel文件
        row = r_xls.sheets()[0].nrows # 获取已有的行数
        excel = copy(r_xls) # 将xlrd的对象转化为xlwt的对象
        table = excel.get_sheet(0) # 获取要操作的sheet
        tb = doc.tables
        
        # table 1
        col1 = tb[0].rows[0].cells[1].text
        
        col2 = tb[0].rows[15].cells[1].text
        col2 = col2[col2.index('=')+1:col2.index('m')]
        col3 = tb[0].rows[15].cells[4].text[:-1]
        col3 = 0 if col3 == '' else col3
        col4 = tb[0].rows[16].cells[4].text[:-1]
        col4 = 0 if col4 == '' else col4
        col5 = tb[0].rows[17].cells[4].text[:-1]
        col5 = 0 if col5 == '' else col5
        
        col6 = tb[0].rows[12].cells[1].text
        col6 = col6[col6.index('=')+1:col6.index('m')]
        col7 = tb[0].rows[12].cells[4].text[:-1]
        col7 = 0 if col7 == '' else col7
        col8 = tb[0].rows[13].cells[4].text[:-1]
        col8 = 0 if col8 == '' else col8
        col9 = tb[0].rows[14].cells[4].text[:-1]
        col9 = 0 if col9 == '' else col9
        
        col10 = tb[0].rows[9].cells[1].text
        col10 = col10[col10.index('=')+1:col10.index('m')]
        col11 = tb[0].rows[9].cells[4].text[:-1]
        col11 = 0 if col11 == '' else col11
        col12 = tb[0].rows[10].cells[4].text[:-1]
        col12 = 0 if col12 == '' else col12
        col13 = tb[0].rows[11].cells[4].text[:-1]
        col13 = 0 if col13 == '' else col13
        
        insert_values = [col1,col2,col3,col4,col5,col6,col7,col8,col9,col10,col11,col12,col13]
        
        # table 5
    
        latter_len = len(tb[4].rows)-5
        # 表格共统计5圈的情况
        if latter_len == 20:
            t5_cols = list(range(10,25))+list(range(5,10))
            excel_cols = list(range(34))
            
            for i in t5_cols:
                text = tb[4].rows[i].cells[3].text
                text = 0 if text == '' else int(text)
                insert_values.append(text)
                
            for i,value in zip(excel_cols,insert_values):
                table.write(row,i,value)
            
            # 检核
            total = sum(insert_values[-5:])
            former = sum(insert_values[-20:-5])
            if total != former:
                log.write(f'{file}检核不成功，请手动查阅。\n')
                print(f'{file}检核不成功，请手动查阅。')
        
        # 表格共统计4圈的情况
        elif latter_len == 16:
            t5_cols = list(range(9,21))+list(range(5,9))
            excel_cols = list(range(25))+list(range(28,32))
            
            for i in t5_cols:
                text = tb[4].rows[i].cells[3].text
                text = 0 if text == '' else int(text)
                insert_values.append(text)
                
            for i,value in zip(excel_cols,insert_values):
                table.write(row,i,value)
            
            # 检核
            total = sum(insert_values[-4:])
            former = sum(insert_values[-16:-4])
            if total != former:
                log.write(f'{file}检核不成功，请手动查阅。\n')
                print(f'{file}检核不成功，请手动查阅。')
        
        # 表格共统计3圈的情况
        elif latter_len == 12:
            t5_cols = list(range(8,17))+list(range(5,8))
            excel_cols = list(range(22))+list(range(28,31))
            
            for i in t5_cols:
                text = tb[4].rows[i].cells[3].text
                text = 0 if text == '' else int(text)
                insert_values.append(text)
                
            for i,value in zip(excel_cols,insert_values):
                table.write(row,i,value)
            # 检核
            total = sum(insert_values[-3:])
            former = sum(insert_values[-12:-3])
            if total != former:
                log.write(f'{file}检核不成功，请手动查阅。\n')
                print(f'{file}检核不成功，请手动查阅。')
        
        else:
            print(col1+' 有未知错误，请检查。')
            log.write(file + ' 有未知错误，请检查。\n')
        
        
        # 同样是excel的文件路径，跟之前的一致
        excel.save(r"C:\Users\NingchengWang\Desktop\word转excel\导出数据.xls")
        print(f'{file}转换成功，{docs.index(file)+1}/{len(docs)}。')
    
    # 防报错终止
    except:
        print(col1+' 有未知错误，请检查。')
        log.write(file + ' 有未知错误，请检查。\n')
        continue

log.close()

















