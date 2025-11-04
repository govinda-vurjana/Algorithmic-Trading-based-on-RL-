import os
import sys
import json
import argparse
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Import the existing pipeline components
sys.path.append(str(Path(__file__).parent))
from run_pipeline import main as run_pipeline  # Import main function from run_pipeline

def load_prompt(prompt_path: str) -> str:
    """Load the prompt template from file."""
    with open(prompt_path, 'r') as f:
        return f.read()

def save_prompt(prompt_path: str, content: str) -> None:
    """Save the updated prompt to file."""
    with open(prompt_path, 'w') as f:
        f.write(content)

def extract_failure_reasons(output: str) -> List[str]:
    """Extract failure reasons from the pipeline output."""
    failure_reasons = []
    
    # Look for lines that contain failure information
    for line in output.split('\n'):
        line = line.strip()
        # Match both the trial failure line and the error message that follows
        if 'FAILED:' in line:
            # Extract the error message part after 'FAILED:'
            error_msg = line.split('FAILED:', 1)[1].strip()
            # Clean up any trailing emojis or special characters
            error_msg = error_msg.replace('❌', '').strip()
            if error_msg and error_msg != 'Unknown error' and error_msg not in failure_reasons:
                failure_reasons.append(error_msg)
    
    # If no explicit failure reasons found, try to extract from error messages
    if not failure_reasons:
        error_keywords = ['Error:', 'Exception:', 'Traceback', 'failed with error']
        error_lines = [
            line.strip() for line in output.split('\n')
            if any(keyword in line for keyword in error_keywords)
        ]
        if error_lines:
            failure_reasons.extend(error_lines[:3])  # Take first 3 error lines max
    
    # If still no reasons found, check for common issues in the output
    if not failure_reasons:
        if 'No module named' in output:
            failure_reasons.append('Missing required Python module')
        elif 'SyntaxError' in output:
            failure_reasons.append('Syntax error in generated code')
        elif 'NameError' in output:
            failure_reasons.append('Undefined variable or function')
        elif 'TypeError' in output:
            failure_reasons.append('Type error in the code')
    
    # If we still don't have any reasons, add a generic one
    if not failure_reasons and 'failed' in output.lower():
        failure_reasons.append('Unknown error - check the full output for details')
    
    return failure_reasons

def generate_improved_prompt(current_prompt: str, failure_reasons: List[str], attempt: int) -> str:
    """Generate an improved prompt based on failure reasons with specific guidance."""
    if not failure_reasons:
        return current_prompt
    
    # Add a section for error analysis and guidance
    error_guidance = "\n\n## Error Analysis and Guidance\n"
    error_guidance += f"This is attempt {attempt + 1}. Here are the issues from previous attempts:\n"
    
    # Add each failure reason with a counter
    for i, reason in enumerate(failure_reasons, 1):
        error_guidance += f"{i}. {reason}\n"
    
    # Add specific guidance for common error patterns
    if any("sharpe_ratio" in str(reason).lower() for reason in failure_reasons):
        error_guidance += "\nIMPORTANT: To fix Sharpe ratio issues:\n"
        error_guidance += "- Ensure you're not dividing by zero in Sharpe ratio calculation\n"
        error_guidance += "- Make sure you have enough data points to calculate returns\n"
        error_guidance += "- Check that your returns have enough variability (not all zeros)\n"
    
    if any("profit_factor" in str(reason).lower() for reason in failure_reasons):
        error_guidance += "\nIMPORTANT: To fix profit factor calculation:\n"
        error_guidance += "- Calculate as (total profit / total loss)\n"
        error_guidance += "- Handle the case where total loss is zero\n"
        error_guidance += "- Ensure you're aggregating profits and losses correctly\n"
    
    if any("broadcast" in str(reason).lower() for reason in failure_reasons):
        error_guidance += "\nIMPORTANT: To fix array shape/broadcast errors:\n"
        error_guidance += "- Check that all arrays have compatible shapes before operations\n"
        error_guidance += "- Verify the lengths of your signals and price arrays match\n"
        error_guidance += "- Use numpy's reshape() or np.newaxis if needed to align dimensions\n"
    
    if any("missing" in str(reason).lower() or "not found" in str(reason).lower() for reason in failure_reasons):
        error_guidance += "\nIMPORTANT: To fix missing components:\n"
        error_guidance += "- Ensure all required imports are included at the top of the file\n"
        error_guidance += "- Check that all variable names are defined before use\n"
        error_guidance += "- Verify that all required functions are implemented\n"
    
    # Add general debugging tips
    error_guidance += "\nGENERAL DEBUGGING TIPS:\n"
    error_guidance += "1. Add print statements to debug variable values and shapes\n"
    error_guidance += "2. Verify your data loading and preprocessing steps\n"
    error_guidance += "3. Check for off-by-one errors in array indexing\n"
    error_guidance += "4. Ensure all required indicators are properly calculated\n"
    
    # Insert the error guidance just before the implementation template
    if "## Implementation Template" in current_prompt:
        parts = current_prompt.split("## Implementation Template")
        return parts[0] + error_guidance + "## Implementation Template" + parts[1]
    
    return current_prompt + error_guidance

