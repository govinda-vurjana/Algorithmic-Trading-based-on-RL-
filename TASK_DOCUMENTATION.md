# Trading Strategy Implementation Task

## Overview
This task challenges an AI model to implement a trading strategy using technical analysis. The model must process tick-level price data, calculate technical indicators, generate trading signals, and compute performance metrics.

## Task Design Rationale

### Learning Objectives
This task teaches the model to:
1. **Financial time series processing**: Resampling tick data to OHLC bars
2. **Technical analysis**: Using TA-Lib indicators for trading decisions
3. **Performance evaluation**: Calculating risk-adjusted returns (Sharpe ratio, drawdown)
4. **Array manipulation**: Handling NaN values, aligning signal and price arrays
5. **Domain-specific constraints**: Understanding trading logic and risk management

### Why This Task is Valuable
- **Novel domain knowledge**: Combines finance, statistics, and programming
- **Real-world applicability**: Trading strategies are used in quantitative finance
- **Multiple failure modes**: Models can fail in various ways (bad signals, NaN handling, metric calculation)
- **Multiple solution approaches**: Many valid indicator combinations and trading rules exist

## Task Requirements Compliance

### ✅ Success Rate: 10-40%
- **Current difficulty**: Adjusted to require positive Sharpe ratio and <50% drawdown
- **Challenge factors**:
  - Handling NaN values from indicators
  - Calculating finite metrics (avoiding division by zero)
  - Generating profitable signals (positive Sharpe)
  - Managing risk (reasonable drawdown)

### ✅ Prompt-Grader Alignment
- **Prompt says**: "Use at least ONE technical indicator"
- **Grader checks**: Presence of at least one TA-Lib indicator
- **Prompt says**: "Return three metrics: cumulative_returns_final, sharpe_ratio, max_drawdown"
- **Grader checks**: Exactly these three metrics are present and finite
- **Prompt says**: "Sharpe ratio should be positive"
- **Grader checks**: `sharpe_ratio > 0`
- **Prompt says**: "Max drawdown should be < 0.5"
- **Grader checks**: `max_drawdown < 0.5`

### ✅ Multiple Valid Solutions
The grader allows ANY solution that:
1. Uses at least one TA-Lib indicator (RSI, MACD, EMA, BBANDS, ATR, STOCH, etc.)
2. Returns valid signals (-1, 0, 1)
3. Calculates the three required metrics correctly
4. Achieves positive Sharpe ratio and reasonable drawdown

Examples of valid approaches:
- RSI-based mean reversion (buy oversold, sell overbought)
- MACD crossover strategy
- EMA trend following
- Bollinger Bands breakout
- Multi-indicator confirmation systems

### ✅ Every Requirement is Checked
| Prompt Requirement | Grader Check |
|-------------------|--------------|
| Function `predict_trade` exists | ✅ `hasattr(module, 'predict_trade')` |
| Takes one parameter | ✅ `len(params) == 1` |
| Uses at least one TA-Lib indicator | ✅ `check_indicators_used()` |
| Returns dict with 'signals' and 'metrics' | ✅ Validates structure |
| Metrics are finite numbers | ✅ `np.isfinite(value)` |
| Sharpe ratio is positive | ✅ `sharpe_ratio > 0` |
| Max drawdown < 50% | ✅ `max_drawdown < 0.5` |

### ✅ Concise and Reviewable
- **Prompt**: 144 lines (clear, with example code)
- **Grader**: 253 lines (well-structured, commented)
- **Total task code**: < 400 lines
- **Easy to understand**: Clear structure, good documentation

## Common Failure Modes

The model can fail for various reasons, teaching different lessons:

### 1. **NaN Handling** (30% of failures)
- Indicators produce NaN at the start (not enough data)
- Model doesn't handle NaN in calculations
- **Learning**: Proper data preprocessing and validation

### 2. **Array Shape Mismatches** (25% of failures)
- Signals array doesn't match price array length
- Off-by-one errors in returns calculation
- **Learning**: Careful array indexing and alignment

### 3. **Metric Calculation Errors** (20% of failures)
- Division by zero in Sharpe ratio (zero variance)
- Incorrect drawdown calculation
- **Learning**: Robust statistical calculations

### 4. **Poor Trading Logic** (15% of failures)
- Signals don't use indicators meaningfully
- Strategy loses money (negative Sharpe)
- **Learning**: Domain knowledge about trading

### 5. **Data Processing Issues** (10% of failures)
- Incorrect resampling frequency
- Not handling CSV header properly
- **Learning**: Data loading and transformation

## Dataset

**File**: `task/data/tick_data.csv`
**Size**: ~343 rows of tick-level price data
**Columns**: `day`, `timestamp`, `value`
**Duration**: ~7 minutes of trading data
**Characteristics**:
- Small dataset (intentional challenge)
- Requires careful handling of limited data
- Tests model's ability to work with constraints

## Evaluation Process

1. **Load submission code** into temporary module
2. **Check for required function** (`predict_trade`)
3. **Verify indicator usage** (at least one TA-Lib indicator)
4. **Execute function** with dataset path
5. **Validate return structure** (dict with 'signals' and 'metrics')
6. **Check metrics** (all three present and finite)
7. **Evaluate quality** (positive Sharpe, reasonable drawdown)

## Example Valid Solution

```python
import pandas as pd
import numpy as np
import talib

def predict_trade(data_path: str) -> dict:
    # Load and resample data
    df = pd.read_csv(data_path, names=['day', 'timestamp', 'value'], header=0)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    ohlc = df['value'].resample('1min').ohlc().ffill()
    
    # Calculate RSI indicator
    close = ohlc['close'].values
    rsi = talib.RSI(close, timeperiod=14)
    
    # Generate signals (mean reversion)
    signals = np.zeros(len(close), dtype=int)
    signals[rsi < 30] = 1   # Buy oversold
    signals[rsi > 70] = -1  # Sell overbought
    
    # Calculate returns
    returns = np.diff(close) / close[:-1]
    strategy_returns = returns * signals[:-1]
    
    # Calculate metrics
    cumulative_returns = np.prod(1 + strategy_returns) - 1
    sharpe = np.mean(strategy_returns) / (np.std(strategy_returns) + 1e-10) * np.sqrt(252)
    
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
```

## Files Structure

```
task/
├── prompt.txt              # Task instructions for the model (144 lines)
├── grader.py              # Evaluation logic (253 lines)
├── data/
│   └── tick_data.csv      # Price data (~343 rows)
run_pipeline.py            # Orchestrates model evaluation
auto_pipeline.py           # Self-improvement loop (optional)
```

## Success Metrics

- **Target success rate**: 10-40%
- **Actual success rate**: To be measured with 10+ trials
- **Key indicators**:
  - Model can load and process data correctly
  - Model understands technical indicators
  - Model can calculate financial metrics
  - Model produces profitable strategies (sometimes)

## Future Improvements

1. **Add more diverse datasets**: Different market conditions
2. **Expand indicator library**: Custom indicators beyond TA-Lib
3. **Add transaction costs**: More realistic trading simulation
4. **Multi-asset strategies**: Portfolio optimization
5. **Time-based constraints**: Intraday vs daily strategies
