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
    macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    ema_fast = talib.EMA(close, timeperiod=9)
    ema_slow = talib.EMA(close, timeperiod=21)
    
    signals = np.zeros(len(close), dtype=int)
    
    for i in range(26, len(close)):
        bullish_momentum = (ema_fast[i] > ema_slow[i] and 
                           macd[i] > macd_signal[i] and 
                           rsi[i] > 45 and rsi[i] < 70)
        
        bearish_momentum = (ema_fast[i] < ema_slow[i] and 
                           macd[i] < macd_signal[i] and 
                           rsi[i] < 55 and rsi[i] > 30)
        
        if bullish_momentum:
            signals[i] = 1
        elif bearish_momentum:
            signals[i] = -1
    
    if np.sum(np.abs(signals)) == 0:
        for i in range(26, len(close)):
            if rsi[i] < 50:
                signals[i] = 1
            elif rsi[i] > 50:
                signals[i] = -1
    
    returns = np.diff(close) / close[:-1]
    strategy_returns = returns * signals[:-1]
    strategy_returns = strategy_returns[np.isfinite(strategy_returns)]
    
    if len(strategy_returns) > 0:
        log_returns = np.log1p(strategy_returns)
        log_returns = log_returns[np.isfinite(log_returns)]
        if len(log_returns) > 0:
            cumulative_returns = np.expm1(np.sum(log_returns))
        else:
            cumulative_returns = 0.0
    else:
        cumulative_returns = 0.0
    
    if len(strategy_returns) > 1:
        mean_ret = np.mean(strategy_returns)
        std_ret = np.std(strategy_returns, ddof=1)
        sharpe = (mean_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0.0
    else:
        sharpe = 0.0
    
    if len(strategy_returns) > 0:
        portfolio_values = np.cumprod(1 + strategy_returns)
        running_max = np.maximum.accumulate(portfolio_values)
        drawdowns = (running_max - portfolio_values) / running_max
        max_dd = np.max(drawdowns)
    else:
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