async def run_pipeline_with_retry() -> Tuple[float, str]:
    """Run the pipeline and handle retries with proper cleanup."""
    from run_pipeline import TradingPipeline
    
    try:
        # Create and run the pipeline
        pipeline = TradingPipeline()
        await pipeline.run()  # This populates pipeline.results
        
        # Calculate accuracy
        passed = sum(1 for r in pipeline.results if r.get('passed', False))
        total = len(pipeline.results) if pipeline.results else 1
        accuracy = passed / total if total > 0 else 0.0
        
        # Generate output with trial results
        output_lines = []
        for i, result in enumerate(pipeline.results):
            status = "✅ PASSED" if result.get('passed') else f"❌ FAILED: {result.get('error', 'Unknown error')}"
            output_lines.append(f"Trial {i+1}: {status}")
        
        # Add summary
        output = "\n".join(output_lines)
        output += f"\n\n📊 Trial Results: {passed}/{total} passed ({accuracy*100:.1f}%)"
        
        # Print trial results
        print("\n" + "="*50)
        print("TRIAL RESULTS")
        print("="*50)
        print(output)
        print("="*50 + "\n")
        
        return accuracy, output
        
    except Exception as e:
        error_msg = f"Error in pipeline: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return 0.0, error_msg

def run_auto_pipeline(prompt_path: str, max_attempts: int = 10, target_accuracy: float = 0.3) -> tuple[bool, float]:
    """Run the pipeline with automatic prompt improvement."""
    original_prompt = load_prompt(prompt_path)
    current_prompt = original_prompt
    best_accuracy = 0.0
    best_prompt = original_prompt
    
    for attempt in range(max_attempts):
        print(f"\n🔍 Attempt {attempt + 1}/{max_attempts}")
        print("-" * 50)
        
        # Update the prompt file
        save_prompt(prompt_path, current_prompt)
        
        # Run the pipeline and capture output
        from io import StringIO
        from contextlib import redirect_stdout
        
        f = StringIO()
        with redirect_stdout(f):
            try:
                accuracy, trial_output = asyncio.run(run_pipeline_with_retry())
                output = f.getvalue() + "\n" + trial_output
            except Exception as e:
                print(f"Error running pipeline: {str(e)}")
                output = f.getvalue()
                accuracy = 0.0
        
        # Update best prompt if current accuracy is better
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_prompt = current_prompt
            
            # Save the best solution
            with open('best_solution.py', 'w') as f:
                f.write(open('solution.py').read())
        
        # Check if we've reached the target accuracy
        if accuracy >= target_accuracy:
            print(f"\n🎉 Target accuracy of {target_accuracy*100}% achieved!")
            return True, best_accuracy
        
        # If not, analyze failures and improve the prompt
        failure_reasons = extract_failure_reasons(output)
        if not failure_reasons and accuracy > 0:
            print("No specific failures detected, but accuracy is still below target.")
            failure_reasons = [f"Accuracy {accuracy*100:.1f}% below target {target_accuracy*100}%"]
        
        if not failure_reasons:
            print("No failure reasons found. Please check the pipeline output.")
            failure_reasons = ["Unknown error"]
            
        print(f"\n📊 Attempt {attempt + 1} Results:")
        print(f"- Accuracy: {accuracy*100:.1f}% (Target: {target_accuracy*100}%)")
        print("\n❌ Failures detected:")
        for reason in failure_reasons:
            print(f"  - {reason}")
            
        # Generate improved prompt for next attempt
        current_prompt = generate_improved_prompt(original_prompt, failure_reasons, attempt)
    
    # If we get here, we didn't reach the target accuracy
    print(f"\n❌ Failed to reach target accuracy of {target_accuracy*100}% after {max_attempts} attempts.")
    print(f"Best accuracy achieved: {best_accuracy*100:.1f}%")
    
    # Restore the best prompt
    save_prompt(prompt_path, best_prompt)
    print(f"\nRestored best performing prompt (accuracy: {best_accuracy*100:.1f}%)")
    
    return False, best_accuracy

