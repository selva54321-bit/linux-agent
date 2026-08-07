import subprocess
import time
import sys
import os
from langchain.tools import tool

# Add the parent directory to sys.path so we can import agent.state
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.state import ToolResult
from agent.workspace import workspace

@tool
def git_status() -> dict:
    """Returns the current git status."""
    start_time = time.time()
    try:
        result = subprocess.run(["git", "status"], cwd=str(workspace.root), capture_output=True, text=True)
        return ToolResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
            tool_name="git_status",
            duration=time.time() - start_time
        ).to_dict()
    except Exception as e:
        return ToolResult(
            success=False,
            stderr=f"Error running git status: {e}",
            tool_name="git_status",
            duration=time.time() - start_time
        ).to_dict()

@tool
def git_log(n: int = 5) -> dict:
    """Returns the last n commits from git log."""
    start_time = time.time()
    try:
        result = subprocess.run(["git", "log", f"-n{n}"], cwd=str(workspace.root), capture_output=True, text=True)
        return ToolResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
            tool_name="git_log",
            duration=time.time() - start_time
        ).to_dict()
    except Exception as e:
        return ToolResult(
            success=False,
            stderr=f"Error running git log: {e}",
            tool_name="git_log",
            duration=time.time() - start_time
        ).to_dict()
