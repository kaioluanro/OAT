from datetime import datetime, timedelta
from lightweight_charts import Chart
import asyncio
import pandas as pd
import time
import schedule
import requests
import json
import os
#==================
from indicator import SMAs,sinais
from ENUMs import exchange as exchange_
from ENUMs import timeframe as timeframe_
from telegram_bot import send_message
from webService import sendWebhook
from config import config_load, config_salver

def get_data_exchange(symbol='BTCUSDT',timeframe="15m",limit=10, exchange="bitget"):
    """Pega os data historico em real-time da exchange.

    Args:
        symbol (str, optional): Simbolo do ativo. Defaults to 'BTCUSDT'.
        min (int, optional): timeframe do ativo. Defaults to 15.
        limit (int, optional): numero total de candle requisitados. limite 1 ate 1000. Defaults to 10.
        exchange (str, optional): Qual corretora pega os dados. Defaults to "bitget" but change "binance".

    Returns:
        json
    """
    dataJson={'code': '00000', 'msg': 'success', 'requestTime': 1742743603478, 'data': [['1742734800000', '84734.9', '84750', '84668', '84731.1', '17.425709', '1476010.72922155', '1476010.72922155'], ['1742735700000', '84731.1', '84973.03', '84731.1', '84953.95', '29.449869', '2499690.34663857', '2499690.34663857'], ['1742736600000', '84953.95', '85013.17', '84865.49', '84865.5', '58.346774', '4956563.85864525', '4956563.85864525'], ['1742737500000', '84865.5', '85090.79', '84858', '85064.72', '46.893317', '3985662.00030487', '3985662.00030487'], ['1742738400000', '85064.72', '85185.34', '84967.79', '85035.06', '121.981407', '10372971.69102061', '10372971.69102061'], ['1742739300000', '85035.06', '85077.62', '84866.99', '84901.58', '53.312995', '4528764.1817422', '4528764.1817422'], ['1742740200000', '84901.58', '85098.88', '84901.58', '84985.29', '31.316587', '2661880.791576', '2661880.791576'], ['1742741100000', '84985.29', '85044.07', '84879', '84888.01', '26.634353', '2262295.10905733', '2262295.10905733'], ['1742742000000', '84888.01', '85044.07', '84888', '85028.52', '25.515634', '2167965.47381441', '2167965.47381441'], ['1742742900000', '85028.52', '85145.05', '85001.15', '85119.48', '35.975157', '3061188.45365309', '3061188.45365309']]}
    dataJson_binance=[[1742735700000,"84752.90","84943.50","84665.10","84943.50","128916.394",1742736599999,"10936016998.72870",11704,"80642.030","6841869142.59800","0"],[1742736600000,"84943.30","85009.30","84864.00","84864.00","113295.712",1742737499999,"9623155452.95490",8865,"57886.406","4918078614.38250","0"],[1742737500000,"84864.00","85023.00","84847.80","84975.70","112088.504",1742738399999,"9521740822.96030",8192,"58012.892","4929452083.69750","0"],[1742738400000,"85023.00","85080.20","84940.40","84980.20","118669.816",1742739299999,"10088837486.02200",9474,"66999.586","5697711676.14240","0"],[1742739300000,"85045.60","85082.20","84882.20","84921.80","120626.563",1742740199999,"10249515341.90660",8389,"55789.826","4741943352.16050","0"],[1742740200000,"84921.80","85046.00","84874.00","84978.20","111422.538",1742741099999,"9468029765.84910",8624,"58390.831","4963189599.93040","0"],[1742741100000,"85002.90","85059.30","84899.30","84940.20","108435.761",1742741999999,"9213649061.85620",8888,"53880.293","4579565843.43140","0"],[1742742000000,"84903.60","85047.10","84889.30","85019.90","104130.275",1742742899999,"8848590190.49060",7730,"53291.099","4529981860.43670","0"],[1742742900000,"85046.00","85139.40","84952.30","85103.40","114623.276",1742743799999,"9750714381.16890",8660,"64330.624","5473782777.12190","0"],[1742743800000,"85103.40","85193.00","85010.70","85193.00","103100.059",1742744699999,"8774040891.70100",8994,"57800.900","4920337537.66650","0"]]

    t=timeframe_[exchange][timeframe]
    
    if exchange==exchange_['bitget']:
        api_url = f"https://api.bitget.com/api/v2/spot/market/candles?symbol={symbol}&granularity={t}&limit={limit}"
        return exchange,json.loads(requests.get(api_url).content)
    elif exchange==exchange_['binance']:
        api_url = f"https://testnet.binancefuture.com/fapi/v1/klines?symbol={symbol}&interval={t}&limit={limit}"
        return exchange,json.loads(requests.get(api_url).content)
    elif exchange=='test_bitget':
        return 'bitget',dataJson
    elif exchange=='test_binance':
        return 'binance',dataJson_binance

