# -*- coding: utf-8 -*-
# __author__ = "Mengxuan Chen"
# __email__  = "chenmx19@mails.tsinghua.edu.cn"
# __date__   = "20200716"

import numpy as np
import pandas as pd
from tqdm import tqdm
import warnings
from getTradingDate import getTradingDateFromJY
from utils import stock_dif
warnings.filterwarnings('ignore')


class Para():
    data_path = '.\\data\\'
    result_path = '.\\result\\'
    dataPathPrefix = 'D:\caitong_security'
    startDate = 20051231
    endDate = 20200430
    pass
para = Para()
tradingDateList = getTradingDateFromJY(para.startDate, para.endDate, ifTrade=True, Period='M')

# In[]
# 外部融资销售增长比=经营资产销售百分比-经营负债销售百分比-［（1+g）/g］×预计营业净利率×（1-预计股利支付率）=0
dividend = pd.read_csv(para.result_path + '股利支付.csv', index_col=0)
dividend.fillna(method = 'ffill',axis = 0,inplace=True)
dividend.fillna(0,inplace = True)

net_profit = pd.read_csv(para.result_path + '净利润.csv', index_col=0)
net_profit.fillna(method = 'ffill',axis = 0,inplace=True)
net_profit.fillna(0,inplace = True)

dividend = stock_dif(dividend.T,net_profit.T).T
dividend.columns = net_profit.columns.copy()
dividend_rate = np.array(dividend) / np.array(net_profit)
dividend_rate = pd.DataFrame(dividend_rate,index = net_profit.index, columns=net_profit.columns)
dividend_rate = stock_dif(dividend_rate.T, net_profit.T).T
dividend_rate = dividend_rate.loc[:,str(para.startDate):str(para.endDate)]
# dividend_rate.columns = tradingDateList[:-1]
# In[]
# 预计经营资产负债
# 各项经营资产（或负债）=预计营业收入×各项目销售百分比
# 预计营业收入, 一致预期数据, 单位百万元
conPreSales = pd.read_hdf(para.dataPathPrefix +
'\DataBase\Data_AShareConsensusData\Data_Consensus\Data_StockForecast\Data\BasicDailyFactor_Stock_con_or.h5')
# 一致预期净利润, 单位百万元
conPreNetprofit = pd.read_hdf(para.dataPathPrefix +
'\DataBase\Data_AShareConsensusData\Data_Consensus\Data_StockForecast\Data\BasicDailyFactor_Stock_con_np.h5')
# 一致预期净资产， 单位百万元
conPreNetAsset = pd.read_hdf(para.dataPathPrefix +
'\DataBase\Data_AShareConsensusData\Data_Consensus\Data_StockForecast\Data\BasicDailyFactor_Stock_con_na.h5')
# In[]
PreSales_M = []
PreNetprofit_M = []
PreNetasset_M = []
for i, currentDate in enumerate(tqdm(tradingDateList)):
    PreSales_M.append(conPreSales.loc[currentDate, :])
    PreNetprofit_M.append(conPreNetprofit.loc[currentDate, :])
    PreNetasset_M.append(conPreNetAsset.loc[currentDate, :])
# conPreSales_M
conPreSales_M = pd.DataFrame(PreSales_M,
                             columns = conPreSales.columns.copy(),
                             index = tradingDateList)
conPreSales_M = conPreSales_M.loc[str(para.startDate):str(para.endDate),:]
conPreSales_M = stock_dif(conPreSales_M,net_profit.T).T
# conPreNetprofit_M
conPreNetprofit_M = pd.DataFrame(PreNetprofit_M,
                             columns = conPreSales.columns.copy(),
                             index = tradingDateList)
conPreNetprofit_M = conPreNetprofit_M.loc[str(para.startDate):str(para.endDate),:]
conPreNetprofit_M = stock_dif(conPreNetprofit_M,net_profit.T).T
# conPreNetAsset_M
conPreNetAsset_M = pd.DataFrame(PreNetasset_M,
                             columns = conPreSales.columns.copy(),
                             index = tradingDateList)
conPreNetAsset_M = conPreNetAsset_M.loc[str(para.startDate):str(para.endDate),:]
conPreNetAsset_M = stock_dif(conPreNetAsset_M,net_profit.T).T


