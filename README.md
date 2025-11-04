# Algorithmic Trading Strategy Implementation Task

## 🚀 Project Overview

This project challenges AI models to implement a trading strategy using technical analysis. The model must process tick-level price data, calculate technical indicators, generate trading signals, and compute performance metrics.
<img width="1536" height="632" alt="image" src="https://github.com/user-attachments/assets/e0eea607-2482-4c24-93ec-0764e6be70ec" />
<img width="1582" height="508" alt="image" src="https://github.com/user-attachments/assets/dc063dfd-d2d3-4813-be8a-7ce161a4e3f0" />


## 📈 Task Description

### The Challenge
Implement a function called `predict_trade` that takes a CSV file path as input and returns a dictionary with trading signals and performance metrics. The function should:

1. Load and preprocess tick data
2. Calculate technical indicators (RSI, MACD, EMA, etc.)
3. Generate trading signals based on indicator conditions
4. Calculate performance metrics (Sharpe ratio, max drawdown, cumulative returns)

### Learning Objectives
- **Financial time series processing**: Resampling tick data to OHLC bars
- **Technical analysis**: Using TA-Lib indicators for trading decisions
- **Performance evaluation**: Calculating risk-adjusted returns
- **Array manipulation**: Handling edge cases and data alignment
- **Domain-specific constraints**: Understanding trading logic and risk management

## 🛠️ Project Structure

```
.
├── task/
│   ├── prompt.txt          # Detailed task instructions and requirements
│   ├── grader.py           # Evaluation logic and success criteria
│   └── data/
│       └── tick_data.csv   # Sample tick data for testing
├── run_pipeline.py         # Main script to run evaluations
├── auto_pipeline.py        # Automated prompt improvement script
└── README.md               # This file
```

## 🎯 Success Criteria

A solution must pass all these requirements:

1. **Function Signature**: Implement `predict_trade(data_path: str) -> dict`
2. **Indicator Usage**: Use at least one TA-Lib indicator
3. **Return Structure**: Return dict with 'signals' and 'metrics' keys
4. **Metrics Required**:
   - `cumulative_returns_final`: Total return of the strategy (≥ 0.8%)
   - `sharpe_ratio`: Risk-adjusted return (≥ 2.0 to pass)
   - `max_drawdown`: Maximum peak-to-trough decline (< 25% to pass)
5. **Profitability**: Meaningful positive cumulative returns

## 🚦 How to Run

### Prerequisites
- Python 3.8+
- Required packages: `pandas`, `numpy`, `talib`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/govinda-vurjana/Algorithmic-Trading-based-on-RL-.git
   cd Algorithmic-Trading-based-on-RL-
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Note: For TA-Lib, you might need to install system dependencies first:
   - **Windows**: Download pre-built binary from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
   - **macOS**: `brew install ta-lib`
   - **Linux**: `sudo apt-get install python3-ta-lib`

3. Configure API Key:
   
   Create a `.env` file in the project root (or copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your Anthropic API key:
   ```bash
   ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key-here"
   ```
   
   **Model Used:**
   - Anthropic: `claude-sonnet-4-20250514`
   
   📖 For detailed API setup instructions, see [API_SETUP.md](API_SETUP.md)

### Running Evaluations

#### Single Run
```bash
python run_pipeline.py
```

#### Multiple Trials
```bash
python run_pipeline.py --trials 10
```

#### Auto-Improvement Mode
```bash
python auto_pipeline.py --auto --attempts 10 --target 0.3
```

## 📊 Expected Output

Successful solutions will produce output similar to:

```python
{
    'signals': array([0, 1, -1, ...]),  # Trading signals: -1 (sell), 0 (hold), 1 (buy)
    'metrics': {
        'cumulative_returns_final': 0.15,  # 15% total return
        'sharpe_ratio': 1.2,              # Risk-adjusted return
        'max_drawdown': 0.25               # 25% maximum drawdown
    }
}
```

## 🎓 Learning Outcomes

This task teaches:
1. **Financial Data Processing**
   - Handling high-frequency tick data
   - Resampling to OHLC format
   - Managing missing values and edge cases

2. **Technical Analysis**
   - Implementing common indicators (RSI, MACD, EMA)
   - Signal generation and validation
   - Risk management techniques

3. **Performance Metrics**
   - Calculating risk-adjusted returns
   - Measuring drawdowns
   - Evaluating strategy performance

## 🤖 Model Performance

- **Target Success Rate**: 10-40%
- **Common Failure Modes**:
  - Sharpe ratio of 0.0 - strategy not generating enough trades
  - Low Sharpe ratio (< 2.0) - insufficient risk-adjusted returns
  - High max drawdown (> 25%) - too risky
  - Low cumulative returns (< 0.8%) - not profitable enough
  - Division by zero in Sharpe ratio calculation
  - Incorrect signal alignment with price data
  - Invalid indicator parameters

## 📚 Resources

- [TA-Lib Documentation](https://mrjbq7.github.io/ta-lib/)
- [QuantConnect Tutorials](https://www.quantconnect.com/learn)
- [Backtrader Documentation](https://www.backtrader.com/docu/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- TA-Lib contributors
- The Quant Finance community
- Anthropic for Claude models
