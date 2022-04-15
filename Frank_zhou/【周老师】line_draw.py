import numpy as np
import matplotlib.pyplot as plt

matrix = np.random.randint(0,100,size=(999, 30)) # 生成50行3列的dataframe
avg_list = np.mean(matrix,axis=0)

plt.plot(avg_list)
plt.show()



