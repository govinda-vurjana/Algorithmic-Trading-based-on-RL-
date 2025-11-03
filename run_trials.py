"""
RL Task Evaluation Runner
========================
Main script to run and evaluate the RL task.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Callable, Dict, List

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import task components
from task.grader import grade_submission
from task.tool_api import AVAILABLE_TOOLS

# Import APIs based on provider
API_PROVIDER = os.getenv("API_PROVIDER", "anthropic").lower()

if API_PROVIDER == "anthropic":
    from anthropic import AsyncAnthropic
    from anthropic.types import MessageParam, ToolUnionParam
elif API_PROVIDER == "openai":
    from openai import AsyncOpenAI
else:
    raise ValueError(f"Unsupported API provider: {API_PROVIDER}")


async def run_agent_loop(
    prompt: str,
    tools: List[Dict],
    tool_handlers: Dict[str, Callable],
    max_steps: int = 20,
    model: str = None,
    verbose: bool = True,
) -> Any:
    """Run the agent loop with the given prompt and tools."""
    
    # Set default model based on provider
    if model is None:
        model = "claude-3-5-haiku-latest" if API_PROVIDER == "anthropic" else "gpt-4o-mini"
    
    if verbose:
        print(f"Using {API_PROVIDER.upper()} API with model: {model}")
    
    if API_PROVIDER == "anthropic":
        return await _run_anthropic_loop(prompt, tools, tool_handlers, max_steps, model, verbose)
    else:
        return await _run_openai_loop(prompt, tools, tool_handlers, max_steps, model, verbose)


async def _run_anthropic_loop(prompt, tools, tool_handlers, max_steps, model, verbose):
    """Run agent loop with Anthropic API"""
    client = AsyncAnthropic()
    messages = [{"role": "user", "content": prompt}]

    for step in range(max_steps):
        if verbose:
            print(f"\n=== Step {step + 1}/{max_steps} ===")

        response = await client.messages.create(
            model=model, max_tokens=1000, tools=tools, messages=messages
        )

        has_tool_use = False
        tool_results = []
        submitted_answer = None

        # Process the response
        for content in response.content:
            if content.type == "text":
                if verbose:
                    print(f"Assistant: {content.text}")
            elif content.type == "tool_use":
                has_tool_use = True
                tool_name = content.name

                if tool_name in tool_handlers:
                    if verbose:
                        print(f"Using tool: {tool_name}")

                    handler = tool_handlers[tool_name]
                    tool_input = content.input

                    # Call the tool handler
                    if isinstance(tool_input, dict):
                        result = handler(**tool_input)
                    else:
                        result = handler(tool_input)

                    # Check if answer was submitted
                    if tool_name == "submit_answer" and result.get("submitted"):
                        submitted_answer = result["answer"]

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": json.dumps(result, default=str),
                    })

        # Continue conversation
        if has_tool_use:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            if submitted_answer is not None:
                if verbose:
                    print(f"\nAgent submitted answer")
                return submitted_answer
        else:
            if verbose:
                print("\nNo tool use in response, ending loop.")
            break

    if verbose:
        print(f"\nReached maximum steps ({max_steps}) without submitting answer.")
    return None


async def _run_openai_loop(prompt, tools, tool_handlers, max_steps, model, verbose):
    """Run agent loop with OpenAI API"""
    client = AsyncOpenAI()
    
    # Convert tools to OpenAI format
    openai_tools = []
    for tool in tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"]
            }
        })
    
    messages = [{"role": "user", "content": prompt}]

    for step in range(max_steps):
        if verbose:
            print(f"\n=== Step {step + 1}/{max_steps} ===")

        response = await client.chat.completions.create(
            model=model,
            max_tokens=1000,
            tools=openai_tools,
            messages=messages
        )

        message = response.choices[0].message
        has_tool_use = False
        submitted_answer = None

        if message.content:
            if verbose:
                print(f"Assistant: {message.content}")

        if message.tool_calls:
            has_tool_use = True
            
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": message.tool_calls
            })

            # Process each tool call
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                
                if tool_name in tool_handlers:
                    if verbose:
                        print(f"Using tool: {tool_name}")

                    handler = tool_handlers[tool_name]
                    
                    try:
                        tool_input = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_input = {}

                    # Call the tool handler
                    try:
                        if isinstance(tool_input, dict) and tool_input:
                            result = handler(**tool_input)
                        else:
                            # Handle case where tool_input is empty or not a dict
                            result = {"error": "Invalid tool input"}
                    except Exception as e:
                        result = {"error": f"Tool execution error: {str(e)}"}

                    # Check if answer was submitted
                    if tool_name == "submit_answer" and result.get("submitted"):
                        submitted_answer = result["answer"]

                    # Add tool result message
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, default=str)
                    })

            if submitted_answer is not None:
                if verbose:
                    print(f"\nAgent submitted answer")
                return submitted_answer
        else:
            if verbose:
                print("\nNo tool use in response, ending loop.")
            break

    if verbose:
        print(f"\nReached maximum steps ({max_steps}) without submitting answer.")
    return None


async def run_single_trial(
    trial_id: int,
    prompt: str,
    tools: List[Dict],
    tool_handlers: Dict[str, Callable],
    verbose: bool = False,
) -> Dict[str, Any]:
    """Run a single trial and return results."""
    
    if verbose:
        print(f"\n{'=' * 20} TRIAL {trial_id} {'=' * 20}")

    start_time = datetime.now()
    
    result = await run_agent_loop(
        prompt=prompt,
        tools=tools,
        tool_handlers=tool_handlers,
        max_steps=10,
        verbose=verbose,
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Grade the submission
    if result:
        success, feedback, detailed_results = grade_submission(result)
    else:
        success = False
        feedback = "No answer submitted"
        detailed_results = {}

    trial_result = {
        "trial_id": trial_id,
        "success": success,
        "feedback": feedback,
        "duration_seconds": duration,
        "timestamp": start_time.isoformat(),
        "submitted_answer": str(result) if result else None,
        "detailed_results": detailed_results
    }

    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status} Trial {trial_id}: {feedback} ({duration:.1f}s)")

    return trial_result


async def main(concurrent: bool = True):
    """Main evaluation function."""
    
    # Load task prompt
    with open("task/prompt.txt", "r") as f:
        prompt = f.read()

    # Prepare tools
    tools = []
    tool_handlers = {}
    
    for tool_name, tool_config in AVAILABLE_TOOLS.items():
        tools.append({
            "name": tool_name,
            "description": tool_config["description"],
            "input_schema": tool_config["input_schema"],
        })
        tool_handlers[tool_name] = tool_config["function"]

    # Configuration
    num_trials = 10
    
    print(f"Running {num_trials} trials {'concurrently' if concurrent else 'sequentially'}...")
    print("=" * 60)

    # Create trial tasks
    tasks = [
        run_single_trial(
            trial_id=i + 1,
            prompt=prompt,
            tools=tools,
            tool_handlers=tool_handlers,
            verbose=False,
        )
        for i in range(num_trials)
    ]

    # Run trials
    start_time = datetime.now()
    
    if concurrent:
        results = []
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
    else:
        results = []
        for task in tasks:
            result = await task
            results.append(result)

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    # Calculate statistics
    successes = sum(1 for r in results if r["success"])
    pass_rate = (successes / num_trials) * 100

    # Display results
    print(f"\n{'=' * 60}")
    print("EVALUATION RESULTS")
    print(f"{'=' * 60}")
    print(f"Total Trials: {num_trials}")
    print(f"Passed: {successes}")
    print(f"Failed: {num_trials - successes}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"Total Time: {total_duration:.1f}s")
    print(f"Avg Time/Trial: {total_duration/num_trials:.1f}s")

    # Check target range (10-40% for RL training)
    if 10 <= pass_rate <= 40:
        print("🎉 SUCCESS: Pass rate is within target range for RL training!")
    elif pass_rate < 10:
        print("⚠️  WARNING: Pass rate too low. Consider making task easier.")
    else:
        print("⚠️  WARNING: Pass rate too high. Consider making task harder.")

    # Save results
    save_results(results, pass_rate, total_duration)


def save_results(results: List[Dict], pass_rate: float, duration: float):
    """Save detailed results and summary."""
    
    # Create results directory
    os.makedirs("results", exist_ok=True)
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y-%m-%d")
    results_file = f"results/runs_{timestamp}.json"
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_trials": len(results),
        "pass_rate": pass_rate,
        "duration_seconds": duration,
        "target_range": [10, 40],
        "trials": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Save pass rate summary
    with open("results/pass_rate.txt", 'w') as f:
        f.write(f"Pass Rate: {pass_rate:.1f}%\n")
        f.write(f"Target Range: 10-40%\n")
        f.write(f"Status: {'✓ GOOD' if 10 <= pass_rate <= 40 else '⚠ ADJUST'}\n")
        f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n📄 Results saved to: {results_file}")


if __name__ == "__main__":
    # Set to True for concurrent execution, False for sequential
    asyncio.run(main(concurrent=True))