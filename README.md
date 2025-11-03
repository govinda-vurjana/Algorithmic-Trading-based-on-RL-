RL Task for LLM Training
===

Simple framework for creating and testing RL tasks for LLM training.

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/preferencemodel/hello-py.git
   ```

2. Navigate to the project directory:
   ```
   cd hello-py
   ```

3. Set up API keys in `.env` file:
   ```
   ANTHROPIC_API_KEY=your_anthropic_key_here
   OPENAI_API_KEY=your_openai_key_here
   API_PROVIDER=openai
   ```

4. Run the task evaluation:
   ```
   # Default dataset
   uv run run_trials.py
   
   # Custom dataset from URL
   uv run run_with_dataset.py --dataset-url "https://example.com/data.csv" --target-column "target"
   
   # Interactive mode
   uv run run_custom.py
   ```



## Current Task: Data Preprocessing Pipeline Fix

Challenges models to fix bugs in a data preprocessing pipeline, teaching:
- Data leakage prevention
- Proper missing value handling  
- Categorical encoding best practices
- Input/output validation

## Dataset Options

### Default Dataset
- **File**: `task/data/sample_dataset.csv`
- **Size**: 25 rows × 8 columns
- **Features**: Mixed data types with missing values
- **Target**: Binary classification (0/1)

### Custom Datasets
- **Download from URL**: Use any CSV dataset from the internet
- **Local files**: Use existing files in `task/data/`
- **Flexible targets**: Specify any column as target

## Target Success Rate

Aim for 10-40% pass rate for effective RL training.

## Execution Modes

Edit `concurrent` parameter in `run_trials.py`:

```python
asyncio.run(main(concurrent=True))   # Faster
asyncio.run(main(concurrent=False))  # Sequential
```
