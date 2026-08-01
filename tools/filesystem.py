import os
from langchain.tools import tool

@tool
def read_file(path: str) -> str:
    """Reads the contents of a file at the given path."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def write_file(path: str, content: str) -> str:
    """Writes the content to the given file path. Overwrites if it exists."""
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def append_file(path: str, content: str) -> str:
    """Appends content to the end of a file at the given path."""
    try:
        with open(path, 'a') as f:
            f.write(content)
        return f"Successfully appended to {path}"
    except Exception as e:
        return f"Error appending to file: {e}"

@tool
def list_directory(path: str = ".") -> str:
    """Lists the contents of the given directory path."""
    try:
        items = os.listdir(path)
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {e}"
