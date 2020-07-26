# -*- coding: utf-8 -*-
__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20200714"

import numpy as np
import pandas as pd
from tqdm import tqdm
from getTradingDate import getTradingDateFromJY
import warnings
warnings.filterwarnings('ignore')


class Para():
    dataPathPrefix = 'D:\caitong_security'
    data_path = '.\\data\\'
    result_path = '.\\result\\'
    pass
para = Para()

df = pd.read_excel(para.data_path+"原始数据集-wind去格式并调整.xlsx", None)
sheet_name = list(df.keys())

def generate_month(df_o):
    data_list = []
    for i in range(int(len(df_o.columns)/4)):
        data_0 = pd.concat([df_o.iloc[:, i*4 + 3],
                           df_o.iloc[:, i*4 + 3],
                           df_o.iloc[:, i*4 + 4],
                           df_o.iloc[:, i*4 + 4],
                           df_o.iloc[:, i*4 + 4],
                           df_o.iloc[:, i*4 + 4],
                           df_o.iloc[:, i*4 + 4],
                           df_o.iloc[:, i*4 + 4],
                           df_o.iloc[:, i*4 + 5],
                           df_o.iloc[:, i*4 + 5],
                           df_o.iloc[:, i*4 + 5],
                           df_o.iloc[:, i*4 + 5]], axis=1)
        data_0.index = df_o.iloc[:,0].copy()
        data_list.append(data_0)
    dataFrame = pd.concat([data_list[0],
                            data_list[1],
                            data_list[2],
                            data_list[3],
                            data_list[4],
                            data_list[5],
                            data_list[6],
                            data_list[7],
                            data_list[8],
                            data_list[9],
                            data_list[10],
                            data_list[11],
                            data_list[12],
                            data_list[13],
                            data_list[14],
                            data_list[15],
                            data_list[16],
                            data_list[17],
                            data_list[18],
                            data_list[19]], axis=1)
    tradingDateList = getTradingDateFromJY('20000831', '20200730', ifTrade=True, Period='M')
    dataFrame.columns =  tradingDateList.copy()
    return dataFrame

for k, factor_k in enumerate(sheet_name):
    df_original = df[sheet_name[k]]
    df_final = generate_month(df_original)
    df_final.to_csv(para.result_path + factor_k + '.csv')

