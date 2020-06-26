import numpy as np

def calc_correcao(N1,N2):
    SSC1 = 2/(N1+1) #rápida
    SSC2 = 2/(N2+1) #lenta
    a1= 1 - SSC1
    a2= 1 - SSC2
    return (a2-a1)/((1-a1)*(1-a2))

def calc_med_ema(sinal,N):
    ema = np.zeros(len(sinal))
    ema[0] = sinal[0]
    SSC = 2/(N+1)
    for i in range(1,len(sinal)):            
        ema[i] = ema[i-1]*(1-SSC) + sinal[i]*SSC
    return ema

def MACD(sinal,N1,N2,N3):
    correcao = calc_correcao(N1,N2)
    emaN1 = calc_med_ema(sinal,N1)
    emaN2 = calc_med_ema(sinal,N2)
    linha_MACD = (emaN1 - emaN2)/correcao # rápida - lenta (1 derivada)
    linha_sinal = calc_med_ema(linha_MACD,N3) # lenta
    return linha_sinal

def should_long(close):
# Tendência de alta----------------------------------------------
    estado = 0
    if MACD(close, 12*7, 26*7, 9*7 ) > 0:
        # Condição necessária  (convergência: linhas de mesmo sinal)
        if MACD(close, 7, 14, 13) > MACD(close, 12*7, 26*7, 9*7 ) and estado == 0:
            estado = 1

        # Condição suficiente 1 (princípio da divergência) (sinal opostos)
        if MACD(close, 7, 14, 13) < 0 and estado == 1:
            estado = 0
    else:
        estado = 0
    return

def should_short(close):
# %Tendência de queda---------------------------------------------------
    estado = 0
    if MACD(close, 12*7, 26*7, 9*7 ) < 0:
        # Condição necessária (convergência: linhas de mesmo sinal)
        if MACD(close, 7, 14, 13)< MACD(close, 12*7, 26*7, 9*7 ) and estado == 0:
            estado = 1
        
        #  %Condição suficiente 1 (princípio da divergência) (sinais opostos)
        if MACD(close, 7, 14, 13) > 0 and estado == 1:
            estado = 0
    else:
        estado = 0
    return

def sorting_indicator(sinal, N):
    # Obtém séries de dados ordenadas de forma crescente e decrescente
    # Utilizar Critério de corte em 92% e 130 periodos
    # Somente define tendência acima de 92%
    y_alta = np.sort(sinal)
    y_queda = y_alta[::-1]
    prec= 1e-3

    den =  np.sum(np.power((sinal - np.mean(sinal)),2))
    
    # Cálcula R2 de alta
    num =  np.sum(np.power((sinal - y_alta),2))
    R2_alta  = 100*(1 - num/(den+prec))

    # Cálcula R2 de queda
    num =  np.sum(np.power((sinal - y_queda),2))
    R2_queda  = 100*(1 - num/(den+prec))

    # Tomada de decisão: Qual a tendência preponderante
    if R2_alta > R2_queda:
        R2 = R2_alta
    else:
        R2 = -R2_queda
    return R2



###########################################################################
###########################   TESTES   ####################################
###########################################################################

import matplotlib.pyplot as plt
import pandas_datareader.data as web
data = np.array(web.DataReader('BTC-USD', 'yahoo', start = '2017-01-02', end = '2019-01-20')['Adj Close'].to_numpy())

# plt.plot(MACD(data, 12*7, 26*7, 9*7 ), color='red')
# plt.plot(MACD(data, 7, 14, 13), color='green')
# plt.plot(sorting_indicator(data,130))
# plt.show()
print(sorting_indicator(data,130))


        # %Obtém séries de dados ordenadas de forma crescente e decrescente
        # y_alta = sort(sinal,'ascend');
        # y_queda = y_alta(end:-1:1);
        # N =10;
        # prec= 1e-3;
        
        # den =  sum((sinal-mean(sinal)).^2);
        # den = calc_med_ema(den,N);
        
        # %Cálcula R2 de alta
        # num =  sum((sinal-y_alta).^2);
        # num =  calc_med_ema(num,N);
        # R2_alta  = max([0 100*(1 - num/(den+prec))]);
        
        # %Cálcula R2 de queda
        # num =  sum((sinal-y_queda).^2);
        # num =  calc_med_ema(num,N);
        # R2_queda  = max([0 100*(1 - num/(den+prec))]);

        # %Tomada de decisão: Qual a tendência preponderante
        # if R2_alta > R2_queda
        #     R2 = R2_alta;
        # else
        #     R2 = -R2_queda;
        # end  
