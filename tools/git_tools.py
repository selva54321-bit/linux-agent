import subprocess
from langchain.tools import tool

@tool
def git_status() -> str:
    """Returns the current git status."""
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Git status failed:\n{result.stderr}"
    except Exception as e:
        return f"Error running git status: {e}"

@tool
def git_log(n: int = 5) -> str:
    """Returns the last n commits from git log."""
    try:
        result = subprocess.run(["git", "log", f"-n{n}"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Git log failed:\n{result.stderr}"
    except Exception as e:
        return f"Error running git log: {e}"
