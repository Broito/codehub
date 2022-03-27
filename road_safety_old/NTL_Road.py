import datetime

f = open(r'E:\Junior_year_2\全球环境变化\作业五\SN_m_tot_V2.0.txt')
time = []
sunspot = []
t = []
for line in f:
    info = line.split()
    for i in range(3,len(info),6):
        sunspot.append(float(info[i]))
    for i in range(0,len(info),6):
        time.append(datetime.datetime.strptime(info[i]+info[i+1],'%Y%m'))
    for i in range(2,len(info),6):
        t.append(float(info[i]))

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# matplotlib inline
fig = plt.figure(figsize=(18, 6))
ax = fig.add_subplot(111)
p1, = ax.plot_date(time, sunspot, 'o-', color = 'blue', linewidth = 1, label =
'$CO_2$',markersize=0)
ax.set_xlim(time[0],time[-1])
ax.xaxis.set_major_locator(mdates.YearLocator(6))
plt.xticks(rotation=45)
plt.xlabel('Year',fontsize=14)
plt.ylabel('Number',fontsize=14)
plt.title('monthly sunspot number',fontsize=16)
plt.show()