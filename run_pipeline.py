import os
import re
import sys
import json
import asyncio
import warnings
from pathlib import Path
from typing import Dict, Any, List
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings('ignore')
import numpy as np
np.seterr(all='ignore')
import pandas as pd
pd.options.mode.chained_assignment = None

# Load environment variables
load_dotenv()

# Add task directory to path
sys.path.append(str(Path(__file__).parent / 'task'))
from task.grader import grade_submission

class TradingPipeline:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.results = []
        
    async def get_model_response(self, prompt: str) -> str:
        """Get response from the model."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an AI that generates trading strategies. Only respond with valid Python code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {str(e)}")
            return ""

    @staticmethod
    def clean_response(response: str) -> str:
        """Extract Python code from markdown response."""
        code_blocks = re.findall(r'```(?:python)?\s*(.*?)\s*```', response, re.DOTALL)
        return code_blocks[0].strip() if code_blocks else response

    async def evaluate_solution(self, code: str, trial_num: int) -> Dict[str, Any]:
        """Evaluate a solution using the grader."""
        try:
            # Save code to temp file
            os.makedirs('temp', exist_ok=True)
            temp_file = f'temp/temp_solution_{trial_num}.py'
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Grade the submission
            dataset_path = os.path.join('task', 'data', 'tick_data.csv')
            passed, message, metrics = await asyncio.to_thread(
                grade_submission, code, dataset_path
            )
            
            return {
                'trial': trial_num,
                'passed': passed,
                'error': None if passed else message,
                'metrics': metrics
            }
            
        except Exception as e:
            return {
                'trial': trial_num,
                'passed': False,
                'error': f"Evaluation error: {str(e)}",
                'metrics': {}
            }
            
    async def run_trial(self, trial_num: int, prompt: str) -> Dict[str, Any]:
        """Run a single trial with minimal output."""
        # Get model response
        response = await self.get_model_response(prompt)
        if not response:
            return {'trial': trial_num, 'error': 'Empty response from model', 'passed': False}
        
        # Clean response
        solution_code = self.clean_response(response)
        
        # Evaluate solution
        result = await self.evaluate_solution(solution_code, trial_num)
        
        # Print trial result
        status = "✅ PASSED" if result.get('passed') else f"❌ FAILED: {result.get('error', 'Unknown error')}"
        print(f"Trial {trial_num + 1}: {status}")
        
        # Save successful solutions
        if result.get('passed'):
            os.makedirs('solutions', exist_ok=True)
            with open(f'solutions/solution_{trial_num}.py', 'w') as f:
                f.write(solution_code)
        
        return result

    async def run(self, num_trials: int = 10):
        """Run the pipeline with clean output."""
        self.num_trials = num_trials
        self.results = []
        
        # Print initial stats
        print("\n" + "=" * 50)
        print("TRADING STRATEGY EVALUATION")
        print("=" * 50)
        
        # Load and show data stats
        try:
            data_path = os.path.join('task', 'data', 'tick_data.csv')
            # Read with header and proper column names
            df = pd.read_csv(data_path, names=['day', 'timestamp', 'value'], header=0)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate durations
            total_duration = df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]
            total_minutes = total_duration.total_seconds() / 60
            
            # Calculate split points
            train_size = int(len(df) * 0.8)
            train_duration = (df['timestamp'].iloc[train_size-1] - df['timestamp'].iloc[0]).total_seconds() / 60
            test_duration = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[train_size]).total_seconds() / 60
            
            print(f"\n📊 Dataset Stats:")
            print(f"- Total Rows: {len(df):,}")
            print(f"- First Timestamp: {df['timestamp'].iloc[0]}")
            print(f"- Last Timestamp: {df['timestamp'].iloc[-1]}")
            print(f"- Total Duration: {total_minutes:.2f} minutes")
            print(f"- Data Split (80/20):")
            print(f"  - Training: {train_duration:.2f} minutes ({train_size} rows)")
            print(f"  - Testing: {test_duration:.2f} minutes ({len(df)-train_size} rows)")
            print(f"- Unique Days: {df['day'].nunique()}")
            print(f"- Value Stats:")
            print(f"  - Min: {df['value'].min():.4f}")
            print(f"  - Max: {df['value'].max():.4f}")
            print(f"  - Mean: {df['value'].mean():.4f}")
            
        except Exception as e:
            print(f"\n⚠️ Could not load data stats: {str(e)}")
        
        # Load prompt
        try:
            prompt_path = os.path.join('task', 'prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read()
            print(f"\n🚀 Starting {num_trials} trials...\n")
        except Exception as e:
            print(f"\n❌ Error loading prompt: {str(e)}")
            return
        
        # Run trials
        tasks = [self.run_trial(i, prompt) for i in range(num_trials)]
        self.results = await asyncio.gather(*tasks)
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print clean summary of all trials."""
        passed = sum(1 for r in self.results if r.get('passed'))
        total = len(self.results)
        accuracy = passed / total * 100 if total > 0 else 0
        
        # Print final result
        print("\n" + "=" * 50)
        print(f"FINAL RESULTS")
        print("=" * 50)
        print(f"Total Trials: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"🎯 Accuracy: {accuracy:.1f}%")
        
        # Print any unique errors
        if passed < total:
            print("\nFailure Reasons:")
            errors = {}
            for r in self.results:
                if not r.get('passed') and 'error' in r:
                    errors[r['error']] = errors.get(r['error'], 0) + 1
            
            for error, count in errors.items():
                print(f"- {error} (x{count})")
        
        print("=" * 50)
        
        # Save results to JSON
        os.makedirs('results', exist_ok=True)
        with open('results/evaluation_results.json', 'w') as f:
            json.dump({
                'timestamp': pd.Timestamp.now().isoformat(),
                'total_trials': len(self.results),
                'passed': sum(1 for r in self.results if r.get('passed')),
                'results': [{
                    'trial': r.get('trial'),
                    'passed': r.get('passed'),
                    'error': r.get('error'),
                    'metrics': r.get('metrics')
                } for r in self.results]
            }, f, indent=2)

def main():
    # Clean up old files
    for f in Path('solutions').glob('solution_*.py'):
        f.unlink()
    
    pipeline = TradingPipeline()
    asyncio.run(pipeline.run())
    pipeline.print_summary()
    return pipeline

if __name__ == "__main__":
    main()
