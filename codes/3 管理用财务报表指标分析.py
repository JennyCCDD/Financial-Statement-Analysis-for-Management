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
# 净金融负债 = 金融负债 − 金融资产
financial_liability = pd.read_csv(para.result_path + 'financial_liability.csv',index_col=0)
financial_asset = pd.read_csv(para.result_path + 'financial_asset.csv',index_col=0)
net_financial_liability = np.array(financial_liability) - np.array(financial_asset)
net_financial_liability = pd.DataFrame(net_financial_liability,
                                       index = financial_liability.index,
                                       columns = financial_liability.columns)
# In[]
# 税后利息率 = 税后利息费用 ÷ 净金融负债
financial_loss = pd.read_csv(para.result_path + 'financial_loss.csv',index_col=0)
interest_rate_after_tax = np.array(financial_loss) / (np.array(net_financial_liability) + 0.000000001)
interest_rate_after_tax = pd.DataFrame(interest_rate_after_tax,
                                       index = financial_loss.index,
                                       columns = financial_loss.columns)
interest_rate_after_tax.to_csv(para.result_path + 'interest_rate_after_tax.csv')
# In[]
# 净经营资产 = 经营资产 − 经营负债 = 净金融负债 + 股东权益
operating_asset = pd.read_csv(para.result_path + 'operating_asset.csv',index_col=0)
operating_liability = pd.read_csv(para.result_path + 'operating_liability.csv',index_col=0)
net_operating_asset = np.array(operating_asset) - np.array(operating_liability)
net_operating_asset = pd.DataFrame(net_operating_asset,
                                       index = operating_asset.index,
                                       columns = operating_asset.columns)

# In[]
# 所得税率 = 所得税费用/利润总额
tax_expenditure = pd.read_csv(para.result_path + '所得税额.csv',index_col=0)
tax_expenditure.fillna(method = 'ffill',axis = 0,inplace=True)
profit_all = pd.read_csv(para.result_path + '利润总额.csv',index_col=0)
profit_all.fillna(method = 'ffill',axis = 0,inplace=True)
tax_rate = np.array(tax_expenditure) / np.array(profit_all)
tax_rate = pd.DataFrame(tax_rate,
                        index=profit_all.index,
                        columns=profit_all.columns)

# In[]
# 税后经营净利润 = 息税前利润 × （1 − 所得税率）
EBIT = pd.read_csv(para.result_path + '息税前收益.csv',index_col=0)
EBIT.fillna(method = 'ffill',axis = 0,inplace=True)
EBI = np.array(EBIT) * (1 - np.array(tax_rate))
EBI = pd.DataFrame(EBI,
                   index=EBIT.index,
                   columns=EBIT.columns)

# In[]
# 净财务杠杆 = 净金融负债 ÷ 股东权益
equity = pd.read_csv(para.result_path + '股东权益.csv',index_col=0)
equity.fillna(method = 'ffill',axis = 0,inplace=True)
financail_leverage = np.array(net_financial_liability) / np.array(equity)
financail_leverage = pd.DataFrame(financail_leverage,
                                   index=equity.index,
                                   columns=equity.columns)

# In[]
# 经营差异率 = 净经营资产净利率 − 税后利息率
operating_diff = np.array(financail_leverage) - np.array(interest_rate_after_tax)
operating_diff = pd.DataFrame(operating_diff,
                                   index=financail_leverage.index,
                                   columns=financail_leverage.columns)

# In[]
# 净经营资产周转次数 = 销售收入 ÷ 净经营资产
sales = pd.read_csv(para.result_path + '营业总收入.csv',index_col=0)
sales.fillna(method = 'ffill',axis = 0,inplace=True)
net_operating_asset_turnover = np.array(sales) / np.array(net_operating_asset)
net_operating_asset_turnover = pd.DataFrame(net_operating_asset_turnover,
                                               index=sales.index,
                                               columns=sales.columns)

# In[]
# 税后经营净利率 = 税后经营净利润 ÷ 销售收入
net_profit_after_tax = np.array(EBI) / np.array(sales)
net_profit_after_tax = pd.DataFrame(net_profit_after_tax,
                                   index=EBI.index,
                                   columns=EBI.columns)

# In[]
# 杠杆贡献率 = 经营差异率 × 净财务杠杆
leverage_contrib = np.array(operating_diff) * np.array(financail_leverage)
leverage_contrib = pd.DataFrame(leverage_contrib,
                                   index=operating_diff.index,
                                   columns=operating_diff.columns)

# In[]
# 净经营资产净利率 = 税后经营净利率 × 净经营资产周转次数
net_operating_asset_net_profit = np.array(net_profit_after_tax) * np.array(net_operating_asset_turnover)
net_operating_asset_net_profit = pd.DataFrame(net_operating_asset_net_profit,
                                   index=net_profit_after_tax.index,
                                   columns=net_profit_after_tax.columns)

# In[]
# 净资产收益率 = （税后经营净利润 − 税后利息费用） ÷ 股东权益
# = 净经营资产净利率 + 杠杆贡献率
net_ROE = np.array(net_operating_asset_net_profit) + np.array(leverage_contrib)
net_ROE[np.isinf(net_ROE)] = 0
net_ROE = pd.DataFrame(net_ROE,
                       index=net_operating_asset_net_profit.index,
                       columns=net_operating_asset_net_profit.columns)

# In[]
# 净资产收益率 = 净经营资产净利率 + 杠杆贡献率
net_ROE.to_csv(para.result_path + 'net_ROE.csv')
net_operating_asset_net_profit.to_csv(para.result_path + 'net_operating_asset_net_profit.csv')
leverage_contrib.to_csv(para.result_path + 'leverage_contrib.csv')

# 净经营资产净利率 = 税后经营净利率 × 净经营资产周转次数
net_profit_after_tax.to_csv(para.result_path + 'net_profit_after_tax.csv')
net_operating_asset_turnover.to_csv(para.result_path + 'net_operating_asset_turnover.csv')

# 杠杆贡献率 = 经营差异率 × 净财务杠杆
operating_diff.to_csv(para.result_path + 'operating_diff.csv')
financail_leverage.to_csv(para.result_path + 'financail_leverage.csv')
