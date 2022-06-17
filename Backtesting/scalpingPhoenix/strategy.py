import ccxt
import ta
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import AwesomeOscillatorIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD
import pandas as pd
import yfinance as yf

def requestData(ticker, period, interval):
    """
    Common tickers: 
    - EURUSD=X
    - GBPUSD=X
    - AUDUSD=X
    - NZDUSD=X
    - JPYUSD=X
    """
    return yf.download(tickers=ticker, period=period, interval=interval)

def enableEMA(df, period):
    # Exponential moving average
    ema = EMAIndicator(df['close'], window=period)
    df['3ema'] = ema.ema_indicator()
    return df

def enableBollingerBands(df):
    bb_indicator = BollingerBands(df['close'], 20, 2)
    df['upperband'] = bb_indicator.bollinger_hband()
    df['lowerband'] = bb_indicator.bollinger_lband()
    df['medianBand'] = bb_indicator.bollinger_mavg()
    return df

def enableAwesomeIndicator(df):
    AO_indicator = AwesomeOscillatorIndicator(df['high'], df['low'], 5, 34)
    df['aoIndicator'] = AO_indicator.awesome_oscillator()
    return df

def provideSignals(df):
    signals = []
    i = 34
    numberOfDp = len(df)

    while i < numberOfDp:
    # Going long
        # Check if the 3ema has crossed above the median band
        # First check if the 3ema is below the median band
        # Next check if the 3ema has crossed above the median band
        if df['3ema'].iat[i - 1] < df['medianBand'].iat[i - 1]:
            if df['3ema'].iat[i] > df['medianBand'].iat[i]:
                # Next check if the AO is close to crossing the zero line
                if df['aoIndicator'].iat[i] < 0.001 and df['aoIndicator'].iat[i] > -0.001:
                    # Check the colour of the current AO stick
                    if df['aoIndicator'].iat[i] > df['aoIndicator'].iat[i - 1]:
                        signals.append(enterTrade(df, i, "Green", "Buy"))
                    else:
                        signals.append(enterTrade(df, i, "Red", "Buy"))
        
        # Going short
        # Check if the 3ema has crossed below the median band
        # First check if the 3ema is above the median band
        # Next check if the 3ema has crossed below the median band
        if df['3ema'].iat[i - 1] > df['medianBand'].iat[i - 1]:
            if df['3ema'].iat[i] < df['medianBand'].iat[i]:
                # Next check if the AO is close to crossing the zero line
                if df['aoIndicator'].iat[i] < 0.001 and df['aoIndicator'].iat[i] > -0.001:
                    # Check the colour of the current AO stick
                    if df['aoIndicator'].iat[i] > df['aoIndicator'].iat[i - 1]:
                        signals.append(enterTrade(df, i, "Green", "Sell"))
                    else:
                        signals.append(enterTrade(df, i, "Red", "Sell"))

        i += 1
    
    return signals
 
def enterTrade(df, i, aoColour, tradeType):
    entryPrice = df['close'].iat[i]
    pipDp = 10000
    originalI = i
    numberOfDp = len(df)
    
    
    while i < numberOfDp:
        if aoColour == "Green":
            if df['aoIndicator'].iat[i] < df['aoIndicator'].iat[i - 1]:
                exitPrice = df['close'].iat[i]
                tradeTime = i - originalI
                if tradeType == "Buy":
                    pipsGained = (exitPrice - entryPrice) * pipDp
                    percentageGained = ((exitPrice - entryPrice) / entryPrice) * 100
                    if exitPrice > entryPrice:
                        successfulTrade = True
                    else:
                        successfulTrade = False
                elif tradeType == "Sell":
                    pipsGained = (entryPrice - exitPrice) * pipDp
                    percentageGained = ((entryPrice - exitPrice) / entryPrice) * 100
                    if exitPrice < entryPrice:
                        successfulTrade = True
                    else:
                        successfulTrade = False 
                return signalObject(originalI, entryPrice, exitPrice, pipsGained, percentageGained, tradeTime, successfulTrade)
        
        if aoColour == "Red":
            if df['aoIndicator'].iat[i] > df['aoIndicator'].iat[i - 1]:
                exitPrice = df['close'].iat[i]
                tradeTime = i - originalI
                if tradeType == "Buy":
                    pipsGained = (exitPrice - entryPrice) * pipDp
                    percentageGained = ((exitPrice - entryPrice) / entryPrice) * 100
                    if exitPrice > entryPrice:
                        successfulTrade = True
                    else:
                        successfulTrade = False
                elif tradeType == "Sell":
                    pipsGained = (entryPrice - exitPrice) * pipDp
                    percentageGained = ((entryPrice - exitPrice) / entryPrice) * 100
                    if exitPrice < entryPrice:
                        successfulTrade = True
                    else:
                        successfulTrade = False
                return signalObject(originalI, entryPrice, exitPrice, pipsGained, percentageGained, tradeTime, successfulTrade)

        i += 1     

    return signalObject(originalI, entryPrice, 0, 0, 0, 0, None)


def signalObject(originalI, entryPrice, exitPrice, pipsGained, percentageGained, tradeTime, successfulTrade):
    obj = {
        'originalI': originalI,
        'entryPrice': entryPrice,
        'exitPrice': exitPrice,
        'pipsGained': pipsGained,
        'percentageGained': percentageGained,
        'tradeTime': tradeTime,
        'successfulTrade': successfulTrade
    }
    return obj

def stats(signals):
    successfulTrades = 0
    unsuccessfulTrades = 0
    incompleteTrades = 0
    percentageGain = 0
    totalPipsGained = 0
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
        
        percentageGain += signal['percentageGained']
        totalPipsGained += signal['pipsGained']
        profits.append(signal['percentageGained'])


    winRate = (successfulTrades / len(signals)) * 100
    print("Number of successful trades: " + str(successfulTrades))
    print("Number of unsuccessful trades: " + str(unsuccessfulTrades))
    print("Number of incomplete trades: " + str(incompleteTrades))
    print("Percentage gain: " + str(percentageGain) + " %")
    print("Total pips gained: " + str(totalPipsGained))
    print("Win rate % = " + str(winRate))
    print("Highest win streak: " + str(biggestWinStreak))
    print("Highest loss streak: " + str(biggestLossStreak))
    print("Biggest gain: " + str(max(profits)))
    print("Biggest loss: " + str(min(profits)))

def main():
    pd.set_option('display.max_rows', None)
    df = requestData("AUDUSD=X", "10d", "30m")
    df.columns= df.columns.str.lower()
    df = enableEMA(df, 3)
    df = enableBollingerBands(df)
    df = enableAwesomeIndicator(df)
    
    print(df)
    
    signals = provideSignals(df)
    for signal in signals:
        print(signal)
    
    print("=========================================================")
    print('RESULTS SUMMARY')
    print("=========================================================")
    stats(signals)
    
main()
    