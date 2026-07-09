import numpy as np
import pandas as pd
from scipy.stats import norm
import random
import matplotlib.pyplot as plt
    

class OptionsPricer:
    def __init__(self, S__t, K, vol, r, t, N):
        self.S__t = S__t
        self.K = K
        self.vol = vol
        self.r = r
        self.t = t / 365
        self.N = N



    def black(self):
        d1 = (np.log(self.S__t /self.K) + (self.r + (self.vol**2 / 2)) * self.t) / (self.vol * np.sqrt(self.t))
        d2 = d1 - self.vol * np.sqrt(self.t)
        C = norm.cdf(d1) * self.S__t - norm.cdf(d2) * self.K * np.exp(-self.r * self.t)
        P = self.K * np.exp(-self.r * self.t) * norm.cdf(-d2) - self.S__t * norm.cdf(-d1)
        return float(C), float(P)
  

    def binomial(self):
        
            deltat = self.t / self.N
            d = np.exp(-self.vol * np.sqrt(deltat))
            u = 1 / d
            p = (np.exp(self.r * deltat) - d) / (u - d)
    
        
            
            calllst = []
            putlst = []
            

            uexp = self.N
            dexp = 0
            
            for _ in range(self.N):
                aqr = self.S__t * (u ** uexp) * (d ** dexp)
                calllst.append(aqr)
                putlst.append(aqr)
                if uexp == 1:
                    atr = self.S__t * (d ** self.N)
                    calllst.append(atr)
                    putlst.append(atr)
                else:
                    uexp -= 1
                    dexp += 1
                    
                
            Call_Payoffs = [max(S_t- self.K, 0.0) for S_t in calllst]
            Put_Payoffs = [max(self.K - S_t, 0.0) for S_t in putlst]

            values = Call_Payoffs

            while len(values) > 1:
                V = []

                for j in range(len(values) - 1):

                    Vs = values[j]
                    Vt = values[j+1]
                    V.append(float(np.exp(-self.r * deltat) * (p * Vs + (1- p)* Vt)))
                    
                values = V
                
            call_price = values[0]
            
#################################################################################################################################################################
            
            values = Put_Payoffs
            while len(values) > 1:
                V = []

                for j in range(len(values) - 1):

                    Vs = values[j]
                    Vt = values[j+1]
                    V.append(float(np.exp(-self.r * deltat) * (p * Vs + (1- p)* Vt)))
                    
                values = V
                
            put_price = values[0]
            
            return call_price, put_price
            
            
        
    def montecarlo(self):
        Z = np.random.normal(0,1, self.N)
        St = self.S__t * np.exp((self.r - 1/2 * self.vol**2)* self.t + self.vol * np.sqrt(self.t) * Z) 
        Call_Payoffs = [max(i - self.K, 0.0) for i in St]
        Put_Payoffs = [max(self.K - j, 0.0) for j in St]
        
        Call = np.exp(-self.r * self.t) * np.mean(Call_Payoffs)
        Put = np.exp(-self.r * self.t) * np.mean(Put_Payoffs)
        return Call, Put


