# Algorithmic Trading Strategy Implementation Task

## 🚀 Project Overview

This project challenges AI models to implement a trading strategy using technical analysis. The model must process tick-level price data, calculate technical indicators, generate trading signals, and compute performance metrics.

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
   - `cumulative_returns_final`: Total return of the strategy
   - `sharpe_ratio`: Risk-adjusted return (≥ 1.0 to pass)
   - `max_drawdown`: Maximum peak-to-trough decline (< 40% to pass)
5. **Profitability**: Positive cumulative returns

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
  - Division by zero in Sharpe ratio calculation
  - Incorrect signal alignment with price data
  - Edge cases with small datasets
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
- OpenAI for the base models
- **`results/all_runs.json`**: Detailed results for every trial in every run are appended to this single file for a complete chronological record.
