# -*- coding: utf-8 -*-
__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20200601"
'''
revised: 20200724 
'''

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
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def orthogonalize(regressY, regressX):
    # regressY: 因变量数据
    # regressX: 自变量数据

    # 首先给自变量因子加上截距项
    regressX = sm.add_constant(regressX)

    data = pd.concat([regressX, regressY], axis=1)
    data = data.dropna()

    # 我们不能直接用下面的这种形式，因为它丢失了标签栏的很多信息
    # est = sm.OLS(regressY, regressX, missing = 'drop').fit()

    # 注意,iloc这个是不包含
    est = sm.OLS(data.iloc[:, -1], data.iloc[:, 0:2]).fit()

    df = pd.Series(np.nan, regressX.index)
    df[data.index] = est.resid

    return df

class Para():
    startDate = 20091231
    endDate = 20200508
    groupnum = 3
    groupnum2 = 3
    weightMethod = '简单加权'  # 简单加权 市值加权
    ret_calMethod = '简单'  # 对数
    ret_style = '超额收益'  # 绝对收益 超额收益
    normalize = 'None'  # None Size Size_and_Industry
    sample = 'out_of_sample' # in_sample out_of_sample
    data_path = '.\\data\\'
    result_path = '.\\result\\'
    listnum = 121 # for stock sample at least be listed for listnum of days
    backtestwindow = 60 # number of days used to form portfolios
    fin_stock = 'no' # include finnacial stock or not
    dataPathPrefix = 'D:\caitong_security'
    pass
para = Para()

