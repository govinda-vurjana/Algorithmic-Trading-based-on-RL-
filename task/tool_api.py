"""
Tool API
========
Simple tools that the model can use during task execution.
"""

import os
import json
import urllib.request
import urllib.parse
from pathlib import Path 
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Dict


def python_expression_tool(expression: str) -> Dict[str, Any]:
    """
    Execute Python code and return the result.
    
    Args:
        expression: Python code to execute
        
    Returns:
        Dict with 'result' and 'error' keys
    """
    try:
        namespace = {}
        stdout = StringIO()
        with redirect_stdout(stdout):
            # Try eval first, then exec
            if "print(" not in expression:
                try:
                    result = eval(expression, namespace, namespace)
                    print(result)
                except:
                    exec(expression, namespace, namespace)
            else:
                exec(expression, namespace, namespace)
        return {"result": stdout.getvalue(), "error": None}
    except Exception as e:
        return {"result": None, "error": str(e)}


def file_reader_tool(filepath: str) -> Dict[str, Any]:
    """
    Read files from the task directory.
    
    Args:
        filepath: Path to file (relative to task directory)
        
    Returns:
        Dict with 'content' and 'error' keys
    """
    try:
        # Security: only allow reading from task directory
        if not filepath.startswith("task/"):
            filepath = f"task/{filepath}"
        
        # Handle common path variations
        if filepath.startswith("task/task/"):
            filepath = filepath.replace("task/task/", "task/")
        
        if not os.path.exists(filepath):
            return {"content": None, "error": f"File not found: {filepath}"}
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {"content": content, "error": None}
    except Exception as e:
        return {"content": None, "error": str(e)}


# def dataset_download_tool(url: str, filename: str = None) -> Dict[str, Any]:
#     """
#     Download a dataset from a URL.
    
#     Args:
#         url: URL to download the dataset from
#         filename: Optional filename to save as
        
#     Returns:
#         Dict with 'filepath', 'filename' and 'error' keys
#     """
#     try:
#         # NOTE: urllib.request, urllib.parse, and pathlib.Path 
#         # are now imported globally at the top of the file.
        
#         # Create data directory if it doesn't exist
#         data_dir = Path("task/data")
#         data_dir.mkdir(parents=True, exist_ok=True)
        
#         # Generate filename if not provided
#         if filename is None:
#             parsed_url = urllib.parse.urlparse(url)
#             filename = Path(parsed_url.path).name
#             if not filename or '.' not in filename:
#                 filename = "downloaded_dataset.csv"  # Default extension
        
#         filepath = data_dir / filename
        
#         # 🟢 FILE EXISTENCE CHECK TO PREVENT REDOWNLOAD
#         if filepath.exists():
#             print(f"File already exists: {filepath}. Skipping download.")
#             return {"filepath": str(filepath), "filename": filename, "error": None}
#         # 🟢 END OF FIX

#         # Download the file
#         print(f"Downloading dataset from: {url}")
#         urllib.request.urlretrieve(url, filepath)
#         print(f"Dataset saved to: {filepath}")
        
#         return {"filepath": str(filepath), "filename": filename, "error": None}
#     except Exception as e:
#         return {"filepath": None, "filename": None, "error": str(e)}


def submit_answer_tool(answer: Any) -> Dict[str, Any]:
    """
    Submit the final answer.
    
    Args:
        answer: The solution to submit
        
    Returns:
        Dict with 'answer' and 'submitted' keys
    """
    return {"answer": answer, "submitted": True}


# Tool registry for easy access
AVAILABLE_TOOLS = {
    "python_expression": {
        "function": python_expression_tool,
        "description": "Execute Python code and see the output",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Python code to execute. Use print() for output.",
                }
            },
            "required": ["expression"],
        },
    },
    "file_reader": {
        "function": file_reader_tool,
        "description": "Read files from the task directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to read (e.g., 'data/sample.csv')",
                }
            },
            "required": ["filepath"],
        },
    },
    # "dataset_download": {
    #     "function": dataset_download_tool,
    #     "description": "Download a dataset from a URL",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "url": {
    #                 "type": "string",
    #                 "description": "URL to download the dataset from (e.g., 'https://example.com/data.csv')",
    #             },
    #             "filename": {
    #                 "type": "string",
    #                 "description": "Optional filename to save as (e.g., 'my_dataset.csv')",
    #             }
    #         },
    #         "required": ["url"],
    #     },
    # },
    "submit_answer": {
        "function": submit_answer_tool,
        "description": "Submit your final solution",
        "input_schema": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "Your solution code"
                }
            },
            "required": ["answer"],
        },
    },
}