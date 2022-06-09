import os
import urllib.request

os.chdir('I:\Datahub\ODIAC')

def download(url,file):
    f = urllib.request.urlopen(url)
    data = f.read()
    with open(file,'wb') as code:
        code.write(data)
        print(url)

year = list(range(2000,2020))
month = ['01','02','03','04','05','06','07','08','09','10','11','12']

urls = []
files = []
for y in year:
    for m in month:
        y_m = str(y)[-2:]+m
        url = f'https://db.cger.nies.go.jp/nies_data/10.17595/20170411.001/odiac2020b/1km_tiff/{y}/odiac2020b_1km_excl_intl_{y_m}.tif.gz'
        urls.append(url)
        files.append(f'odiac2020b_1km_excl_intl_{y_m}.tif.gz')

for url,file in zip(urls[156:],files[156:]):
    download(url,file)
