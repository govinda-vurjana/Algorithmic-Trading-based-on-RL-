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

   The `run_trials.py` script is the single entrypoint for running evaluations.

   **Default Dataset**

   To run the evaluation with the default local dataset (`task/data/sample_dataset.csv`):
   ```bash
   uv run run_trials.py
   ```

   **Custom Dataset**

   You can specify a custom dataset using command-line arguments. The script can be pointed to any local CSV file.
   ```bash
   uv run run_trials.py --dataset-path "path/to/your/data.csv" --target-column "your_target_column_name"
   ```

## Execution Modes

You can control the execution mode with command-line flags:

- **Concurrent (Default)**: Runs trials in parallel for speed.
  ```bash
  uv run run_trials.py
  ```
- **Sequential**: Runs trials one by one. Useful for debugging.
  ```bash
  uv run run_trials.py --no-concurrent
  ```

## Logging

- **`results/pass_rate.txt`**: A summary of each run, including the data source and pass rate, is appended here.
- **`results/all_runs.json`**: Detailed results for every trial in every run are appended to this single file for a complete chronological record.

## Example Log Output (`results/pass_rate.txt`)

```
--- 2025-11-04 03:09:38 ---
Dataset: task/data/sample_dataset.csv
Pass Rate: 40.0%
Target Range: 10-40%
Status: ✓ GOOD

--- 2025-11-04 03:12:46 ---
Dataset: data/sample.csv
Pass Rate: 20.0%
Target Range: 10-40%
Status: ✓ GOOD

```