class main():
    def __init__(self,factorI,factor2I):
        self.tradingDateList = getTradingDateFromJY(para.startDate, para.endDate, ifTrade=True, Period='M')
        self.factorI = factorI
        self.factor2I =factor2I
        self.Price, self.LimitStatus, self.Status, self.listDateNum, self.Industry, self.Size = basic_data(para)
        if self.factorI == 'ROE_DilutedQ':
            DATA = loadData(self.factorI)
            Factor = DATA.BasicDailyFactorAlpha.loc[para.startDate:para.endDate, :]
            self.Factor = stock_dif(Factor, self.LimitStatus)
        else:
            Factor = pd.read_csv(para.result_path + self.factorI + '.csv', index_col=0).T
            # Factor[self.Factor == np.nan] = 0
            Factor[Factor == np.inf] = np.nan
            self.Factor = stock_dif(Factor, self.LimitStatus)
            # self.Factor[self.Factor > 1] = np.nan
        Factor2 = pd.read_csv(para.result_path + self.factor2I + '.csv', index_col=0).T
        # Factor2[self.Factor2 == np.nan] = 0
        Factor2[Factor2 == np.inf] = np.nan
        self.Factor2 = stock_dif(Factor2, self.LimitStatus)
        self.df = pd.read_csv(para.data_path + 'whole.csv', index_col=0)
        pass

    def every_month(self):
        dfList = []
        dfList_abs = []
        for i, currentDate in enumerate(tqdm(self.tradingDateList[:-2])):
            lastDate = self.tradingDateList[self.tradingDateList.index(currentDate) - 1]
            nextDate = self.tradingDateList[self.tradingDateList.index(currentDate) + 1]
            if para.sample == 'in_sample':
                # use different method to calculate the return
                # logreturn for short time period and simple return calculation for long time period
                if para.ret_calMethod == '对数':
                    self.ret = np.log(self.Price.loc[currentDate, :] / self.Price.loc[lastDate, :])
                elif para.ret_calMethod == '简单':
                    self.ret = self.Price.loc[currentDate, :] / self.Price.loc[lastDate, :] - 1
                self.benchmark = pd.Series([self.df.iloc[i, 0]] * len(self.Factor.columns),
                                           index=self.ret.index.copy())
            elif para.sample == 'out_of_sample':
                if para.ret_calMethod == '对数':
                    self.ret = np.log(self.Price.loc[nextDate, :] / self.Price.loc[currentDate, :])
                elif para.ret_calMethod == '简单':
                    self.ret = self.Price.loc[nextDate, :] / self.Price.loc[currentDate, :] - 1
                self.benchmark = pd.Series([self.df.iloc[i + 1, 0]] * len(self.Factor.columns),
                                           index=self.ret.index.copy())
            self.dataFrame = pd.concat([
                                   self.Factor2.loc[str(currentDate), :],
                                   self.Factor.loc[str(currentDate), :],
                                   # self.Factor2.iloc[i, :],
                                   # self.Factor.iloc[i, :],
                                   self.ret,
                                   self.benchmark,
                                   self.LimitStatus.loc[currentDate, :],
                                   self.Status.loc[currentDate, :],
                                   self.listDateNum.loc[currentDate, :],
                                   self.Industry.loc[currentDate, :],
                                   self.Size.loc[currentDate, :]],
                                  axis=1, sort=True)
            self.dataFrame = self.dataFrame.reset_index()
            self.dataFrame.columns = ['stockid',
                                 '%s' % self.factor2I,
                                 '%s' % self.factorI,
                                 'RET',
                                 'Bechmark',
                                 'LimitStatus',
                                 'Status',
                                 'listDateNum',
                                 'Industry',
                                 'Size']

            if para.normalize == 'Size':
                # 市值中性化
                self.dataFrame['factor'] = orthogonalize(self.dataFrame['factor'],self.dataFrame['Size'])
            elif para.normalize == 'Size_and_Industry':
                # 市值中性化与行业中性化
                dummy_Industry = pd.get_dummies(self.dataFrame['Industry'],prefix = 'Industry')
                X = pd.concat([dummy_Industry,self.dataFrame['Size']],axis = 1, sort = False)
                self.dataFrame['factor'] = orthogonalize(self.dataFrame['factor'],X)
            elif para.normalize == 'None':
                pass
            self.dataFrame = self.dataFrame.dropna()
            # dataFrame = dataFrame.loc[dataFrame['factor'] != 0]
            self.dataFrame = self.dataFrame.loc[self.dataFrame['LimitStatus'] == 0]  # 提取非涨跌停的正常交易的数据
            self.dataFrame = self.dataFrame.loc[self.dataFrame['Status'] == 1]  # 提取非ST/ST*/退市的正常交易的数据
            self.dataFrame = self.dataFrame.loc[self.dataFrame['listDateNum'] >= para.listnum]  # 提取上市天数超过listnum的股票
            if para.fin_stock == 'no':  # 非银行金融代号41
                self.dataFrame = self.dataFrame.loc[self.dataFrame['Industry'] != 41]
                self.dataFrame = self.dataFrame.loc[self.dataFrame['Industry'] != 40]

            self.dataFrame['premium'] = self.dataFrame['RET'] - self.dataFrame['Bechmark']

            # 对单因子进行排序打分
            self.dataFrame = self.dataFrame.sort_values(by='%s' % self.factorI, ascending=False)
            # factor描述性统计分析：count, std, min, 25%, 50%, 75%, max
            Des = self.dataFrame['%s' % self.factorI].describe()

            self.dataFrame['Score'] = ''
            eachgroup = int(Des['count'] / para.groupnum)
            for groupi in range(0, int(para.groupnum)):
                self.dataFrame.iloc[groupi * eachgroup:(groupi + 1) * eachgroup, -1] = groupi + 1
            self.dataFrame.iloc[(para.groupnum - 1) * eachgroup:, -1] = para.groupnum

            meanlist = []
            meanlist_abs = []
            for k in range(1, para.groupnum + 1):
                self.dataFrame2 = self.dataFrame.loc[self.dataFrame['Score'] == k, :]
                self.dataFrame2.sort_values(by='%s' % self.factor2I, inplace=True, ascending=False)
                Des2 = self.dataFrame2['%s' % self.factor2I].describe()

                self.dataFrame2['Score2'] = ''
                eachgroup2 = int(Des2['count'] / para.groupnum2)
                for groupj in range(0, int(para.groupnum2)):
                    self.dataFrame2.iloc[groupj * eachgroup2:(groupj + 1) * eachgroup2, -1] = groupj + 1
                self.dataFrame2.iloc[(para.groupnum2 - 1) * eachgroup2:, -1] = para.groupnum2
                if para.weightMethod == '简单加权':
                    meanlist.append(np.array(self.dataFrame2.groupby('Score2')['premium'].mean()))
                    meanlist_abs.append(np.array(self.dataFrame2.groupby('Score2')['RET'].mean()))
                elif para.weightMethod == '市值加权':
                    meanlist_group = []
                    meanlist_abs_group = []
                    for kk in range(1, para.groupnum2 + 1):
                        self.dataFrame2_ = self.dataFrame2.loc[self.dataFrame2['Score2'] == kk, :]
                        meanlist_abs_g = weightmeanFun(self.dataFrame2_)
                        self.dataFrame2_['RET'] = self.dataFrame2_['premium'].copy()
                        meanlist_g = weightmeanFun(self.dataFrame2_)
                        meanlist_group.append(meanlist_g)
                        meanlist_abs_group.append(meanlist_abs_g)
                    meanlist.append(meanlist_group)
                    meanlist_abs.append(meanlist_abs_group)

            meanDf = pd.DataFrame(meanlist)
            meanDf = meanDf.unstack()
            dfList.append(meanDf)
            meanDf_abs = pd.DataFrame(meanlist_abs)
            meanDf_abs = meanDf_abs.unstack()
            dfList_abs.append(meanDf_abs)
        self.meanDf = pd.DataFrame(dfList, index=self.tradingDateList[1:-1])
        self.meanDf_abs = pd.DataFrame(dfList_abs,index = self.tradingDateList[1:-1])
        return self.meanDf, self.meanDf_abs

    def portfolio_test(self, meanDf):
        sharp_list = []
        ret_list = []
        std_list = []
        mdd_list = []
        r2var_list = []
        cr2var_list = []
        anl = []
        compare= pd.DataFrame()
        for oneleg in tqdm(range(len(meanDf.columns))):
            portfolioDF = pd.DataFrame()
            portfolioDF['ret'] = meanDf.iloc[:,oneleg]
            portfolioDF['nav'] = (portfolioDF['ret']+1).cumprod()
            performance_df = performance(portfolioDF,para)
            performance_df_anl = performance_anl(portfolioDF,para)
            sharp_list.append(np.array(performance_df.iloc[:,0].T)[0])
            ret_list.append(np.array(performance_df.iloc[:,1].T)[0])
            std_list.append(np.array(performance_df.iloc[:,2].T)[0])
            mdd_list.append(np.array(performance_df.iloc[:,3].T)[0])
            r2var_list.append(np.array(performance_df.iloc[:,4].T)[0])
            cr2var_list.append(np.array(performance_df.iloc[:,5].T)[0])
            anl.append(np.array(performance_df_anl.iloc[:,0].T))
            compare[str(oneleg)] = portfolioDF['nav']
        performanceDf = pd.concat([pd.Series(sharp_list),
                                   pd.Series(ret_list),
                                   pd.Series(std_list),
                                   pd.Series(mdd_list),
                                   pd.Series(r2var_list),
                                   pd.Series(cr2var_list)],
                                    axis = 1, sort = True)
        performanceDf.columns = ['Sharp',
                                 'RetYearly',
                                 'STD',
                                 'MDD',
                                 'R2VaR',
                                 'R2CVaR']
        anlDf = pd.DataFrame(anl)
        print(anlDf)
        compare.index = self.meanDf.index
        plt.plot(range(len(compare.iloc[1:, 1])),
                 compare.iloc[1:, :])
        plt.title(self.factorI +'_'+self.factor2I)
        plt.xticks([0, 25, 50, 75, 100, 125],
                   ['2009/12/31', '2011/01/31', '2013/02/28', '2015/03/31', '2017/04/30', '2020/04/30'])
        plt.grid(True)
        plt.xlim((0, 125))
        plt.legend()
        plt.savefig(para.result_path + self.factorI +'_'+self.factor2I +'_'+para.weightMethod+
                '_'+para.normalize+'_performance_nav.png')
        plt.show()
        return performanceDf,compare

