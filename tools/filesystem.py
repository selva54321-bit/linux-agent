import os
from langchain.tools import tool
import time
import sys

# Add the parent directory to sys.path so we can import agent.state
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.state import ToolResult
from agent.workspace import workspace

@tool
def read_file(path: str) -> dict:
    """Reads the contents of a file at the given path."""
    start_time = time.time()
    try:
        full_path = workspace.resolve(path)
        with open(full_path, 'r') as f:
            content = f.read()
        return ToolResult(
            success=True,
            stdout=content,
            tool_name="read_file",
            duration=time.time() - start_time
        ).to_dict()
    except Exception as e:
        return ToolResult(
            success=False,
            stderr=f"Error reading file: {e}",
            tool_name="read_file",
            duration=time.time() - start_time
        ).to_dict()

@tool
def write_file(path: str, content: str) -> dict:
    """Writes the content to the given file path. Overwrites if it exists."""
    start_time = time.time()
    try:
        full_path = workspace.resolve(path)
        os.makedirs(full_path.parent, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return ToolResult(
            success=True,
            stdout=f"Successfully wrote to {path}",
            tool_name="write_file",
            duration=time.time() - start_time
        ).to_dict()
    except Exception as e:
        return ToolResult(
            success=False,
            stderr=f"Error writing file: {e}",
            tool_name="write_file",
            duration=time.time() - start_time
        ).to_dict()

@tool
def append_file(path: str, content: str) -> dict:
    """Appends content to the end of a file at the given path."""
    start_time = time.time()
    try:
        full_path = workspace.resolve(path)
        with open(full_path, 'a') as f:
            f.write(content)
        return ToolResult(
            success=True,
            stdout=f"Successfully appended to {path}",
            tool_name="append_file",
            duration=time.time() - start_time
        ).to_dict()
    except Exception as e:
        return ToolResult(
            success=False,
            stderr=f"Error appending to file: {e}",
            tool_name="append_file",
            duration=time.time() - start_time
        ).to_dict()

@tool
def list_directory(path: str = ".") -> dict:
    """Lists the contents of the given directory path."""
    start_time = time.time()
    try:
        full_path = workspace.resolve(path)
        items = os.listdir(full_path)
        content = "\n".join(items) if items else "Directory is empty."
        return ToolResult(
            success=True,
            stdout=content,
            tool_name="list_directory",
            duration=time.time() - start_time
        ).to_dict()
    except Exception as e:
        return ToolResult(
            success=False,
            stderr=f"Error listing directory: {e}",
            tool_name="list_directory",
            duration=time.time() - start_time
        ).to_dict()
