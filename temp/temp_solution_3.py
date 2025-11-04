import pandas as pd
import numpy as np
import talib

def predict_trade(data_path: str) -> dict:
    # 1. Load and resample data
    df = pd.read_csv(data_path, names=['day', 'timestamp', 'value'], header=0)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    ohlc = df['value'].resample('1min').ohlc().ffill()

    # 2. Calculate indicator - MACD
    close = ohlc['close'].values
    macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    # 3. Generate trading signals based on MACD
    signals = np.zeros(len(close), dtype=int)
    signals[(macd > signal) & (np.roll(macd, 1) <= np.roll(signal, 1))] = 1  # Buy signal
    signals[(macd < signal) & (np.roll(macd, 1) >= np.roll(signal, 1))] = -1  # Sell signal

    # 4. Calculate performance metrics
    returns = np.diff(close) / close[:-1]
    strategy_returns = returns * signals[:-1]

    # Cumulative returns
    cumulative_returns = np.prod(1 + strategy_returns) - 1

    # Sharpe ratio (with safety check)
    mean_ret = np.mean(strategy_returns)
    std_ret = np.std(strategy_returns)
    sharpe = (mean_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0.0

    # Max drawdown
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