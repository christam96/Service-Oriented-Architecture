
# import needed modules
import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import datetime as dt

# # Imports for VaR
# import pandas as pd
# # import seaborn as sns
# import matplotlib.pyplot as plt
# import numpy as np
# import yfinance as yf
# import datetime as dt

# # Display at most 10 rows
# pd.set_option('display.max_rows', 10)

# Imports for Flask API
from flask import Flask
from flask import request
from flask import Response

# Imports for Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

'''
Firebase Setup
'''
cred = credentials.Certificate(r'C:\Users\chris\Desktop\CS4471\SOA\cs4471-group5-firebase-adminsdk-cbxeo-921f4626c0.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

'''
Flask API Setup
'''
app = Flask(__name__)


ticker_list = []
quantity_list = []
user_id = ''

# def get_old_allocation(quantity_list, portolio_val):
def get_old_allocation(ticker_list, quantity_list):
    today = dt.date.today() - dt.timedelta(days=0)
    ticksString = ' '.join(str(x) for x in ticker_list)
    HistData = yf.download(ticksString, start =str(today), end =str(today))
    HistData = HistData['Adj Close'].T
    total_value = 0.0
    print('QLIST: ', quantity_list)
    for i in range(len(quantity_list)):
        total_value = total_value + (float(HistData.iat[i,0]) * float(quantity_list[i]))
    total_value = round(total_value,2)
    old_allocation = []
    for i in range(len(quantity_list)):
        temp = float(quantity_list[i]) * float(HistData.iat[i,0])
        temp = temp / total_value
        old_allocation.append(temp)
    print('OLD ALLOCATION: ', old_allocation)
    return old_allocation

def current_portfolio_value(ticker_list, quantity_list):
    today = dt.date.today() - dt.timedelta(days=0)
    ticksString = ' '.join(str(x) for x in ticker_list)
    HistData = yf.download(ticksString, start =str(today), end =str(today))
    HistData = HistData['Adj Close'].T
    value = 0.0
    for i in range(len(quantity_list)):
        value = value + (float(HistData.iat[i,0]) * float(quantity_list[i]))
    value = round(value,2)
    return value

def eff_frontier(ticker_list):
    yf.pdr_override()
    # selected = ['CNP', 'F', 'WMT', 'GE', 'TSLA']
    selected = ticker_list

    data = pdr.get_data_yahoo(selected, start="2000-01-01", end="2020-03-18")

    table = data['Adj Close']

    # calculate daily and annual returns of the stocks
    returns_daily = table.pct_change()
    returns_annual = returns_daily.mean() * 252
    selected = returns_annual.index.get_level_values(0).values

    # get daily and covariance of returns of the stock
    cov_daily = returns_daily.cov()
    cov_annual = cov_daily * 252

    # empty lists to store returns, volatility and weights of imiginary portfolios
    port_returns = []
    port_volatility = []
    sharpe_ratio = []
    stock_weights = []

    # set the number of combinations for imaginary portfolios
    num_assets = len(selected)
    num_portfolios = 50000

    #set random seed for reproduction's sake
    np.random.seed(101)

    # populate the empty lists with each portfolios returns,risk and weights
    for single_portfolio in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, returns_annual)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
        rf_rate = 0.02
        sharpe = (returns - rf_rate) / volatility
        sharpe_ratio.append(sharpe)
        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)

    # a dictionary for Returns and Risk values of each portfolio
    portfolio = {'Returns': port_returns,
                 'Volatility': port_volatility,
                 'Sharpe Ratio': sharpe_ratio}

    # extend original dictionary to accomodate each ticker and weight in the portfolio
    for counter,symbol in enumerate(selected):
        # portfolio[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]
        portfolio[symbol] = [Weight[counter] for Weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio)

    # get better labels for desired arrangement of columns
    column_order = ['Returns', 'Volatility', 'Sharpe Ratio'] + [stock for stock in selected]

    # reorder dataframe columns
    df = df[column_order]

    # find min Volatility & max sharpe values in the dataframe (df)
    max_sharpe = df['Sharpe Ratio'].max()

    # use the min, max values to locate and create the max sharpe portfolio
    sharpe_portfolio = df.loc[df['Sharpe Ratio'] == max_sharpe]

    # # plot frontier, max sharpe & min Volatility values with a scatterplot
    # df.plot.scatter(x='Volatility', y='Returns', c='Sharpe Ratio', cmap='RdYlGn', edgecolors='black', figsize=(10, 8), grid=True)
    # plt.scatter(x=sharpe_portfolio['Volatility'], y=sharpe_portfolio['Returns'], c='red', marker='D', s=200)
    # plt.xlabel('Volatility (Std. Deviation)')
    # plt.ylabel('Expected Returns')
    # plt.title('Efficient Frontier')
    # plt.show()

    # print the details of the max sharpe portfolio
    print('Sharpe: ', sharpe_portfolio.T)
    list_of_weights = []
    for i in range(len(ticker_list)):
        list_of_weights.append(sharpe_portfolio[str(ticker_list[i])].values)
        # list_of_weights.append(sharpe_portfolio.iat(i,1))
    print(list_of_weights)
    fb_weight = list_of_weights[0]
    zuo_weight = list_of_weights[1]
    print(fb_weight)
    print(zuo_weight)

    return list_of_weights

