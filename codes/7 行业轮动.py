# -*- coding: utf-8 -*-
__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20200703"
'''
revised: 20200723 新增行业分布统计；去除银行和非银金融
         20200724 新增绝对收益和超额收益
                  行业轮动策略选择市值中性化或者不处理
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
    weightMethod = '简单加权' # 简单加权 市值加权
    ret_calMethod = '简单' # 对数
    groupnum = 5
    normalize = 'None' # None Size Size_and_Industry
    factor = 'interest_rate_after_tax'
    direction = -1
    # [financial_asset, operating_asset, financial_liability,
    # net_ROE, net_operating_asset_net_profit, leverage_contrib,
    # net_profit_after_tax, net_operaitng_asset_turnover, operating_diff,
    # financail_leverage, g_sustainable, g_implicit
    # ]
    sample = 'out_of_sample' #in_sample  out_of_sample
    data_path = '.\\data\\'
    result_path = '.\\result\\'
    listnum = 121 # for stock sample at least be listed for listnum of days
    backtestwindow = 60 # number of days used to form portfolios
    fin_stock = 'no' # include finnacial stock or not
    dataPathPrefix = 'D:\caitong_security'
    pass
para = Para()



class Industry():
    def __init__(self,para):
        # get trading date list as monthly frequancy
        self.tradingDateList = getTradingDateFromJY(para.startDate,
                                                    para.endDate,
                                                    ifTrade=True,
                                                    Period='M')

        self.Price, self.LimitStatus, self.Status, self.listDateNum, self.Industry, self.Size = basic_data(para)

        if para.factor == 'ROE_DilutedQ':
            DATA = loadData(para.factor)
            Factor = DATA.BasicDailyFactorAlpha.loc[para.startDate:para.endDate, :]
            self.Factor = stock_dif(Factor, self.LimitStatus)
        else:
            Factor = pd.read_csv(para.result_path + para.factor + '.csv', index_col=0).T
            self.Factor = stock_dif(Factor, self.LimitStatus)
            self.Factor[self.Factor == np.nan] = 0
        self.df = pd.read_csv(para.data_path + 'mean_industry_index.csv', index_col=0)
        pass

    def DES(self):
        Des = pd.DataFrame(self.Factor.describe())
        Des['all'] = Des.apply(lambda x: x.sum(), axis = 1)
        return Des['all']

    def every_month(self):
        # deal with the data every month
        meanlist = []
        meanlist_abs = []
        self.corr_list = []
        for i,currentDate in enumerate(tqdm(self.tradingDateList[:-2])):
            lastDate = self.tradingDateList[self.tradingDateList.index(currentDate) - 1]
            nextDate = self.tradingDateList[self.tradingDateList.index(currentDate) + 1]
            if para.sample == 'in_sample':
                # use different method to calculate the return
                # logreturn for short time period and simple return calculation for long time period
                if para.ret_calMethod == '对数':
                    self.ret = np.log(self.Price.loc[currentDate, :] / self.Price.loc[lastDate, :])
                elif para.ret_calMethod == '简单':
                    self.ret = self.Price.loc[currentDate, :] / self.Price.loc[lastDate, :] - 1
                self.benchmark = pd.Series([self.df.iloc[i , 0]] * len(self.Factor.columns),
                                           index=self.ret.index.copy())

            elif para.sample == 'out_of_sample':
                if para.ret_calMethod == '对数':
                    self.ret = np.log(self.Price.loc[nextDate, :] / self.Price.loc[currentDate, :])
                elif para.ret_calMethod == '简单':
                    self.ret = self.Price.loc[nextDate, :] / self.Price.loc[currentDate, :] - 1

                self.benchmark = pd.Series([self.df.iloc[i + 1,0]] * len(self.Factor.columns),index = self.ret.index.copy())

            self.dataFrame = pd.concat([
                                       # self.Factor.iloc[i,:],
                                       self.Factor.loc[str(currentDate),:],
                                       self.ret,
                                       self.benchmark,
                                       self.LimitStatus.loc[currentDate,:],
                                       self.Status.loc[currentDate,:],
                                       self.listDateNum.loc[currentDate,:],
                                       self.Industry.loc[currentDate,:],
                                       self.Size.loc[currentDate,:]],
                                       axis=1, sort=True)
            self.dataFrame = self.dataFrame.reset_index()
            self.dataFrame.columns = ['stockid',
                                         'factor',
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
            # self.dataFrame = self.dataFrame.dropna()
            # dataFrame = dataFrame.loc[dataFrame['factor'] != 0]
            self.dataFrame = self.dataFrame.loc[self.dataFrame['LimitStatus'] == 0]# 提取非涨跌停的正常交易的数据
            self.dataFrame = self.dataFrame.loc[self.dataFrame['Status'] == 1]# 提取非ST/ST*/退市的正常交易的数据
            self.dataFrame = self.dataFrame.loc[self.dataFrame['listDateNum'] >= para.listnum]# 提取上市天数超过listnum的股票
            if para.fin_stock == 'no': # 非银行金融代号41,银行40
                self.dataFrame = self.dataFrame.loc[self.dataFrame['Industry'] != 41]
                self.dataFrame = self.dataFrame.loc[self.dataFrame['Industry'] != 40]

            self.dataFrame['premium'] = self.dataFrame['RET'] - self.dataFrame['Bechmark']

            # 计算spearman秩相关系数
            corr, t = spearmanr(
                self.dataFrame.loc[:, 'factor'],
                self.dataFrame.loc[:, 'RET'])
            self.corr_list.append(corr)

            # 按行业平均该因子值，用于输出dataframe画图
            self.industry_factor =self.dataFrame.groupby(by='Industry', as_index=False)['factor'].mean()

            self.industry_factor.sort_values(by = 'factor', ascending = False, inplace= True) # 降序排列
            self.industry_list = self.industry_factor.Industry

            self.long_industry_list = list(self.industry_factor.Industry[:int(len(self.industry_list)/para.groupnum)])
            self.short_industry_list = list(self.industry_factor.Industry[-int(len(self.industry_list)/para.groupnum):])
            self.mean_dict_long = {}
            self.mean_dict_short ={}
            self.mean_dict_long_abs = {}
            self.mean_dict_short_abs = {}
            for ll in range(len(self.long_industry_list)):
                self.mean_dict_long[ll] = self.dataFrame.loc[
                    self.dataFrame['Industry']==self.long_industry_list[ll]]['premium'].mean()
                self.mean_dict_long_abs[ll] = self.dataFrame.loc[
                    self.dataFrame['Industry'] == self.long_industry_list[ll]]['RET'].mean()

            for zz in range(len(self.short_industry_list)):
                self.mean_dict_short[zz] = self.dataFrame.loc[
                    self.dataFrame['Industry']==self.short_industry_list[zz]]['premium'].mean()
                self.mean_dict_short_abs[zz] = self.dataFrame.loc[
                    self.dataFrame['Industry'] == self.short_industry_list[zz]]['RET'].mean()

            if para.weightMethod == '简单加权':
                meanlist.append([np.array(self.mean_dict_long[0]- self.mean_dict_short[4])*para.direction,
                                np.array(self.mean_dict_long[0]),
                                np.array(self.mean_dict_long[4])])
                meanlist_abs.append([np.array(self.mean_dict_long_abs[0]- self.mean_dict_short_abs[4])*para.direction,
                                        np.array(self.mean_dict_long_abs[0]),
                                        np.array(self.mean_dict_long_abs[4])])
            elif para.weightMethod == '市值加权':pass

        self.meanDf = pd.DataFrame(meanlist,index = self.tradingDateList[1:-1])
        self.meanDf_abs = pd.DataFrame(meanlist_abs,index = self.tradingDateList[1:-1])
        self.corr_avg = np.mean(self.corr_list)
        print('RankIC', round(self.corr_avg, 6))
        return self.industry_factor, self.meanDf, self.meanDf_abs, self.corr_list

    def portfolio_test(self, meanDf):
        sharp_list = []
        ret_list = []
        std_list = []
        mdd_list = []
        r2var_list = []
        cr2var_list = []
        anl = []
        compare = pd.DataFrame()
        for oneleg in tqdm(range(len(meanDf.columns))):
            portfolioDF = pd.DataFrame()
            portfolioDF['ret'] = meanDf.iloc[:, oneleg]
            portfolioDF['nav'] = (portfolioDF['ret'] + 1).cumprod()
            performance_df = performance(portfolioDF, para)
            performance_df_anl = performance_anl(portfolioDF, para)
            sharp_list.append(np.array(performance_df.iloc[:, 0].T)[0])
            ret_list.append(np.array(performance_df.iloc[:, 1].T)[0])
            std_list.append(np.array(performance_df.iloc[:, 2].T)[0])
            mdd_list.append(np.array(performance_df.iloc[:, 3].T)[0])
            r2var_list.append(np.array(performance_df.iloc[:, 4].T)[0])
            cr2var_list.append(np.array(performance_df.iloc[:, 5].T)[0])
            anl.append(np.array(performance_df_anl.iloc[:, 0].T))
            compare[str(oneleg)] = portfolioDF['nav']
        performanceDf = pd.concat([pd.Series(sharp_list),
                                   pd.Series(ret_list),
                                   pd.Series(std_list),
                                   pd.Series(mdd_list),
                                   pd.Series(r2var_list),
                                   pd.Series(cr2var_list)],
                                  axis=1, sort=True)
        performanceDf.columns = ['Sharp',
                                 'RetYearly',
                                 'STD',
                                 'MDD',
                                 'R2VaR',
                                 'R2CVaR']
        anlDf = pd.DataFrame(anl)
        print(anlDf)
        compare.index = meanDf.index
        plt.plot(range(len(compare.iloc[1:, 1])),
                 compare.iloc[1:, :])
        plt.title(para.factor)
        plt.xticks([0, 25, 50, 75, 100, 125],
                   ['2009/12/31', '2011/01/31', '2013/02/28', '2015/03/31', '2017/04/30', '2020/04/30'])
        plt.grid(True)
        plt.xlim((0, 125))
        plt.legend()
        # plt.savefig(para.result_path + para.factor + '_' + para.weightMethod +
        #             '_' + para.normalize + '_performance_nav.png')
        plt.show()
        return performanceDf, compare

if __name__ == "__main__":
    main_fun = Industry(para)
    in_factor, result, result_abs, corrList = main_fun.every_month()
    test, test_nav = main_fun.portfolio_test(result)
    test_abs, test_nav_abs = main_fun.portfolio_test(result_abs)
    print(test_nav_abs)
    print(test)
    print(test_abs)

    # In[]
    in_factor.to_csv(para.result_path + '_' + para.factor + '_' + para.weightMethod +
                     '_' + para.normalize + '_des.csv')
    test_nav_abs.to_csv(para.result_path + '_' + para.factor + '_' + para.weightMethod +
                        '_' + para.normalize + '_test_nav_abs.csv')
    test.to_csv(para.result_path + '_' + para.factor + '_' + para.weightMethod +
                '_' + para.normalize + '_performance.csv')
    test_abs.to_csv(para.result_path + '_' + para.factor + '_' + para.weightMethod +
                    '_' + para.normalize + '_performance_abs.csv')
    pd.DataFrame(corrList).to_csv(para.result_path + '_' + para.factor + '_' + para.weightMethod +
                                  '_' + para.normalize + '_corr.csv')

#