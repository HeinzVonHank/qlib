import ccxt
import pandas as pd
from datetime import datetime

def get_crypto_data(symbol, start_date, end_date, timeframe='1d'):
    """
    从指定交易所获取历史K线数据
    """
    exchange = ccxt.okx() 
    
    start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
    
    all_ohlcvs = []
    
    print(f"开始从 {exchange.name} 获取 {symbol} 的数据...")
    
    while start_ts < end_ts:
        try:
            # 每次最多获取1000条数据 (不同交易所的 limit 可能不同, okx是100)
            # ccxt 会自动处理分页，所以我们只需不断请求
            ohlcvs = exchange.fetch_ohlcv(symbol, timeframe, since=start_ts, limit=100)
            if len(ohlcvs) == 0:
                break
            
            # 更新下一次请求的起始时间
            start_ts = ohlcvs[-1][0] + 1 
            all_ohlcvs.extend(ohlcvs)
            print(f"已获取到 {datetime.fromtimestamp(ohlcvs[-1][0] / 1000).strftime('%Y-%m-%d')} 的数据")
            
        except Exception as e:
            print(f"获取数据时发生错误: {e}")
            break
            
    df = pd.DataFrame(all_ohlcvs, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df[df['datetime'] < pd.to_datetime(end_date)]
    
    return df

if __name__ == '__main__':
    # 交易对在各大交易所通用
    symbols = ['BTC/USDT', 'ETH/USDT']
    start_date = '2020-01-01'
    end_date = '2025-07-15'
    
    full_df = pd.DataFrame()
    
    for symbol in symbols:
        instrument_name = symbol.replace('/', '') 
        df = get_crypto_data(symbol, start_date, end_date)
        df['instrument'] = instrument_name
        full_df = pd.concat([full_df, df])

    # 重新排列列以符合 Qlib 格式要求
    qlib_df = full_df[['datetime', 'instrument', 'open', 'high', 'low', 'close', 'volume']]
    
    # 保存为 CSV
    output_path = 'crypto_data_ohlcv.csv'
    qlib_df.to_csv(output_path, index=False)
    print(f"数据已成功保存到 {output_path}")