"""
Grading Logic
=============
Evaluates whether the submitted solution meets all requirements.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


def grade_submission(
    submitted_code,
    dataset_path="task/data/sample_dataset.csv",
    target_column="target",
):
    """
    Grade the submitted preprocessing function.
    
    Args:
        submitted_code: String containing the preprocessing function
        dataset_path: Path to the dataset to use for grading
        target_column: Name of the target column in the dataset
        
    Returns:
        tuple: (is_correct, feedback_message, detailed_results)
    """
    
    results = {
        "total_requirements": 8,
        "passed_requirements": 0,
        "failed_requirements": [],
        "detailed_feedback": []
    }
    
    try:
        # Clean the submitted code (remove markdown code blocks if present)
        code_to_exec = submitted_code
        if "```python" in code_to_exec:
            # Extract code from markdown blocks
            import re
            code_blocks = re.findall(r'```python\n(.*?)\n```', code_to_exec, re.DOTALL)
            if code_blocks:
                code_to_exec = code_blocks[0]
        elif "```" in code_to_exec:
            # Handle generic code blocks
            import re
            code_blocks = re.findall(r'```\n(.*?)\n```', code_to_exec, re.DOTALL)
            if code_blocks:
                code_to_exec = code_blocks[0]
        
        # Execute the submitted function with warnings suppressed
        import warnings
        warnings.filterwarnings('ignore', category=FutureWarning)
        
        exec_globals = {
            'pd': pd, 'np': np, 'train_test_split': train_test_split,
            'StandardScaler': StandardScaler, 'OneHotEncoder': OneHotEncoder,
            'SimpleImputer': SimpleImputer, 'ColumnTransformer': ColumnTransformer,
            'Pipeline': Pipeline, 'warnings': warnings
        }
        exec(code_to_exec, exec_globals)
        
        if 'preprocess_data' not in exec_globals:
            return False, "Function 'preprocess_data' not found", results
        
        preprocess_func = exec_globals['preprocess_data']
        
        # Test the function with the specified dataset
        try:
            X_train, X_test, y_train, y_test = preprocess_func(
                dataset_path, target_column
            )
        except Exception as e:
            return False, f"Error calling preprocess_data function: {str(e)}", results
        
        # Validate that we got the expected outputs
        if X_train is None or X_test is None or y_train is None or y_test is None:
            return False, "Function returned None values", results
        
        # Requirement 1: No missing values in output
        train_missing = _count_missing(X_train)
        test_missing = _count_missing(X_test)
        
        if train_missing == 0 and test_missing == 0:
            results["passed_requirements"] += 1
            results["detailed_feedback"].append("✓ No missing values in output")
        else:
            results["failed_requirements"].append("Output contains missing values")
            results["detailed_feedback"].append(f"✗ Missing values: train={train_missing}, test={test_missing}")
        
        # Requirement 2: No infinite values
        train_inf = _count_infinite(X_train)
        test_inf = _count_infinite(X_test)
        
        if train_inf == 0 and test_inf == 0:
            results["passed_requirements"] += 1
            results["detailed_feedback"].append("✓ No infinite values in output")
        else:
            results["failed_requirements"].append("Output contains infinite values")
            results["detailed_feedback"].append(f"✗ Infinite values: train={train_inf}, test={test_inf}")
        
        # Requirement 3: Proper train/test split sizes
        original_df = pd.read_csv(dataset_path)
        total_samples = len(original_df)
        expected_test_size = int(0.2 * total_samples)
        actual_test_size = len(X_test)
        
        # Allow for slight variation in split size
        if abs(actual_test_size - expected_test_size) <= 1:
            results["passed_requirements"] += 1
            results["detailed_feedback"].append("✓ Correct train/test split ratio")
        else:
            results["failed_requirements"].append("Incorrect train/test split ratio")
            results["detailed_feedback"].append(f"✗ Test size: expected ~{expected_test_size}, got {actual_test_size}")

        # Requirement 4: All features are numeric (proper categorical encoding)
        if hasattr(X_train, 'select_dtypes'):
            train_numeric = X_train.select_dtypes(include=[np.number]).shape[1]
            test_numeric = X_test.select_dtypes(include=[np.number]).shape[1]
            all_numeric = (train_numeric == X_train.shape[1] and test_numeric == X_test.shape[1])
        else:
            # For numpy arrays, check if dtype is numeric
            all_numeric = X_train.dtype.kind in 'biufc' and X_test.dtype.kind in 'biufc'
        
        if all_numeric:
            results["passed_requirements"] += 1
            results["detailed_feedback"].append("✓ All features properly encoded as numeric")
        else:
            results["failed_requirements"].append("Non-numeric features found")
            results["detailed_feedback"].append("✗ Non-numeric columns in output")
        
        # Requirement 5: Features are normalized/standardized
        if hasattr(X_train, 'std'):
            train_stds = X_train.std()
            normalized_features = (train_stds > 0.8) & (train_stds < 1.2)
            normalized_count = normalized_features.sum()
            total_features = len(train_stds)
        else:
            # For numpy arrays
            train_stds = np.std(X_train, axis=0)
            normalized_features = (train_stds > 0.8) & (train_stds < 1.2)
            normalized_count = normalized_features.sum()
            total_features = len(train_stds)
        
        # --- UPDATED REQUIREMENT 5 CHECK ---
        uses_standard_scaler = "StandardScaler" in submitted_code

        if normalized_count >= total_features * 0.6 and uses_standard_scaler:
            results["passed_requirements"] += 1
            results["detailed_feedback"].append("✓ Features appear normalized and StandardScaler used")
        elif normalized_count >= total_features * 0.6:
            results["passed_requirements"] += 1
            results["detailed_feedback"].append("✓ Features appear normalized (statistical check passed)")
        else:
            results["failed_requirements"].append("Features not properly normalized")
            results["detailed_feedback"].append(f"✗ Only {normalized_count}/{total_features} features normalized")
        # --- END UPDATED REQUIREMENT 5 CHECK ---
        
        # Requirement 6: No data leakage (proper fit/transform usage)
        # Check if the code suggests proper handling
        # --- UPDATED REQUIREMENT 6 CHECK ---
        if ("fit_transform" in submitted_code and "transform" in submitted_code) or \
           ("fit(" in submitted_code and "transform(" in submitted_code) or \
           ("Pipeline(" in submitted_code and "ColumnTransformer" in submitted_code):
            results["passed_requirements"] += 1
            results["detailed_feedback"].append("✓ Code suggests proper fit/transform usage or pipeline construction")
        else:
            results["failed_requirements"].append("Potential data leakage in normalization")
            results["detailed_feedback"].append("✗ Should use fit_transform on train, transform on test, or proper Pipeline structure")
        # --- END UPDATED REQUIREMENT 6 CHECK ---

        # Requirement 7: Categorical variables handled properly
        # Check if output has more features than input (suggesting one-hot encoding)
        original_features = original_df.drop(columns=[target_column]).shape[1]
        
        if X_train.shape[1] >= original_features:
            results["passed_requirements"] += 1
            results["detailed_feedback"].append("✓ Categorical variables handled (feature count increased)")
        else:
            results["failed_requirements"].append("Categorical variables not properly handled")
            results["detailed_feedback"].append(f"✗ Feature count decreased: {original_features} -> {X_train.shape[1]}")
        
        # Requirement 8: Target distribution preserved (stratified sampling)
        # Check if target distribution is preserved
        original_target_dist = original_df[target_column].value_counts(normalize=True).sort_index()
        train_target_dist = pd.Series(y_train).value_counts(normalize=True).sort_index()
        
        # --- UPDATED REQUIREMENT 8 CHECK ---
        uses_stratify = "stratify" in submitted_code

        # Ensure both series have the same index
        common_classes = original_target_dist.index.intersection(train_target_dist.index)
        if len(common_classes) > 0:
            dist_diff = abs(original_target_dist[common_classes] - train_target_dist[common_classes]).max()
            
            if dist_diff < 0.25 and uses_stratify: 
                results["passed_requirements"] += 1
                results["detailed_feedback"].append("✓ Target distribution preserved (stratify used and check passed)")
            elif dist_diff < 0.25:
                # If the distribution is preserved by chance (less likely with small samples)
                results["failed_requirements"].append("Missing 'stratify' argument in code")
                results["detailed_feedback"].append(f"✗ Distribution preserved but 'stratify' argument not found in code. Diff: {dist_diff:.3f}")
            else:
                results["failed_requirements"].append("Target distribution not preserved")
                results["detailed_feedback"].append(f"✗ Target distribution difference: {dist_diff:.3f}")
        else:
            results["failed_requirements"].append("Target distribution check failed")
            results["detailed_feedback"].append("✗ Could not verify target distribution")
        # --- END UPDATED REQUIREMENT 8 CHECK ---
        
        # Success criteria: Need at least 4/8 requirements for a good solution
        success = results["passed_requirements"] >= 4
        
        if success:
            feedback = f"Passed {results['passed_requirements']}/8 requirements - Good job!"
        else:
            feedback = f"Passed only {results['passed_requirements']}/8 requirements - Needs improvement"
        
        return success, feedback, results
        
    except Exception as e:
        return False, f"Error executing preprocessing function: {str(e)}", results


def _count_missing(data):
    """Count missing values in data (works with both pandas and numpy)"""
    if hasattr(data, 'isnull'):
        return data.isnull().sum().sum()
    else:
        return np.isnan(data).sum() if data.dtype.kind in 'fc' else 0


def _count_infinite(data):
    """Count infinite values in data (works with both pandas and numpy)"""
    if hasattr(data, 'select_dtypes'):
        return np.isinf(data.select_dtypes(include=[np.number])).sum().sum()
    else:
        return np.isinf(data).sum() if data.dtype.kind in 'fc' else 0