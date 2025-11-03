"""
RL Task Runner with Custom Dataset
=================================
Run the RL task with a custom dataset URL or use the default sample dataset.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from run_trials import main as run_main


def download_dataset(url: str, filename: str = None) -> str:
    """Download dataset from URL and return the filepath"""
    try:
        import urllib.request
        import urllib.parse
        
        # Create data directory if it doesn't exist
        data_dir = Path("task/data")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            parsed_url = urllib.parse.urlparse(url)
            filename = Path(parsed_url.path).name
            if not filename or '.' not in filename:
                filename = "custom_dataset.csv"
        
        filepath = data_dir / filename
        
        print(f"📥 Downloading dataset from: {url}")
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ Dataset saved to: {filepath}")
        
        return str(filepath)
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        sys.exit(1)


def update_grader_for_custom_dataset(dataset_path: str, target_column: str):
    """Update the grader to use the custom dataset"""
    grader_path = Path("task/grader.py")
    
    # Read current grader
    with open(grader_path, 'r') as f:
        content = f.read()
    
    # Replace the hardcoded dataset path
    old_path = '"task/data/sample_dataset.csv"'
    new_path = f'"{dataset_path}"'
    
    # Replace the hardcoded target column
    old_target = '"target"'
    new_target = f'"{target_column}"'
    
    # Update the content
    updated_content = content.replace(old_path, new_path)
    updated_content = updated_content.replace(old_target, new_target)
    
    # Write back
    with open(grader_path, 'w') as f:
        f.write(updated_content)
    
    print(f"🔧 Updated grader to use dataset: {dataset_path} with target: {target_column}")


def restore_original_grader():
    """Restore the original grader settings"""
    grader_path = Path("task/grader.py")
    
    # Read current grader
    with open(grader_path, 'r') as f:
        content = f.read()
    
    # Restore original settings (this is a simple approach)
    # In a production system, you'd want to backup/restore properly
    import re
    
    # Replace any custom dataset path back to original
    content = re.sub(r'"task/data/[^"]*\.csv"', '"task/data/sample_dataset.csv"', content)
    content = re.sub(r'preprocess_func\(\s*"[^"]*",\s*"[^"]*"\s*\)', 
                    'preprocess_func(\n            "task/data/sample_dataset.csv", "target"\n        )', content)
    
    # Write back
    with open(grader_path, 'w') as f:
        f.write(content)


def update_prompt_for_custom_dataset(dataset_info: str):
    """Update the prompt to mention the custom dataset"""
    prompt_path = Path("task/prompt.txt")
    
    # Read current prompt
    with open(prompt_path, 'r') as f:
        content = f.read()
    
    # Add custom dataset info at the top
    custom_info = f"""
CUSTOM DATASET INFORMATION:
{dataset_info}

"""
    
    # Add the info after the first line
    lines = content.split('\n')
    lines.insert(1, custom_info)
    
    # Write back
    with open(prompt_path, 'w') as f:
        f.write('\n'.join(lines))


async def main():
    parser = argparse.ArgumentParser(description='Run RL task with custom or default dataset')
    parser.add_argument('--dataset-url', type=str, help='URL to download dataset from')
    parser.add_argument('--target-column', type=str, default='target', 
                       help='Name of the target column (default: target)')
    parser.add_argument('--filename', type=str, help='Filename to save dataset as')
    parser.add_argument('--trials', type=int, default=10, help='Number of trials to run')
    parser.add_argument('--concurrent', action='store_true', default=True, 
                       help='Run trials concurrently (default: True)')
    
    args = parser.parse_args()
    
    try:
        if args.dataset_url:
            # Download and use custom dataset
            print("🚀 Running RL Task with Custom Dataset")
            print("=" * 50)
            
            # Download the dataset
            dataset_path = download_dataset(args.dataset_url, args.filename)
            
            # Analyze the dataset
            try:
                import pandas as pd
                df = pd.read_csv(dataset_path)
                
                dataset_info = f"""Dataset: {dataset_path}
Rows: {len(df)}
Columns: {list(df.columns)}
Target Column: {args.target_column}
Missing Values: {df.isnull().sum().sum()}
Data Types: {df.dtypes.to_dict()}"""
                
                print("\n📊 Dataset Analysis:")
                print(dataset_info)
                
                # Validate target column exists
                if args.target_column not in df.columns:
                    print(f"❌ Error: Target column '{args.target_column}' not found in dataset")
                    print(f"Available columns: {list(df.columns)}")
                    sys.exit(1)
                
                # Update grader and prompt
                update_grader_for_custom_dataset(dataset_path, args.target_column)
                update_prompt_for_custom_dataset(dataset_info)
                
            except Exception as e:
                print(f"❌ Error analyzing dataset: {e}")
                sys.exit(1)
        else:
            # Use default dataset
            print("🚀 Running RL Task with Default Dataset")
            print("=" * 50)
            print("Using: task/data/sample_dataset.csv")
        
        # Update number of trials in run_trials.py if specified
        if args.trials != 10:
            print(f"🔧 Running {args.trials} trials")
        
        # Run the main evaluation
        await run_main(concurrent=args.concurrent)
        
    finally:
        # Always restore original grader settings
        if args.dataset_url:
            restore_original_grader()
            print("🔄 Restored original grader settings")


if __name__ == "__main__":
    asyncio.run(main())