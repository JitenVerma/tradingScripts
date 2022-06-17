import ccxt
import ta
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend import IchimokuIndicator
import config
import pandas as pd
import yfinance as yf


def requestData(apiKey, secretKey, ticker, timeFrame, candleLimit):

    exchange = ccxt.binance({
        'apiKey': apiKey,
        'secret': secretKey
    })

    markets = exchange.load_markets()

    #15 minute time frame, 96 data points (1 day)
    bars = exchange.fetch_ohlcv(ticker, timeframe=timeFrame, limit=candleLimit)
    return pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])


def enableIchimokuClouds(df):
    ichimokuData = IchimokuIndicator(df['high'], df['low'], 9, 26, 52)
    df['leadOne'] = ichimokuData.ichimoku_a()
    df['leadTwo'] = ichimokuData.ichimoku_b()
    return df

def produceSignals(df):
    signals = []
    i = 60
    numberOfDp = len(df)
    while i < numberOfDp:
        # Check if leadOne line is above lead2 line
        if df['leadOne'].iat[i] > df['leadTwo'].iat[i]:
            # Check if candle closes above leadOne
            if df['close'].iat[i] > df['leadOne'].iat[i]:
                tradeSummary = enterTrade(df, i)
                i = tradeSummary['i']
                print(tradeSummary)
                signals.append(tradeSummary)

        i += 1
    
    return signals

def enterTrade(df, i):
    entryPrice = df['close'].iat[i]
    startingPeriod = i
    numberOfDp = len(df)

    while i < numberOfDp:
        # Check if candle closes below leadOne
        if df['close'].iat[i] < df['leadOne'].iat[i]:
            profit = ((df['close'].iat[i] - entryPrice) / entryPrice) * 100
            tradingPeriod = i - startingPeriod
            successfulTrade = None
            if profit > 0:
                successfulTrade = True
            else:
                successfulTrade = False


            tradeSummary = {
                'startingPeriod': startingPeriod,
                'entryPrice': entryPrice,
                'tradingPeriod': tradingPeriod,
                'profit': profit,
                'successfulTrade': successfulTrade,
                'i': i
            }

            return tradeSummary
        
        i += 1
    
    # If signal has not yet closed
    profit = 0
    tradingPeriod = i - startingPeriod
    successfulTrade = None

    tradeSummary = {
        'startingPeriod': startingPeriod,
        'entryPrice': entryPrice,
        'tradingPeriod': tradingPeriod,
        'profit': profit,
        'successfulTrade': successfulTrade,
        'i': i
    }

    return tradeSummary

def calculateStats(signals):
    successfulTrades = 0
    unsuccessfulTrades = 0
    incompleteTrades = 0
    percentageGain = 0
    biggestWinStreak = 0
    winStreak = 0
    biggestLossStreak = 0
    lossStreak = 0
    profits = []
    for signal in signals:
        if signal['successfulTrade'] == True:
            successfulTrades += 1
            winStreak += 1
            lossStreak = 0
            if winStreak > biggestWinStreak:
                biggestWinStreak = winStreak

        elif signal['successfulTrade'] == False:
            unsuccessfulTrades += 1
            lossStreak += 1
            winStreak = 0
            if lossStreak > biggestLossStreak:
                biggestLossStreak = lossStreak
        else:
            incompleteTrades += 1
        
        percentageGain += signal['profit']
        profits.append(signal['profit'])
    
    winRate = (successfulTrades / len(signals)) * 100
    print("Number of successful trades: " + str(successfulTrades))
    print("Number of unsuccessful trades: " + str(unsuccessfulTrades))
    print("Number of incomplete trades: " + str(incompleteTrades))
    print("Percentage gain: " + str(percentageGain) + " %")
    print("Win rate % = " + str(winRate))
    print("Highest win streak: " + str(biggestWinStreak))
    print("Highest loss streak: " + str(biggestLossStreak))
    print("Biggest gain: " + str(max(profits)))
    print("Biggest loss: " + str(min(profits)))

#Main code
def mainCryptoCode():
    df = requestData(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, 'ETH/USDT', '4h', 1000)
    df = enableIchimokuClouds(df)
    signals = produceSignals(df)


    print("=========================================================")
    print('RESULTS SUMMARY')
    print("=========================================================")
    calculateStats(signals)


#mainCode()

df = yf.download(tickers = "AUDUSD=X", period='60d', interval='15m')
print(df)
#df = enableIchimokuClouds(df)
#signals = produceSignals(df)


print("=========================================================")
print('RESULTS SUMMARY')
print("=========================================================")
#calculateStats(signals)
#print(msft.history())