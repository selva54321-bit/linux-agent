from typing import TypedDict, Optional, List, Dict, Any
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    cwd: Optional[str] = None
    duration: Optional[float] = None
    tool_name: str
    
    def to_dict(self):
        return self.model_dump()

class AgentState(TypedDict):
    goal: str
    plan: List[str]
    current_step: Optional[str]
    history: List[ToolResult]
    workspace_context: Dict[str, Any]
    status: str