# In[]
# 确定销售百分比
# 各项目销售百分比=基期经营资产（负债）÷基期营业收入
# operating_asset_sales = np.array(operating_asset) / np.array(sales)
# operating_liability_sales = np.array(operating_liability) / np.array(sales)
# 经营资产销售百分比, 经营负债销售百分比
operating_asset = pd.read_csv(para.result_path + 'operating_asset.csv',index_col=0)
operating_asset = operating_asset.loc[:,str(para.startDate):str(para.endDate)]
operating_liability = pd.read_csv(para.result_path + 'operating_liability.csv',index_col=0)
operating_liability = operating_liability.loc[:,str(para.startDate):str(para.endDate)]

sales = pd.read_csv(para.result_path + '营业总收入.csv',index_col=0)
sales.fillna(method = 'ffill',axis = 0,inplace=True)
sales = sales.loc[:,str(para.startDate):str(para.endDate)]

equity = pd.read_csv(para.result_path + '股东权益.csv',index_col=0)
equity.fillna(method = 'ffill',axis = 0,inplace=True)
equity = equity.loc[:,str(para.startDate):str(para.endDate)]
# 经营资产预期销售比=(当期经营资产/当期净资产)*分析师一致预期净资产/分析师一致预期营业收入
operating_asset_sales = (np.array(operating_asset) / np.array(equity))  \
                       * (np.array(conPreNetAsset_M) / np.array(conPreSales_M))
operating_asset_sales = pd.DataFrame(operating_asset_sales,
                                     index = operating_asset.index,
                                     columns=operating_asset.columns)
operating_asset_sales = operating_asset_sales.loc[:,str(para.startDate):str(para.endDate)]
operating_asset_sales = stock_dif(operating_asset_sales.T, net_profit.T).T
operating_asset_sales.columns = conPreNetprofit_M.columns.copy()

# In[]
# 经营负债预期销售比=(当期经营负债/当期净资产)*分析师一致预期净资产/分析师一致预期营业收入
operating_liability_sales = (np.array(operating_liability) / np.array(equity))  \
                            * (np.array(conPreNetAsset_M) / np.array(conPreSales_M))
operating_liability_sales = pd.DataFrame(operating_liability_sales,
                                         index = operating_liability.index,
                                         columns=operating_liability.columns)
operating_liability_sales = operating_liability_sales.loc[:,str(para.startDate):str(para.endDate)]
operating_liability_sales = stock_dif(operating_liability_sales.T, net_profit.T).T
operating_liability_sales.columns = conPreNetprofit_M.columns.copy()


# In[]
numerator = np.array(operating_asset_sales.iloc[:,:-1]) - np.array(operating_liability_sales.iloc[:,:-1])
sales = pd.read_csv(para.result_path + '营业总收入.csv',index_col=0)
sales.fillna(method = 'ffill',axis = 0,inplace=True)
sales = stock_dif(sales.T, net_profit.T).T
sales = sales.loc[:,str(para.startDate):str(para.endDate)]
# 分析师一致预期净利率=分析师一致预期净利润/分析师一致预期营业收入
conPreNetprofitrate = np.array(conPreNetprofit_M.iloc[:,:-1]) / np.array(conPreSales_M.iloc[:,:-1])
denominator = np.array(conPreNetprofitrate) * (1-np.array(dividend_rate))
g_implicit =  denominator / (numerator - denominator)
g_implicit = pd.DataFrame(g_implicit,
                          index=net_profit.index,
                          columns=tradingDateList[1:])
g_implicit.to_csv(para.result_path + 'g_implicit.csv')

# In[]
# 使用期初权益乘数计算：可持续增长率=营业净利率×总资产周转次数×权益乘数×利润留存率
# 使用期末权益乘数计算：可持续增长率=（营业净利率×总资产周转次数×权益乘数×利润留存率）/（1-营业净利率×总资产周转次数×权益乘数×利润留存率）

asset = pd.read_csv(para.result_path + '总资产.csv',index_col=0)
asset.fillna(method = 'ffill',axis = 0,inplace=True)
asset = stock_dif(asset.T, net_profit.T).T
asset = asset.loc[:,str(para.startDate):str(para.endDate)]
# 可持续增长率=分析师一致预期营业收入/分析师一致预期净资产*(当期净资产/当期总资产)* (1-股利支付率)
g_sustainable = (np.array(conPreSales_M.iloc[:,:-1]) / np.array(conPreNetAsset_M.iloc[:,:-1]))\
                * (np.array(equity.iloc[:,:-1]) / np.array(asset)) \
                * (1-np.array(dividend_rate))
g_sustainable = pd.DataFrame(g_sustainable,
                          index=net_profit.index,
                          columns=tradingDateList[1:])
g_sustainable.to_csv(para.result_path + 'g_sustainable.csv')
