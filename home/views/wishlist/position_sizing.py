import math
import numpy as np
from django.shortcuts import render
from django.utils import timezone
from apps.common.models import *
import business.logic as Logic
from django.shortcuts import get_object_or_404
import pandas as pd
from pandas import DataFrame
from django.http import JsonResponse


def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    # Step 1. Get
    # Step 1.a. Get static_settings
    # Fetch the user static setting by userid
    user_static_setting = get_object_or_404(UserStaticSetting, user_id=user_id)
    # Retrieve the risk level
    risk = user_static_setting.risk
    min_position = user_static_setting.position_min
    max_position = user_static_setting.position_max

    # Step 1.b. Get Portfolio Size
    cash = portfolio.cash
    money_market = portfolio.money_market
    investment = portfolio.investment
    margin_loan = portfolio.margin_loan
    total = cash + money_market + investment

    # Wishlist.objects.filter(pick_at=request.user).first()
    # Step 1.c. Get Wishlist
    # here_need_help = Wishlist.objects.filter(pick_at=request.user).first()
    symbols = ['OWL','CALM','YPF','FOUR','DAVE']
    # symbols = [ 'DAVE', ]
    timeframe = '1D'
    # Attach symbol name from MarketSymbol model
    final_df = pd.DataFrame(
        MarketSymbol.objects.filter(symbol__in=symbols).values('symbol', 'name'))
    # put dummy column for now
    final_df['pick_at'] =  timezone.now().date()
    final_df["purpose"] = WishlistPurposeChoices.SEPA
    final_df["add_by"] = get_object_or_404(User, id=user_id).username


    # Step 1. d. Get Industry
    industry_df = pd.DataFrame(list(MarketStock.objects.filter(
        symbol__in=final_df['symbol'].tolist()
    ).values('symbol', 'exchange', 'industry', 'sector')))

    # Step 1.d. Get Data
    all_hist_df = getHistoricalData(symbols, timeframe)
    # Calculate Current Price
    current_price_df = pd.DataFrame(getCurrentPrice(symbols, all_hist_df))
    # Calculate Bollinger Bands
    indicator_df = pd.DataFrame(getBollinger(symbols, all_hist_df, window=20))
    # Calculate ATR
    atr_df = pd.DataFrame(getATR(symbols, all_hist_df, period=14))
    # Calculate Support and Resistance
    sr_df = pd.DataFrame(getSupportResistance(symbols, all_hist_df))

    # Merge the DataFrames
    final_df = pd.merge(final_df, industry_df, on='symbol')
    final_df = pd.merge(final_df, current_price_df, on='symbol')
    final_df = pd.merge(final_df, indicator_df, on='symbol')
    final_df = pd.merge(final_df, atr_df, on='symbol')
    final_df = pd.merge(final_df, sr_df, on='symbol')


    # #########################

    # Step 2. Calculate Positions
    # Step 2.a. calculate Position Size for each symbol
    def ideal_position_size():
        return total / (min_position + max_position)/2
    def default_risk():
        return float(total * (risk / 100))
    def default_risk_pct():
        return float(total * (risk / 100) / total) * 100

    # Step 2.b. calculate the risk
    final_df['risk'] = final_df.apply(lambda row: default_risk() , axis=1)
    final_df['risk_pct'] = final_df.apply(lambda row: default_risk_pct(), axis=1)

    # step 2.c. calculate the open position
    # use lower band as buy price ( consider add some buffer from true range
    # for possible open positions
    final_df['open_stop'] = final_df['lower_band'] + final_df['ATR'] * 0.02
    final_df['open_limit'] = final_df['open_stop']  - final_df['current_price'] * 0.005

    # step 2.d. calculate the stop limit
    final_df['open_rs_distance_1'] = abs(final_df['open_stop'] - final_df['rs_lower_1'])
    final_df['open_rs_distance_2'] = abs(final_df['open_stop'] - final_df['rs_lower_2'])

    def calculate_stop_limit(row):
        distance_1 = abs(row['open_stop'] - row['rs_lower_1'])
        distance_2 = abs(row['open_stop'] - row['rs_lower_2'])
        atr_threshold = 2 * row['ATR']

        if distance_1 > atr_threshold and distance_2 > atr_threshold:
            return min(distance_1, distance_2)
        elif distance_1 > atr_threshold:
            return distance_1
        elif distance_2 > atr_threshold:
            return distance_2
        else:
            return atr_threshold  # or some default value if neither condition is met

    final_df['close_stop'] = final_df.apply(
        lambda row: row['open_stop'] - calculate_stop_limit(row), axis=1)
    final_df['close_limit'] =  final_df['close_stop'] - final_df['current_price'] * 0.005

    # step 2.e. calculate the # Shares base on risk
    def calculate_shares(row):
        return math.floor(float(row['risk']) / (row['open_stop'] - row['close_stop']))
    final_df['num_shares'] = final_df.apply(calculate_shares, axis=1)

    # step 2.f. calculate the $ & % CAPITAL NEED
    final_df['capital_need'] = final_df['num_shares'] * final_df['open_stop']
    final_df['capital_need_pct'] = final_df['capital_need'] / float(total) * 100

    # step 2.g. calculate # Size Need
    size = float(total) / ((min_position + max_position) / 2)
    final_df['size_weight'] = final_df['capital_need'] / size

    # #########################
    # Risk Model
    # Step 3.a Calculate Gain Bollinger Band
    final_df['gain_upper_1'] = (final_df['upper_band'] - final_df['current_price']) * final_df['num_shares']
    final_df['gain_upper_2'] = (final_df['upper_band_2'] - final_df['current_price']) * final_df['num_shares']
    final_df['gain_upper_3'] = (final_df['upper_band_3'] - final_df['current_price']) * final_df['num_shares']

    # Step 3.b Calculate Ratio
    final_df['risk_ratio_1'] = final_df['gain_upper_1'] / final_df['risk'] * 100
    final_df['risk_ratio_2'] = final_df['gain_upper_2'] / final_df['risk'] * 100
    final_df['risk_ratio_3'] = final_df['gain_upper_3'] / final_df['risk'] * 100

    return render(
        request=request,
        template_name='pages/wishlist/position_sizing.html',
        context= {
            'parent': 'wishlist',
            'segment': 'position_sizing',
            'watchlist_items': final_df.to_dict(orient='records'),
        })