def constructor_ohlc(data_exchange):
    """
    Constroi ohlc para ser consumidor.
    
    Returns:
        Dataframe
    """
    exchange,response_json=data_exchange
    
    if exchange==exchange_['bitget']:
        # Criar o DataFrame
        colunas = ['timestamp', 'open', 'high', 'low', 'close', 'volume_base', 'volume', 'volume_quote']
        df = pd.DataFrame(response_json['data'], columns=colunas)
        # Converter a coluna Timestamp para datetime
        df['time'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
        df['time'] = df['time'].dt.strftime('%d-%m-%Y %H:%M:%S')
        return df
    elif exchange==exchange_['binance']:
        # Criar o DataFrame
        colunas = ['timestamp', 'open', 'high', 'low', 'close', 'volume','close time','quote asset volume','number of trades', 'volume_base', 'Volume_quote', 'ignore']
        df = pd.DataFrame(response_json, columns=colunas)
        # Converter a coluna Timestamp para datetime
        df['time'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
        df['time'] = df['time'].dt.strftime('%d-%m-%Y %H:%M:%S')
        return df

def sleep_minuto(minutes=1):
    """Função para calcular o tempo até o próximo minuto redondo
    """
    agora = datetime.now()
    proximo_minuto = (agora + timedelta(minutes=minutes)).replace(second=0, microsecond=0)
    tempo_restante = (proximo_minuto - agora).total_seconds()
    time.sleep(tempo_restante)

def convertTimestampToDate(timestamp):
    timestamp_em_segundos = timestamp / 1000
    data_hora = datetime.fromtimestamp(timestamp_em_segundos)
    data_hora_formatada = data_hora.strftime('%d-%m-%Y %H:%M:%S')
    return data_hora_formatada

from datetime import datetime, timedelta

def proximo_tempo_atualizacao(timeframe):
    agora = datetime.now()
    minutos = timeframe_['num'][timeframe]  # Pega o valor em minutos (ex: 1, 5, 15...)
    
    if minutos < 60:  # Timeframes menores que 1h (1min, 5min, 15min...)
        # Calcula o próximo múltiplo exato
        proximo_minuto = ((agora.minute // minutos) + 1) * minutos
        delta = timedelta(minutes=proximo_minuto - agora.minute, seconds=-agora.second, microseconds=-agora.microsecond)
        return agora + delta
    else:  # Timeframes em horas (1h, 4h...)
        horas = minutos // 60
        proxima_hora = ((agora.hour // horas) + 1) * horas
        delta = timedelta(hours=proxima_hora - agora.hour, minutes=-agora.minute, seconds=-agora.second, microseconds=-agora.microsecond)
        return agora + delta

def salve_olhc():
    config = config_load()
    df = constructor_ohlc(get_data_exchange(symbol=config['symbol'], limit=500, timeframe=config['timeframe'], exchange=config['exchange']))
    lastSymbol = config['symbol']
    lastTimeframe = config['timeframe']
    
    # Calcula o próximo tempo exato de atualização
    proximo_update = proximo_tempo_atualizacao(config['timeframe'])
    
    while True:
        agora = datetime.now()
        config = config_load()
        
        # Verifica mudança no símbolo ou timeframe
        if (lastSymbol != config['symbol']) or (lastTimeframe != config['timeframe']):
            
            print(f"🔄 Config alterada! Novo: {config['symbol']} ({config['timeframe']})")
            
            df = constructor_ohlc(get_data_exchange(symbol=config['symbol'], limit=500, timeframe=config['timeframe'], exchange=config['exchange']))
            df_ = sinais(df)
            df_.to_csv('dados_personalizados.csv')
            lastSymbol = config['symbol']
            lastTimeframe = config['timeframe']
            proximo_update = proximo_tempo_atualizacao(config['timeframe'])  # Recalcula o tempo
            asyncio.run(send_message(f'🔄 Config atualizada: {config["symbol"]} ({config["timeframe"]})'))
            continue
        
        # Verifica se é hora de atualizar (tempo sincronizado)
        if agora >= proximo_update:
            print(f"⏰ Atualizando em {agora.strftime('%H:%M:%S')} (Timeframe: {config['timeframe']})")
            
            # Atualiza os dados
            df2 = constructor_ohlc(get_data_exchange(symbol=config['symbol'], limit=1, timeframe=config['timeframe'], exchange='bitget'))
            df = pd.concat([df, df2], ignore_index=True)
            df_ = sinais(df)
            
            dataWebhook = {
                    'symbol': config['symbol'],
                    'compra_8_20': False, 
                    'venda_8_20': False,
                    'compra_elefante': False, 
                    'venda_elefante': False,
                    'candles': []
                }
            
            # Verificação de sinais (exemplo)
            if df_['compra'].iloc[-1] == True:
                asyncio.run(send_message(f'🚅💚💚💚 {config['symbol']} - Trem da 8:20 - Buy 💚💚💚 🚅')) # enviar para Telegram
                dataWebhook['compra_8_20'] = True
                dataWebhook['candles'] = df_.tail(10).fillna(0).to_dict(orient='records')
            elif df_['venda'].iloc[-1]==True:
                asyncio.run(send_message(f'🚅❤❤❤ {config['symbol']} - Trem da 8:20 - Sell Sell Sell ❤❤❤ 🚅'))
                dataWebhook['venda_8_20'] = True
                dataWebhook['candles'] = df_.tail(10).fillna(0).to_dict(orient='records')
            elif df_['bullElephantBar'].iloc[-1]==True:
                asyncio.run(send_message(f'🐘💚💚💚 {config['symbol']} - Elephant - Buy 💚💚💚 🐘'))
                dataWebhook['compra_elefante'] = True
                dataWebhook['candles'] = df_.tail(10).fillna(0).to_dict(orient='records')
            elif df_['bearElephantBar'].iloc[-1]==True:
                asyncio.run(send_message(f'🐘❤❤❤ {config['symbol']} - Elephant - Sell ❤❤❤ 🐘'))
                dataWebhook['venda_elefante'] = True
                dataWebhook['candles'] = df_.tail(10).fillna(0).to_dict(orient='records')
            
            # Salva os dados em JSON e CSV
            with open("dadostoESP32.json", "w", encoding="utf-8") as arquivo:
                json.dump(dataWebhook, arquivo, ensure_ascii=False, indent=4)
            df_.to_csv('dados_personalizados.csv')
            
            # Calcula o próximo horário exato
            proximo_update = proximo_tempo_atualizacao(config['timeframe'])
        
        # Pequena pausa para evitar sobrecarga
        time.sleep(0.1)