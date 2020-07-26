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
    data_path = '.\\data\\'
    result_path = '.\\result\\'
    pass
para = Para()
# In[]
total_asset = pd.read_csv(para.result_path + '总资产.csv',index_col=0)
total_asset.fillna(method = 'ffill',axis = 1, inplace=True)
total_asset.fillna(0,inplace = True)
trading_fin_asset = pd.read_csv(para.result_path + '交易性金融资产.csv',index_col=0)
trading_fin_asset.fillna(method = 'ffill',axis = 1,inplace=True)
trading_fin_asset.fillna(0,inplace = True)
sell_fin_asset = pd.read_csv(para.result_path + '可供出售金融资产.csv',index_col=0)
sell_fin_asset.fillna(method = 'ffill',axis = 1,inplace=True)
sell_fin_asset.fillna(0,inplace = True)
holding_bond = pd.read_csv(para.result_path + '持有到期投资.csv',index_col=0)
holding_bond.fillna(method = 'ffill',axis = 1,inplace=True)
holding_bond.fillna(0,inplace = True)
bond_invest = pd.read_csv(para.result_path + '债权投资.csv',index_col=0)
bond_invest.fillna(method = 'ffill',axis = 1,inplace=True)
bond_invest.fillna(0,inplace = True)
other_bond_invest = pd.read_csv(para.result_path + '其他债权投资.csv',index_col=0)
other_bond_invest.fillna(method = 'ffill',axis = 1,inplace=True)
other_bond_invest.fillna(0,inplace = True)
other_equity_invest = pd.read_csv(para.result_path + '其他权益工具投资.csv',index_col=0)
other_equity_invest.fillna(method = 'ffill',axis = 1,inplace=True)
other_equity_invest.fillna(0,inplace = True)
other_nonliq_invest = pd.read_csv(para.result_path + '其他非流动金融资产.csv',index_col=0)
other_nonliq_invest.fillna(method = 'ffill',axis = 1,inplace=True)
other_nonliq_invest.fillna(0,inplace = True)
fv_invest = pd.read_csv(para.result_path + '以公允价值价量且其变动计入其他综合收益的金融资产.csv',index_col=0)
fv_invest.fillna(method = 'ffill',axis = 1,inplace=True)
fv_invest.fillna(0,inplace = True)
financial_asset = np.array(trading_fin_asset) + np.array(sell_fin_asset)\
                                        + np.array(holding_bond)\
                                        + np.array(bond_invest)\
                                        + np.array(other_bond_invest)\
                                        + np.array(other_equity_invest)\
                                        + np.array(other_nonliq_invest)\
                                        + np.array(fv_invest)
financial_asset = pd.DataFrame(financial_asset,index = total_asset.index, columns=total_asset.columns)


operating_asset = np.array(total_asset) - np.array(financial_asset)
operating_asset = pd.DataFrame(operating_asset,index = total_asset.index, columns=total_asset.columns)
financial_asset.to_csv(para.result_path + 'financial_asset.csv')
operating_asset.to_csv(para.result_path + 'operating_asset.csv')

# In[]
total_liability = pd.read_csv(para.result_path + '总负债.csv',index_col=0)
total_liability.fillna(method = 'ffill',axis = 1,inplace=True)
total_liability.fillna(0,inplace = True)
short_debt = pd.read_csv(para.result_path + '短期借款.csv',index_col=0)
short_debt.fillna(method = 'ffill',axis = 1,inplace=True)
short_debt.fillna(0,inplace = True)
long_debt = pd.read_csv(para.result_path + '长期借款.csv',index_col=0)
long_debt.fillna(method = 'ffill',axis = 1,inplace=True)
long_debt.fillna(0,inplace = True)
one_y_nonliq = pd.read_csv(para.result_path + '一年内到期的非流动负债.csv',index_col=0)
one_y_nonliq.fillna(method = 'ffill',axis = 1,inplace=True)
one_y_nonliq.fillna(0,inplace = True)
payable_note = pd.read_csv(para.result_path + '应付票据.csv',index_col=0)
payable_note.fillna(method = 'ffill',axis = 1,inplace=True)
payable_note.fillna(0,inplace = True)
payable_interest = pd.read_csv(para.result_path + '应付利息.csv',index_col=0)
payable_interest.fillna(method = 'ffill',axis = 1,inplace=True)
payable_interest.fillna(0,inplace = True)
payable_bond = pd.read_csv(para.result_path + '应付债券.csv',index_col=0)
payable_bond.fillna(method = 'ffill',axis = 1,inplace=True)
payable_bond.fillna(0,inplace = True)
financial_liability = np.array(short_debt) \
                        + np.array(long_debt) \
                        + np.array(one_y_nonliq) \
                        + np.array(payable_note) \
                        + np.array(payable_interest) \
                        + np.array(payable_bond)
financial_liability = pd.DataFrame(financial_liability,index = total_liability.index, columns=total_liability.columns)
operating_liability = np.array(total_liability) - np.array(financial_liability)
operating_liability = pd.DataFrame(operating_liability,index = total_liability.index, columns=total_liability.columns)
financial_liability.to_csv(para.result_path + 'financial_liability.csv')
operating_liability.to_csv(para.result_path + 'operating_liability.csv')

# In[]
# 利息费用=利息支出-财务费用明细中的利息资本化金额-利息收入
interest_out = pd.read_csv(para.result_path + '财务费用-利息支出.csv',index_col=0)
interest_out.fillna(method = 'ffill',axis = 1,inplace=True)
interest_out.fillna(0,inplace = True)
interest_cap = pd.read_csv(para.result_path + '财务费用-利息资本化.csv',index_col=0)
interest_cap.fillna(method = 'ffill',axis = 1,inplace=True)
interest_cap.fillna(0,inplace = True)
interest_in = pd.read_csv(para.result_path + '财务费用-利息收入.csv',index_col=0)
interest_in.fillna(method = 'ffill',axis = 1,inplace=True)
interest_in.fillna(0,inplace = True)
financial_loss = np.array(interest_out) - np.array(interest_cap) - np.array(interest_in)
financial_loss = pd.DataFrame(financial_loss,index = total_liability.index, columns=total_liability.columns)
interest = pd.read_csv(para.result_path + '财务费用.csv',index_col=0)
financial_loss[financial_loss == np.nan] = interest
financial_loss.to_csv(para.result_path + 'financial_loss.csv')

