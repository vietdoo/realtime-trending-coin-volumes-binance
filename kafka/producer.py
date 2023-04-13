import requests
import json
import time
from kafka import KafkaProducer
#from config import *
import time
import datetime
from datetime import date
from datetime import timedelta
import os
topic_name = 'coin'
servers = 'localhost:9092'
servers = 'kafka:9092'
LIMIT = 30
N = 5

#time.sleep(10)
print(servers)

while (True):

    try:
        producer = KafkaProducer(bootstrap_servers=[servers])
        break
    except:
        pass
    time.sleep(1)

def requestCoin(coin):
    url = f'https://api.binance.com/api/v3/klines?symbol={coin}&interval=1m&limit={LIMIT}'
    r = requests.get(url)
    data = r.json()
    return data

def getCoins(coin_list):
    data = {}
    for coin in coin_list:
        try:
            coin_info = requestCoin(coin)
            coin_aka = coin.replace('USDT', '')
            data[coin_aka] = coin_info
            
        except Exception as e:
            print('getCoinsE:', e)
        time.sleep(1)
    return data

def cleanCoin(data, name):
    coin_data = {}
    coin_data['name'] = name 
    now = datetime.datetime.now()
    timestart = int(now.timestamp())
    coin_data['timestart'] = timestart
   # coin_data['price'] = float(data[3])
    coin_data['volume'] = float(data[7])
   # coin_data['num'] = float(data[8])
    coin_data
    return coin_data

def sendCoins(data, sleep_time = 5):
    name_list = [x for x in data]
    for i in range(len(data[name_list[0]])):
        for name in name_list:
            print(name)
            coin = data[name][i]
            t0 = (coin[0])
            t1 = (coin[6])
            volume = coin[7]
            d0 = datetime.datetime.fromtimestamp(t0 / 1000 )
            d1 = datetime.datetime.fromtimestamp(t1 / 1000 )
            send_data = cleanCoin(coin, name)
            print(d0, '-->', d1, 'volume: ', volume)  
            producer.send(topic_name, json.dumps(send_data).encode('utf-8'))
            time.sleep(sleep_time)
        
        
def getCoinsList():
    # url = 'https://api.binance.com/api/v3/ticker/24hr'
    # r = requests.get(url)
    # df = r.json()
    # df = [coin for coin in df if coin["symbol"].endswith("USDT")]
    # sdf = sorted(df, key = lambda x: float(x['lastPrice']), reverse = True)[:N]
    # return [coin['symbol'] for coin in sdf]

    return ['BTCUSDT', 'BNBUSDT', 'ETHUSDT', 'DOGEUSDT', 'XRPUSDT', 
            'SHIBUSDT', 'ADAUSDT', 'ARBUSDT', 'MATICUSDT', 'SOLUSDT']

coin_list = getCoinsList()
while True:
    
    coins = getCoins(coin_list)
    sendCoins(coins)


producer.close()

