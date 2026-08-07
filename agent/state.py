from typing import TypedDict, Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

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

class CommandPlan(BaseModel):
    tool_name: str = Field(description="The name of the tool to execute (e.g., run_command, read_file).")
    tool_args: Dict[str, Any] = Field(description="The arguments to pass to the tool.")
    explanation: str = Field(description="Explanation of why this command was chosen.")
    expected_result: str = Field(description="What success looks like.")
    verification_command: str = Field(description="The command to run to verify success.")
    safety_level: Literal["SAFE", "WARNING", "BLOCKED"] = Field(description="Safety classification of the command.")

class AgentState(TypedDict):
    goal: str
    plan: List[str]
    current_step: Optional[str]
    history: List[ToolResult]
    workspace_context: Dict[str, Any]
    status: str
    
    # Phase 3 Engine states
    needs_search: bool
    search_results: str
    command_plan: Optional[CommandPlan]
    retry_count: int
    error_reasoning: str
