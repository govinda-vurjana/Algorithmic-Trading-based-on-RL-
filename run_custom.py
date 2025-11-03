"""
Simple Custom Dataset Runner
===========================
Easy way to run the RL task with a custom dataset.
"""

import asyncio
import sys
from run_with_dataset import main as run_with_dataset_main


async def interactive_run():
    """Interactive mode to get dataset URL from user"""
    
    print("🤖 RL Task - Custom Dataset Runner")
    print("=" * 40)
    
    # Ask user for dataset choice
    print("\nChoose an option:")
    print("1. Use default sample dataset")
    print("2. Download dataset from URL")
    print("3. Use existing file in task/data/")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Use default dataset
        print("\n🚀 Using default sample dataset...")
        from run_trials import main as run_default
        await run_default(concurrent=True)
        
    elif choice == "2":
        # Get URL from user
        url = input("\nEnter dataset URL: ").strip()
        if not url:
            print("❌ No URL provided")
            return
            
        target_column = input("Enter target column name (default: 'target'): ").strip()
        if not target_column:
            target_column = "target"
            
        filename = input("Enter filename to save as (optional): ").strip()
        
        # Set up arguments and run
        sys.argv = ["run_custom.py", "--dataset-url", url, "--target-column", target_column]
        if filename:
            sys.argv.extend(["--filename", filename])
            
        await run_with_dataset_main()
        
    elif choice == "3":
        # List existing files
        import os
        data_dir = "task/data"
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if files:
                print(f"\nAvailable files in {data_dir}:")
                for i, file in enumerate(files, 1):
                    print(f"{i}. {file}")
                
                try:
                    file_choice = int(input(f"\nChoose file (1-{len(files)}): ")) - 1
                    if 0 <= file_choice < len(files):
                        selected_file = files[file_choice]
                        target_column = input("Enter target column name (default: 'target'): ").strip()
                        if not target_column:
                            target_column = "target"
                        
                        # Update grader to use selected file
                        from run_with_dataset import update_grader_for_custom_dataset, restore_original_grader
                        try:
                            dataset_path = f"task/data/{selected_file}"
                            update_grader_for_custom_dataset(dataset_path, target_column)
                            from run_trials import main as run_default
                            await run_default(concurrent=True)
                        finally:
                            restore_original_grader()
                    else:
                        print("❌ Invalid choice")
                except ValueError:
                    print("❌ Invalid input")
            else:
                print(f"❌ No CSV files found in {data_dir}")
        else:
            print(f"❌ Directory {data_dir} not found")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(interactive_run())