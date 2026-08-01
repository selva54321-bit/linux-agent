import subprocess
import time
import sys
import os
from langchain.tools import tool

# Add the parent directory to sys.path so we can import agent.state
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.state import ToolResult

@tool
def create_virtualenv(path: str = ".venv") -> dict:
    """Creates a Python virtual environment at the specified path."""
    start_time = time.time()
    try:
        subprocess.run(["python3", "-m", "venv", path], check=True, capture_output=True, text=True)
        return ToolResult(
            success=True,
            stdout=f"Successfully created virtual environment at {path}",
            tool_name="create_virtualenv",
            duration=time.time() - start_time
        ).to_dict()
    except subprocess.CalledProcessError as e:
        return ToolResult(
            success=False,
            stderr=f"Failed to create virtual environment:\n{e.stderr}",
            tool_name="create_virtualenv",
            duration=time.time() - start_time
        ).to_dict()
    except Exception as e:
        return ToolResult(
            success=False,
            stderr=f"Failed to create virtual environment: {e}",
            tool_name="create_virtualenv",
            duration=time.time() - start_time
        ).to_dict()

@tool
def pip_install(package: str) -> dict:
    """Installs a Python package using pip."""
    start_time = time.time()
    try:
        result = subprocess.run(["pip", "install", package], capture_output=True, text=True)
        return ToolResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
            tool_name="pip_install",
            duration=time.time() - start_time
        ).to_dict()
    except Exception as e:
        return ToolResult(
            success=False,
            stderr=f"Error running pip install: {e}",
            tool_name="pip_install",
            duration=time.time() - start_time
        ).to_dict()
