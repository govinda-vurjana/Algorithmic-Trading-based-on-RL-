# Dataset Examples

Here are some example datasets you can use with the RL task:

## Public Dataset URLs

### 1. Titanic Dataset
```bash
uv run run_with_dataset.py --dataset-url "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv" --target-column "Survived"
```
- **Features**: Passenger info (age, class, fare, etc.)
- **Target**: Survival (0/1)
- **Challenge**: Missing values, categorical encoding

### 2. Wine Quality Dataset  
```bash
uv run run_with_dataset.py --dataset-url "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv" --target-column "quality"
```
- **Features**: Chemical properties
- **Target**: Quality score (3-8)
- **Challenge**: Multi-class classification

### 3. Boston Housing Dataset
```bash
uv run run_with_dataset.py --dataset-url "https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv" --target-column "medv"
```
- **Features**: Housing characteristics
- **Target**: Median home value
- **Challenge**: Regression task

## Interactive Mode Examples

```bash
# Run interactive mode
uv run run_custom.py

# Choose option 2 (Download from URL)
# Enter URL: https://example.com/your-dataset.csv
# Enter target column: your_target_column
# Enter filename: my_dataset.csv
```

## Custom Dataset Requirements

Your dataset should:
- ✅ Be in CSV format
- ✅ Have a clear target column
- ✅ Contain mixed data types (numeric + categorical)
- ✅ Have some missing values (makes task more realistic)
- ✅ Be reasonably sized (10-1000 rows work well)

## What the AI Will Learn

With any dataset, the AI learns to:
1. **Analyze data structure** (dtypes, missing values, distributions)
2. **Handle missing values** appropriately for each column type
3. **Encode categorical variables** using OneHotEncoder
4. **Prevent data leakage** by splitting before preprocessing
5. **Normalize features** using StandardScaler
6. **Preserve target distribution** with stratified sampling
7. **Validate outputs** for missing/infinite values
8. **Write robust code** with proper error handling

The grader automatically adapts to your dataset size and structure!