def main():
    parser = argparse.ArgumentParser(description='Run the trading strategy pipeline with auto-prompting.')
    parser.add_argument('--auto', action='store_true', 
                       help='Enable auto-prompting to improve the prompt based on failures')
    parser.add_argument('--attempts', type=int, default=10,
                       help='Maximum number of auto-prompting attempts')
    parser.add_argument('--target', type=float, default=0.3,
                       help='Target accuracy (0-1) to achieve')
    
    args = parser.parse_args()
    
    prompt_path = os.path.join('task', 'prompt.txt')
    
    # Ensure the solutions directory exists
    os.makedirs('solutions', exist_ok=True)
    
    if args.auto:
        # Initialize best_accuracy at the start
        best_accuracy = 0.0
        try:
            # Get the best accuracy from run_auto_pipeline
            success, best_accuracy = run_auto_pipeline(prompt_path, args.attempts, args.target)
            if success:
                print("\n✅ Successfully reached target accuracy!")
                print(f"Best solution saved to: best_solution.py")
                return 0
            else:
                print(f"\n❌ Failed to reach target accuracy of {args.target*100}% after {args.attempts} attempts.")
                if os.path.exists('best_solution.py'):
                    print(f"Best solution ({best_accuracy*100:.1f}% accuracy) saved to: best_solution.py")
                return 1
        except KeyboardInterrupt:
            print("\n🚫 Auto-prompting was interrupted by user.")
            if os.path.exists('best_solution.py'):
                # Read the best accuracy from the solution file if available
                try:
                    with open('best_solution.py', 'r') as f:
                        first_line = f.readline()
                        if 'Accuracy:' in first_line:
                            best_accuracy = float(first_line.split(':')[-1].strip().rstrip('%')) / 100.0
                except:
                    pass
                print(f"Best solution so far ({best_accuracy*100:.1f}% accuracy) saved to: best_solution.py")
            return 1
    else:
        # Just run the pipeline once without modifications
        print("Running single pipeline execution...")
        try:
            accuracy, _ = asyncio.run(run_pipeline_with_retry())
            if accuracy > 0:
                with open('solution.py', 'r') as f:
                    with open('best_solution.py', 'w') as out_f:
                        out_f.write(f"# Accuracy: {accuracy*100:.1f}%\n{f.read()}")
                print(f"\n✅ Solution saved to: best_solution.py (Accuracy: {accuracy*100:.1f}%)")
            return 0
        except Exception as e:
            print(f"Error running pipeline: {str(e)}")
            return 1

if __name__ == '__main__':
    main()
