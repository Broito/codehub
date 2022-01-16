import urllib.request
import json
from fake_useragent import UserAgent
import socket
from datetime import datetime, date, timedelta
from lxml import etree
import pandas as pd
import numpy as np

def req_open_html(url):
    print('req_open_html begin')
    location = r"E:\workspace\Group_2021_crawling_migrate\fake_useragent.json"
    ua = UserAgent(path = location)
    headers = {'User-Agent': ua.random}
    print(headers)
    request = urllib.request.Request(url, headers=headers)
    NET_STATUS = False
    while not NET_STATUS:
        try:
            html = urllib.request.urlopen(request, data=None, timeout=10).read().decode('utf-8')
            print('NET_STATUS is good')
            print('req_open_html end')
            return html
        except socket.timeout:
            print('NET_STATUS is not good')
            NET_STATUS = False

month = ['01','02','03','04','05','06','07','08','09','10','11','12']
year = list(map(lambda a: str(a),list(range(2011,2021))))
yymm = []
for y in year:
    for m in month:
        yymm.append(y+m)

url_header = 'https://lishi.tianqi.com/shanghai/'
urls = list(map(lambda a: url_header+a+'.html',yymm))

for url in urls[69:]:
    html = req_open_html(url)
    html = etree.HTML(html)
    
    date = html.xpath('//ul[@class="thrui"]/li/div[@class="th200"]/text()')
    date = list(map(lambda a: str(a).strip(' '),date))
    weather = html.xpath('//ul[@class="thrui"]/li/div[@class="th140"]/text()')
    weather = list(map(lambda a: str(a),weather))
    weather_id = list(map(lambda a: a*4+2,list(range(len(date)))))
    weather = [weather[i] for i in weather_id]
    
    df = pd.DataFrame(data = np.array([date,weather]).T,columns = ['date','weather'])
    df.to_csv(r"C:\Users\NingchengWang\Desktop\上海历史天气.csv",encoding = 'GB18030',mode = 'a', header=False)
    

































