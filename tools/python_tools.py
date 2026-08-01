import subprocess
from langchain.tools import tool

@tool
def create_virtualenv(path: str = ".venv") -> str:
    """Creates a Python virtual environment at the specified path."""
    try:
        subprocess.run(["python3", "-m", "venv", path], check=True)
        return f"Successfully created virtual environment at {path}"
    except Exception as e:
        return f"Failed to create virtual environment: {e}"

@tool
def pip_install(package: str) -> str:
    """Installs a Python package using pip. Assumes virtual env is active or uses global pip."""
    try:
        # In a real agent, we might want to ensure we use the venv pip
        # For this simple tool, we just run pip install.
        result = subprocess.run(["pip", "install", package], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Successfully installed {package}\n{result.stdout}"
        else:
            return f"Failed to install {package}\n{result.stderr}"
    except Exception as e:
        return f"Error running pip install: {e}"