def getHistoricalData(symbols, timeframe='1D'):
    # Fetch historical data for the symbol and timeframe
    data = Logic.research().treading().get_stock_full_hist_bars(True, symbols)

    # Convert the fetched rows into a DataFrame
    df = pd.DataFrame(data, columns=['symbol', 'date', 'close', 'high','low', 'volume'])

    return df

def getCurrentPrice(symbols,  df: DataFrame):
    results = []

    for symbol in symbols:
        data = df[df['symbol'] == symbol]
        latest_data = data.loc[data['date'].idxmax()]  # Get the row with the latest date

        results.append({
            'symbol': symbol,
            'current_price': latest_data['close']
        })

    return results

def getBollinger(symbols:list, df: DataFrame, window=20):
    results = []

    for symbol in symbols:
        data = df[df['symbol'] == symbol]

        # Ensure the data is sorted by date
        data = data.sort_values(by='date')

        # Calculate the moving average and standard deviation
        data['MA'] = data['close'].rolling(window=window).mean()
        data['STD'] = data['close'].rolling(window=window).std()

        # Calculate the Bollinger Bands
        data['Upper'] = data['MA'] + (data['STD'] * 2)
        data['Lower'] = data['MA'] - (data['STD'] * 2)

        # Calculate the Bollinger Bands
        data['Upper1'] = data['MA'] + (data['STD'] * 3)
        data['Lower1'] = data['MA'] - (data['STD'] * 3)
        data['Upper2'] = data['MA'] + (data['STD'] * 4)
        data['Lower2'] = data['MA'] - (data['STD'] * 4)

        # Get the latest Bollinger Bands values
        latest_data = data.iloc[-1]

        results.append({
            'symbol': symbol,
            'upper_band': latest_data['Upper'],
            'lower_band': latest_data['Lower'],

            'upper_band_2': latest_data['Upper1'],
            'lower_band_2': latest_data['Lower1'],
            'upper_band_3': latest_data['Upper2'],
            'lower_band_3': latest_data['Lower2'],

            'moving_average': latest_data['MA']
        })

    return results

def getATR(symbols:list, df: DataFrame, period=14):
    results = []

    for symbol in symbols:
        data = df[df['symbol'] == symbol]

        # Ensure the data is sorted by date
        data = data.sort_values(by='date')

        # Calculate True Range (TR)
        data['H-L'] = data['high'] - data['low']
        data['H-PC'] = abs(data['high'] - data['close'].shift(1))
        data['L-PC'] = abs(data['low'] - data['close'].shift(1))
        data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)

        # Calculate ATR
        data['ATR'] = data['TR'].rolling(window=period).mean()

        # Get the latest ATR value
        latest_data = data.iloc[-1]

        results.append({
            'symbol': symbol,
            'ATR': latest_data['ATR']
        })

    # Return the data with ATR values
    return results

def getSupportResistance(symbols:list, df: DataFrame):
    results = []

    for symbol in symbols:
        data = df[df['symbol'] == symbol]

        # Ensure the data is sorted by date
        data = data.sort_values(by='date')

        # Calculate support and resistance levels
        supports = []
        resistances = []
        for i in range(2, len(data) - 2):
            if data['close'].iloc[i] < data['close'].iloc[i - 1] and data['close'].iloc[i] < data['close'].iloc[i + 1] and \
               data['close'].iloc[i + 1] < data['close'].iloc[i + 2] and data['close'].iloc[i - 1] < data['close'].iloc[i - 2]:
                supports.append(data['close'].iloc[i])
            if data['close'].iloc[i] > data['close'].iloc[i - 1] and data['close'].iloc[i] > data['close'].iloc[i + 1] and \
               data['close'].iloc[i + 1] > data['close'].iloc[i + 2] and data['close'].iloc[i - 1] > data['close'].iloc[i - 2]:
                resistances.append(data['close'].iloc[i])

        # Group and sort supports and resistances
        supports = sorted(supports, reverse=True)[:3]
        resistances = sorted(resistances, reverse=True)[:3]

        # Prepare the result
        results.append({
            'symbol': symbol,
            'rs_upper_1': resistances[0] if len(resistances) > 0 else np.nan,
            'rs_lower_1': supports[0] if len(supports) > 0 else np.nan,
            'rs_upper_2': resistances[1] if len(resistances) > 1 else np.nan,
            'rs_lower_2': supports[1] if len(supports) > 1 else np.nan
        })

    return results

