import pandas as pd
import numpy as np
import talib

def predict_trade(data_path: str) -> dict:
    df = pd.read_csv(data_path, names=['day', 'timestamp', 'value'], header=0)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    ohlc = df['value'].resample('1min').ohlc().ffill()
    
    close = ohlc['close'].values
    high = ohlc['high'].values
    low = ohlc['low'].values
    
    rsi = talib.RSI(close, timeperiod=14)
    macd, macd_signal, _ = talib.MACD(close, 12, 26, 9)
    ema_fast = talib.EMA(close, timeperiod=10)
    ema_slow = talib.EMA(close, timeperiod=20)
    
    signals = np.zeros(len(close), dtype=int)
    
    for i in range(26, len(close)):
        buy_condition = (rsi[i] < 50 and macd[i] > macd_signal[i] and ema_fast[i] > ema_slow[i])
        sell_condition = (rsi[i] > 50 and macd[i] < macd_signal[i] and ema_fast[i] < ema_slow[i])
        
        if buy_condition:
            signals[i] = 1
        elif sell_condition:
            signals[i] = -1
    
    if np.sum(np.abs(signals)) == 0:
        for i in range(26, len(close)):
            if rsi[i] < 45:
                signals[i] = 1
            elif rsi[i] > 55:
                signals[i] = -1
    
    returns = np.diff(close) / close[:-1]
    strategy_returns = returns * signals[:-1]
    
    cumulative_returns = np.prod(1 + strategy_returns) - 1
    
    mean_ret = np.mean(strategy_returns)
    std_ret = np.std(strategy_returns)
    sharpe = (mean_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0.0
    
    cumulative = np.cumprod(1 + strategy_returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (running_max - cumulative) / running_max
    max_dd = np.max(drawdown) if len(drawdown) > 0 else 0.0
    
    return {
        'signals': signals,
        'metrics': {
            'cumulative_returns_final': float(cumulative_returns),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_dd)
        }
    }