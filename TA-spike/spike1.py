import ccxt
import ta
from ta.volatility import BollingerBands, AverageTrueRange
from ta.trend import SMAIndicator, EMAIndicator, MACD
import config
import pandas as pd
from signal import Signal
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

def enableBollingerBands(df):
    bb_indicator = BollingerBands(df['close'])
    df['upperband'] = bb_indicator.bollinger_hband()
    df['lowerband'] = bb_indicator.bollinger_lband()
    df['moving_average'] = bb_indicator.bollinger_mavg()
    return df

def enableATR(df):
    # Average true range
    atr_indicator  = AverageTrueRange(df['high'], df['low'], df['close'])
    df['atr'] = atr_indicator.average_true_range()
    return df

def enableEMA(df, period):
    # Exponential moving average
    ema = EMAIndicator(df['close'], window=period)
    df['100ema'] = ema.ema_indicator()
    return df

def enableMACD(df):
    # MACD
    macd = MACD(df['close'])
    df['macdSignal'] = macd.macd_signal()
    df['macdLine'] = macd.macd()
    return df


def produceSignals(df):
    signalsArray = []
    # BUY SIGNAL
    for i in range(100, len(df) - 1):
        #First data point lies above the 100 EMA
        if df['close'].iat[i] > df['100ema'].iat[i]:
            #Second data point lies above the 100 EMA
            if df['close'].iat[i + 1] > df['100ema'].iat[i + 1]:
                #First data point signal line > macd line
                if df['macdSignal'].iat[i] > df['macdLine'].iat[i]:
                    #Second data point signal line < macd Line
                    if df['macdSignal'].iat[i + 1] < df['macdLine'].iat[i + 1]:
                        newSignal = Signal(i, 0, df['close'].iat[i + 1], df['atr'].iat[i + 1], df)
                        print(newSignal.postSignal())
                        newSignal.determineIfSuccessful()
                        print(str(newSignal.getSuccessfulTrade()))
                        signalsArray.append(newSignal)

        # SELL SIGNAL
        #First data point lies below the 100 EMA
        if df['close'].iat[i] < df['100ema'].iat[i]:
            #Second data point lies below the 100 EMA
            if df['close'].iat[i + 1] < df['100ema'].iat[i + 1]:
                #First data point signal line < macd Line
                if df['macdSignal'].iat[i] < df['macdLine'].iat[i]:
                    #Second data point signal line > macd line
                    if df['macdSignal'].iat[i + 1] > df['macdLine'].iat[i + 1]:
                        newSignal = Signal(i, 1, df['close'].iat[i + 1], df['atr'].iat[i + 1], df)
                        print(newSignal.postSignal())
                        newSignal.determineIfSuccessful()
                        print(str(newSignal.getSuccessfulTrade()))
                        signalsArray.append(newSignal)
    return signalsArray


#print(df['open'].iat[149])

#df1 = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'atr', '100ema', 'macdSignal', 'macdLine']][100:101]
#df2 = df[['timestamp', 'open', 'high', 'low', 'close', 'volume', 'atr', '100ema', 'macdSignal', 'macdLine']][101:102]

#print(df1)
#print(df2)
#print(df.iat[100, 4] > df.iat[100, 7])
#checkSignal(df1, df2)


#Main code
df = requestData(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, 'BTC/USDT', '15m', 1000)
df = enableBollingerBands(df)
df = enableATR(df)
df = enableEMA(df, 100)
df = enableMACD(df)
signalsArray = produceSignals(df)

print("=========================================================")
print('RESULTS SUMMARY')
print("=========================================================")
print("Total data points analysed: " + str(len(df)))
print('Number of signals produced: ' + str(len(signalsArray)))
successfulTrades = 0
unsuccessfulTrades = 0
incompleteTrades = 0
percentageGain = 0
for signal in signalsArray:
    if signal.getSuccessfulTrade() == True:
        successfulTrades += 1
    elif signal.getSuccessfulTrade() == False:
        unsuccessfulTrades += 1
    else:
        incompleteTrades += 1
    
    percentageGain += signal.getProfit()

winRate = (successfulTrades / len(signalsArray)) * 100
print("Number of successful trades: " + str(successfulTrades))
print("Number of unsuccessful trades: " + str(unsuccessfulTrades))
print("Number of incomplete trades: " + str(incompleteTrades))
print("Percentage gain: " + str(percentageGain) + " %")
print("Win rate % = " + str(winRate))