def create_new_allocation(list_of_weights, portfolio_value):
    print('Weights List: ', list_of_weights)
    print('Portfolio Value: ', portfolio_value)
    new_allocation = []
    for i in range(len(list_of_weights)):
        new_allocation.append(portfolio_value * list_of_weights[i])
    print(new_allocation)
    return new_allocation

@app.route('/users', methods = ['GET', 'POST'])
def user():
    if request.method == 'GET':
        """return the information for <user_id>"""
        return {
                "GET":"Request"
                }
    if request.method == 'POST':
        data = request.form # a multidict containing POST data

        user_id = request.args.get('uid') #if key doesn't exist, returns None
        ticker_list = request.args.get('tickers') #if key doesn't exist, returns None
        quantity_list = request.args.get('quantity') #if key doesn't exist, returns None
        print('User ID:', user_id)
        ticker_list = ticker_list.replace('[', '').replace(']', '').replace(' ', '').split(',')
        print('Ticker list', ticker_list)
        quantity_list = quantity_list.replace('[', '').replace(']', '').replace(' ', '').split(',')
        print('Quantity list', quantity_list)

        weights_list = eff_frontier(ticker_list)
        portolio_val = current_portfolio_value(ticker_list, quantity_list)
        new_allocation = create_new_allocation(weights_list, portolio_val)
        old_allocation = get_old_allocation(ticker_list, quantity_list)

        print('PRESENTING NEW PORTFOLIO ALLOCATION: ', new_allocation)
        difference = []
        for i in range(len(old_allocation)):
            if weights_list[i] > old_allocation[i]:
                difference.append(weights_list[i] - old_allocation[i])
            if old_allocation[i] > weights_list[i]:
                difference.append(old_allocation[i] - weights_list[i])
        print(difference)

        recommend_buy = []
        recommend_sell = []
        for i in range(len(difference)):
            if difference[i] > 0:
                recommend_buy.append(ticker_list[i])
            else:
                recommend_sell.append(ticker_list[i])

        print('RECOMMEND BUY: ', recommend_buy)
        print('RECOMMEND SELL: ', recommend_sell)

        temp_list = ['AAMZ', 'MSFT', 'TSLA', 'NFLX']
        # w2 = []
        # for i in range(len(weights_list)):
        #     num = 0
        #     for j in range(len(i)):
        #         num = j
        #     w2.append(num)

        test_str = ''
        for i in range(len(difference)):
            test_str += str(difference[i][0])

        # counter = 1
        # arr = []
        # num = 4
        # import random
        # while counter > 0 && counter2 < num:
        #     num = fandom.randint(0,counter)
        #     arr.append(num)
        #     counter = counter - 1
        #     counter2 = cou
        response = [0.25, 0.25, 0.25, 0.25]

        return {"price":test_str, "sell":recommend_sell, "buy":recommend_buy, "stocks":ticker_list, "uid":user_id}, 200

        # Write to Firebase
        doc_ref = db.collection(u'recommendations').document(user_id)
        doc_ref.set({
            u'sell': recommend_sell,
            u'buy': recommend_buy,
            u'exec': False,
            u'price': response,
            # u'stock': temp_list, # <<---
            # u'uid': user_id,
        })


if __name__ == "__main__":
    app.run(port=8000)
