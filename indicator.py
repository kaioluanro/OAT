from ta.trend import sma_indicator
import pandas as pd
import numpy as np

def SMAs(df,ma1,ma2,ma3,ma4):
    """Simples medias moveis.

    Args:
        df (Dataframe): dataframe
        ma1 (int): perioda media 1
        ma2 (int): perioda media 2
        ma3 (int): perioda media 3
        ma4 (int): perioda media 4

    Returns:
        Series:
    """
    s1=sma_indicator(df['close'],ma1)
    s2=sma_indicator(df['close'],ma2)
    s3=sma_indicator(df['close'],ma3)
    s4=sma_indicator(df['close'],ma4)
    
    return s1,s2,s3,s4

def sinais(df):
    s1,s2,s3,s4 = SMAs(df,8,20,40,200)
    df['sma1'] =s1
    df['sma2'] =s2
    df['sma3'] =s3
    df['sma4'] =s4
    
    # Convertendo as colunas para numérico
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['val'] = df[['open', 'high', 'low', 'close']].sum(axis=1) / 4
    # Define a tendência
    df['up'] = df['val'] > df['val'].shift(1)  # Compara com o valor anterior
    df['down'] = df['val'] <= df['val'].shift(1)
    
    # Verifica troca de tendência
    df['compra'] = df['down'].shift(1) & df['up'] & (df['close'] > df['sma2'])
    df['venda'] = df['up'].shift(1) & df['down'] & (df['close'] < df['sma2'])
    
    # Verifica a condição de compra
    condicao_compra = df['down'].shift(1) & df['up'] & (df['close'] > df['sma2'])
    condicao_venda = df['up'].shift(1) & df['down'] & (df['close'] < df['sma2'])

    # Atribui o valor de 'close' à coluna 'compra' apenas quando a condição for verdadeira
    df['compra_price'] = np.where(condicao_compra, df['close'], np.nan)  # Use np.nan ou 0 como valor padrão
    df['venda_price'] = np.where(condicao_venda, df['close'], np.nan)  # Use np.nan ou 0 como valor padrão
    
    # Entradas do usuário
    length9 = 200  # Período para o cálculo do tamanho médio das velas
    volumeMultiplier = 1.5  # Multiplicador do volume para definir a barra de elefante
    followThroughBars = 3  # Número de barras de follow-through

    # Calcula o tamanho médio das velas (SMA do valor absoluto da diferença entre close e open)
    df['avgCandleSize'] = sma_indicator(abs(df['close'] - df['open']),length9)
    # Calcula o limiar de volume (SMA do volume multiplicado pelo multiplicador)
    df['volumeThreshold11'] = sma_indicator(df['volume'],length9) * volumeMultiplier

    # Define as barras de elefante
    df['bullElephantBar'] = (df['close'] > df['open']) & \
                            ((df['close'] - df['open']) > df['avgCandleSize']) & \
                            (df['volume'] > df['volumeThreshold11'])

    df['bearElephantBar'] = (df['open'] > df['close']) & \
                            ((df['open'] - df['close']) > df['avgCandleSize']) & \
                            (df['volume'] > df['volumeThreshold11'])
                            
    
    condicao_compra_elephant = (df['close'] > df['open'])& \
                                ((df['close'] - df['open']) > df['avgCandleSize']) & \
                                (df['volume'] > df['volumeThreshold11'])
                                
    condicao_venda_elephant  = (df['open'] > df['close']) & \
                            ((df['open'] - df['close']) > df['avgCandleSize']) & \
                            (df['volume'] > df['volumeThreshold11'])

    df['compra_price_elephant'] = np.where(condicao_compra_elephant, df['close'], np.nan)  # Use np.nan ou 0 como valor padrão
    df['venda_price_elephant'] = np.where(condicao_venda_elephant, df['close'], np.nan)  # Use np.nan ou 0 como valor padrão
    
    
    return df
