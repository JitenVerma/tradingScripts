class Signal:
    def __init__(self, index, entryType, entryPrice, ATR, df):
        self.index = index + 1
        self.entryPrice = entryPrice
        self.df = df
        self.successfulTrade = None
        self.profit = 0
        if entryType == 0:
            self.entryType = 'Buy'
            self.stopLoss = entryPrice - (2*ATR)
            self.takeProfit = entryPrice + (4*ATR)
        elif entryType == 1:
            self.entryType = 'Sell'
            self.stopLoss = entryPrice + (2*ATR)
            self.takeProfit = entryPrice - (4*ATR)
        self.determineIfSuccessful()
        

    def postSignal(self):
        entrySignal = str(self.index) + '\n'
        entrySignal += self.entryType + ': ' + str(self.entryPrice) + '\n'
        entrySignal += 'Stop Loss: ' + str(self.stopLoss) + '\n'
        entrySignal += "Take Profit: " + str(self.takeProfit)
        return entrySignal
    
    def determineIfSuccessful(self):
        #Check if buy order has completed
        if self.entryType == 'Buy':
            for i in range(self.index, len(self.df)):
                #Check if price has gone below stop loss
                if self.df['low'].iat[i] < self.stopLoss:
                    self.successfulTrade = False
                    self.profit = self.determineProfit()
                    return

                #Check if price has gone above take profit
                if self.df['high'].iat[i] > self.takeProfit:
                    self.successfulTrade = True
                    self.profit = self.determineProfit()
                    return
        #Check if sell order has completed
        if self.entryType == 'Sell':
            for i in range(self.index, len(self.df)):
                #Check if price has gone above stop loss
                if self.df['low'].iat[i] > self.stopLoss:
                    self.successfulTrade = False
                    self.profit = self.determineProfit()
                    return

                #Check if price has gone below take profit
                if self.df['high'].iat[i] < self.takeProfit:
                    self.successfulTrade = True
                    self.profit = self.determineProfit()
                    return

    def determineProfit(self):
        if self.getSuccessfulTrade() == True:
            return ((abs(self.getEntryPrice() - self.getTakeProfit()) / self.getEntryPrice()) * 100)
        if self.getSuccessfulTrade() == False:
            return -((abs(self.getEntryPrice() - self.getStopLoss()) / self.getEntryPrice()) * 100)


    def getSuccessfulTrade(self):
        return self.successfulTrade
    
    def getEntryPrice(self):
        return self.entryPrice
    
    def getStopLoss(self):
        return self.stopLoss
    
    def getTakeProfit(self):
        return self.takeProfit
    
    def getProfit(self):
        return self.profit
