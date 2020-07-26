# -*- coding: utf-8 -*-
__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20200724"

import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.stats import spearmanr
from getTradingDate import getTradingDateFromJY
from utils import weightmeanFun, basic_data, stock_dif, performance, performance_anl
from datareader import loadData
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import statsmodels.api as sm
import os
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# 读取一个目录里面的所有文件：
def read_path(path):
    dirs = os.listdir(path)
    return dirs

def getpath(dir,file_path):
    full_path=file_path+'/'+dir+'/'
    return full_path

class Para:
    path = 'D:/learning_by_doing/研究5 改进杜邦分析体系的基本面因子/'
    data_path = '.\\data\\'
    result_path = '.\\result\\'
    pass
para = Para()

source_path = getpath('result/industry',para.path)  # 存放excel文件
tag_path = getpath('data',para.path)  # 输出csv的文件
dir = read_path(source_path)
data_list = []
industry_name = pd.read_csv(para.data_path + 'industry.csv',index_col=0)
for i in dir:
    source_file = source_path + i
    csv_data = pd.read_csv(source_file, index_col=0)
    csv_data.columns = ['industry','%s'%i]
    csv_data.sort_values(by = 'industry', ascending = True, inplace= True) # 降序排列
    data_list.append(csv_data['%s'%i])
data = pd.DataFrame(data_list).T
data['industry_name'] = industry_name.iloc[:,1]
data.to_csv('data_industry.csv',encoding='utf_8_sig')