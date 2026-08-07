import subprocess
from langchain.tools import tool

@tool
def run_command(command: str) -> dict:
    """Executes a bash command in the Linux terminal. Use this ONLY when there is no specialized tool for the task.
    Returns a dictionary with 'success', 'stdout', 'stderr', and 'exit_code'."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout[:4000] + "\n...[Truncated]" if len(result.stdout) > 4000 else result.stdout,
            "stderr": result.stderr[:4000] + "\n...[Truncated]" if len(result.stderr) > 4000 else result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Error: Command timed out after 30 seconds.",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Failed to execute command: {str(e)}",
            "exit_code": -1
        }

# This is a test comment.