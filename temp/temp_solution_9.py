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
    ema_fast = talib.EMA(close, timeperiod=12)
    ema_slow = talib.EMA(close, timeperiod=26)
    
    signals = np.zeros(len(close), dtype=int)
    
    for i in range(26, len(close)):
        buy_conditions = 0
        sell_conditions = 0
        
        if rsi[i] < 50:
            buy_conditions += 1
        if rsi[i] > 50:
            sell_conditions += 1
            
        if macd[i] > macd_signal[i]:
            buy_conditions += 1
        if macd[i] < macd_signal[i]:
            sell_conditions += 1
            
        if ema_fast[i] > ema_slow[i]:
            buy_conditions += 1
        if ema_fast[i] < ema_slow[i]:
            sell_conditions += 1
        
        if buy_conditions >= 2:
            signals[i] = 1
        elif sell_conditions >= 2:
            signals[i] = -1
    
    if np.sum(np.abs(signals)) == 0:
        for i in range(26, len(close)):
            if rsi[i] < 45:
                signals[i] = 1
            elif rsi[i] > 55:
                signals[i] = -1
    
    returns = np.diff(close) / close[:-1]
    strategy_returns = returns * signals[:-1]
    
    strategy_returns = strategy_returns[np.isfinite(strategy_returns)]
    
    if len(strategy_returns) > 0:
        cumulative_returns = np.expm1(np.sum(np.log1p(np.clip(strategy_returns, -0.99, 10.0))))
        mean_ret = np.mean(strategy_returns)
        std_ret = np.std(strategy_returns)
        sharpe = (mean_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0.0
        
        cumulative = np.cumprod(1 + strategy_returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (running_max - cumulative) / running_max
        max_dd = np.max(drawdown)
    else:
        cumulative_returns = 0.0
        sharpe = 0.0
        max_dd = 0.0
    
    if not np.isfinite(cumulative_returns):
        cumulative_returns = 0.0
    if not np.isfinite(sharpe):
        sharpe = 0.0
    if not np.isfinite(max_dd):
        max_dd = 0.0
    
    cumulative_returns = np.clip(cumulative_returns, -1.0, 10.0)
    sharpe = np.clip(sharpe, -5.0, 10.0)
    max_dd = np.clip(max_dd, 0.0, 1.0)
    
    return {
        'signals': signals,
        'metrics': {
            'cumulative_returns_final': float(cumulative_returns),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_dd)
        }
    }