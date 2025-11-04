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
    ema_fast = talib.EMA(close, timeperiod=9)
    ema_slow = talib.EMA(close, timeperiod=21)
    
    signals = np.zeros(len(close), dtype=int)
    
    for i in range(26, len(close)):
        bullish_conditions = 0
        bearish_conditions = 0
        
        if rsi[i] < 50:
            bullish_conditions += 1
        elif rsi[i] > 50:
            bearish_conditions += 1
            
        if macd[i] > macd_signal[i]:
            bullish_conditions += 1
        elif macd[i] < macd_signal[i]:
            bearish_conditions += 1
            
        if ema_fast[i] > ema_slow[i]:
            bullish_conditions += 1
        elif ema_fast[i] < ema_slow[i]:
            bearish_conditions += 1
            
        if bullish_conditions >= 2:
            signals[i] = 1
        elif bearish_conditions >= 2:
            signals[i] = -1
    
    if np.sum(np.abs(signals)) == 0:
        for i in range(14, len(close)):
            if rsi[i] < 45:
                signals[i] = 1
            elif rsi[i] > 55:
                signals[i] = -1
    
    returns = np.diff(close) / close[:-1]
    strategy_returns = returns * signals[:-1]
    strategy_returns = strategy_returns[np.isfinite(strategy_returns)]
    
    if len(strategy_returns) > 0 and np.any(strategy_returns != 0):
        log_returns = np.log1p(strategy_returns)
        log_returns = log_returns[np.isfinite(log_returns)]
        if len(log_returns) > 0:
            cumulative_returns = np.expm1(np.sum(log_returns))
        else:
            cumulative_returns = 0.0
            
        mean_ret = np.mean(strategy_returns)
        std_ret = np.std(strategy_returns)
        if std_ret > 0 and np.isfinite(std_ret):
            sharpe = mean_ret / std_ret * np.sqrt(252)
        else:
            sharpe = 0.0
            
        cumulative_wealth = np.cumprod(1 + strategy_returns)
        running_max = np.maximum.accumulate(cumulative_wealth)
        drawdown = (running_max - cumulative_wealth) / running_max
        max_dd = np.max(drawdown) if len(drawdown) > 0 else 0.0
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
    
    cumulative_returns = max(-1.0, min(10.0, cumulative_returns))
    sharpe = max(-5.0, min(10.0, sharpe))
    max_dd = max(0.0, min(1.0, max_dd))
    
    return {
        'signals': signals,
        'metrics': {
            'cumulative_returns_final': float(cumulative_returns),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_dd)
        }
    }