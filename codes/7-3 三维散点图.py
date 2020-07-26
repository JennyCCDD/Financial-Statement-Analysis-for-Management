import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
data = pd.read_excel('工作簿1.xlsx',index_col=0)#,encoding='unicode_escape')
data_pos = np.array(data)
#假设已经定好data_pos = ...
x = data_pos[:, 0]
y = data_pos[:, 1]
for i in range(0, len(data.index)):#净经营资产周转率	税后净利率	经营资产
    plt.text(x[i],y[i], data.index[i],fontdict={'size': 9, 'color': 'black'})
plt.xlabel('净经营资产周转率',fontproperties='SimHei')
plt.ylabel('税后净利率',fontproperties='SimHei')
plt.grid()
plt.plot(x, y, 'ro') # ro表示用红色圆点来表示点
plt.savefig('2D.png')# % MAX_EPISODES)
plt.show()



# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
# fig = plt.figure(figsize=(12,10))
# # ax = Axes3D(fig)
# ax = fig.add_subplot(1, 1, 1, projection='3d')
# data = pd.read_excel('工作簿1.xlsx',index_col=0)#,encoding='unicode_escape')
# x = np.array(data.iloc[:, 0])
# y = np.array(data.iloc[:, 1])
# z = np.array(data.iloc[:, 2])
# ax.scatter(x, y, z, c='blue')
# for i in range(0, len(data.index)):#净经营资产周转率	税后净利率	经营资产
#     ax.text(x[i],y[i],z[i], data.index[i],fontdict={'size': 9, 'color': 'black'})
# ax.set_zlabel('经营资产', fontdict={'size': 12, 'color': 'black'})
# ax.set_ylabel('税后净利率', fontdict={'size': 12, 'color': 'black'})
# ax.set_xlabel('净经营资产周转率', fontdict={'size': 12, 'color': 'black'})
#
# plt.tight_layout()
# plt.savefig('3D.png')# % MAX_EPISODES)
# plt.show()