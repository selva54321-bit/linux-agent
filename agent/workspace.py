from pathlib import Path

class Workspace:
    def __init__(self):
        self.root = Path.cwd()

    def resolve(self, path: str) -> Path:
        """Resolves a given path relative to the workspace root."""
        return (self.root / path).resolve()

# Global workspace instance to be shared across tools
workspace = Workspace()
