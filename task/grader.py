import os
import pandas as pd
import numpy as np
import importlib.util
import sys
import traceback
from typing import Tuple, Dict, Any

def check_code_structure(module) -> Tuple[bool, str]:
    """Check for required function with minimal validation."""
    # Check for required function
    if not hasattr(module, 'predict_trade') or not callable(module.predict_trade):
        return False, "Function 'predict_trade' not found or is not callable."
    
    # Check function signature
    import inspect
    sig = inspect.signature(module.predict_trade)
    params = list(sig.parameters.values())
    
    # Verify function takes exactly one parameter
    if len(params) != 1:
        return False, "predict_trade must take exactly one parameter"
        
    return True, "Code structure validation passed"

def check_indicators_used(code: str) -> Tuple[bool, str]:
    """Check if the code uses at least one technical indicator in a meaningful way.
    
    Args:
        code: The source code to check
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Define indicators to look for (case insensitive)
    common_indicators = [
        'rsi', 'macd', 'ema', 'sma', 'bbands', 'atr', 'stoch', 'adx', 'cci', 'willr'
    ]
    
    # Check for indicator usage in code (case insensitive)
    code_lower = code.lower()
    
    # Look for any indicator usage
    used_indicators = [ind for ind in common_indicators 
                      if f"talib.{ind}" in code_lower or f" {ind}(" in code_lower]
    
    if not used_indicators:
        return False, "No technical indicators found. Use at least one indicator from TA-Lib."
        
    # Check if indicators are used in trading conditions
    has_conditions = any(op in code_lower for op in ['>', '<', '>=', '<=', '==', '!='])
    
    if not has_conditions:
        return False, "Indicators found but not used in any trading conditions"
        
    return True, f"Found indicators: {', '.join(used_indicators)}"

def check_metrics(metrics: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate that the returned metrics are reasonable and complete.
    
    Args:
        metrics: Dictionary of metrics to validate
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Required metrics with reasonable bounds
    required_metrics = {
        'cumulative_returns_final': (-1.0, 10.0),  # -100% to 1000%
        'sharpe_ratio': (-5.0, 10.0),              # Reasonable bounds
        'max_drawdown': (0.0, 1.0),                # 0% to 100%
    }
    
    # Check required metrics
    missing = []
    invalid = []
    
    for metric, (min_val, max_val) in required_metrics.items():
        if metric not in metrics:
            missing.append(metric)
            continue
            
        value = metrics[metric]
        if not isinstance(value, (int, float)) or not np.isfinite(value):
            invalid.append(f"{metric}: must be a finite number, got {value}")
        elif not (min_val <= value <= max_val):
            invalid.append(f"{metric}: must be between {min_val} and {max_val}, got {value:.4f}")
    
    # Compile results
    if missing:
        return False, f"Missing required metrics: {', '.join(missing)}"
    if invalid:
        return False, "Invalid metrics:\n- " + "\n- ".join(invalid)
    
    return True, "All metrics are valid"

def load_and_validate_data(dataset_path: str) -> pd.DataFrame:
    """Load and validate the input data."""
    try:
        # Read the CSV file with proper datetime parsing
        df = pd.read_csv(
            dataset_path,
            names=['day', 'timestamp', 'value'],
            parse_dates=['timestamp'],
            index_col='timestamp'
        )
        
        # Basic validation
        if len(df) < 10:
            print(f"⚠️ Warning: Very small dataset ({len(df)} rows). Results may be unreliable.")
            
        return df['value']  # Return just the value series
        
    except Exception as e:
        raise ValueError(f"Error loading data: {str(e)}")

def grade_submission(submitted_code: str, dataset_path: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Grade a trading strategy submission.
    
    The submission must implement a trading strategy that:
    1. Takes a dataset path and returns trading signals and metrics
    2. Uses at least one technical indicator from TA-Lib
    3. Returns valid performance metrics
    
    Args:
        submitted_code: Python code as string
        dataset_path: Path to the dataset file
        
    Returns:
        Tuple of (passed: bool, message: str, metrics: dict)
    """
    import tempfile
    import uuid
    
    # Create a unique temp file
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, f'solution_{uuid.uuid4().hex}.py')
    module_name = f'solution_{uuid.uuid4().hex}'
    
    try:
        # Save the submitted code to a temporary file
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(submitted_code)
        
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, temp_file)
        if spec is None or spec.loader is None:
            return False, "Failed to create module spec", {}
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            return False, f"Error loading module: {str(e)}", {}
        
        # Check for required function
        if not hasattr(module, 'predict_trade') or not callable(module.predict_trade):
            return False, "Function 'predict_trade' not found or not callable", {}
        
        # Check for indicator usage
        indicators_ok, indicators_msg = check_indicators_used(submitted_code)
        if not indicators_ok:
            return False, f"Indicator check failed: {indicators_msg}", {}
        
        # Execute the prediction
        try:
            result = module.predict_trade(dataset_path)
            
            # Validate result structure
            if not isinstance(result, dict):
                return False, "Return value must be a dictionary", {}
                
            if 'metrics' not in result:
                return False, "Missing 'metrics' in return value", {}
                
            if not isinstance(result['metrics'], dict):
                return False, "'metrics' must be a dictionary", {}
            
            # Validate metrics
            metrics_ok, metrics_msg = check_metrics(result['metrics'])
            if not metrics_ok:
                return False, f"Invalid metrics: {metrics_msg}", {}
            
            # Success criteria - calibrated for 10-40% success rate
            metrics = result['metrics']
            
            # Check if Sharpe ratio is positive and excellent quality (> 2.0 for top performance)
            sharpe = metrics.get('sharpe_ratio', -999)
            if sharpe <= 0:
                return False, f"Sharpe ratio must be positive (got {sharpe:.4f}). Strategy loses money or has no variance.", metrics
            if sharpe < 2.0:
                return False, f"Sharpe ratio too low (got {sharpe:.4f}). Strategy needs excellent risk-adjusted returns (minimum 2.0).", metrics
                
            # Check if max drawdown is very conservative (< 25%)
            max_dd = metrics.get('max_drawdown', 1.0)
            if max_dd > 0.25:
                return False, f"Max drawdown too high: {max_dd:.1%}. Strategy is too risky (maximum 25%).", metrics
            
            # Check cumulative returns are positive and meaningful (> 0.8%)
            cum_ret = metrics.get('cumulative_returns_final', -999)
            if cum_ret <= 0:
                return False, f"Strategy lost money: {cum_ret:.2%} cumulative return. Need positive returns.", metrics
            if cum_ret < 0.008:
                return False, f"Cumulative returns too low: {cum_ret:.2%}. Strategy needs at least 0.8% return.", metrics
            
            return True, "All checks passed!", metrics
            
        except Exception as e:
            return False, f"Error executing predict_trade: {str(e)}", {}
            
    except Exception as e:
        return False, f"Grading error: {str(e)}", {}
        
    finally:
        # Clean up temp files
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception:
            pass
            
        # Clean up module
        if 'module_name' in locals() and module_name in sys.modules:
            try:
                del sys.modules[module_name]
            except Exception:
                pass

if __name__ == '__main__':
    # Example usage
    with open('solution.py', 'r') as f:
        code = f.read()
    
    passed, msg, metrics = grade_submission(code, 'data/tick_data.csv')
    print(f"Passed: {passed}")
    print(f"Message: {msg}")
    if passed:
        print("Metrics:", metrics)