if __name__ == "__main__":
    factor_list = ['financial_asset', 'operating_asset', 'financial_liability',
    'net_ROE', 'net_operating_asset_net_profit', 'leverage_contrib',
    'net_profit_after_tax', 'net_operating_asset_turnover', 'operating_diff',
    'financail_leverage', 'g_sustainable', 'g_implicit',
    'ROE_DilutedQ'
    ]
    factor2_list = ['financial_asset', 'operating_asset', 'financial_liability',
    'net_ROE', 'net_operating_asset_net_profit', 'leverage_contrib',
    'net_profit_after_tax', 'net_operating_asset_turnover', 'operating_diff',
    'financail_leverage', 'g_sustainable', 'g_implicit'
    ]
    for factor_i in factor_list:
        for factor2_i in factor2_list:
            if factor_i == factor2_i: pass
            else:
                main_fun = main(factor_i,factor2_i)
                result, result_abs = main_fun.every_month()
                test, test_nav = main_fun.portfolio_test(result)
                test_abs, test_nav_abs = main_fun.portfolio_test(result_abs)
                print(test)
                print(test_abs)
                print(test_nav_abs)
    # In[]
                test_nav_abs.to_csv(para.result_path+'_' + factor_i +'_'+ factor2_i +'_'+ para.weightMethod+
                            '_'+para.normalize+'_test_nav_abs.csv')
                test.to_csv(para.result_path +'_'+ factor_i +'_'+factor2_i +'_' +para.weightMethod+
                            '_'+para.normalize+'_performance.csv')
                test_abs.to_csv(para.result_path +'_'+ factor_i +'_'+factor2_i +'_' + para.weightMethod+
                            '_'+para.normalize+'_performance_abs.csv')