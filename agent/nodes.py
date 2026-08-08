import json
import os
import platform
import subprocess
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel, Field

from agent.state import AgentState, CommandPlan
from tools.terminal import run_command
from tools import ALL_TOOLS

# ── Detect OS once at import time ──────────────────────────────────────────
def _detect_os_info() -> str:
    """Detect the host OS details so the LLM never suggests wrong-distro commands."""
    info_parts = []
    try:
        result = subprocess.run(
            ["lsb_release", "-d", "-s"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            info_parts.append(result.stdout.strip())
    except Exception:
        pass
    
    if not info_parts:
        # Fallback: read /etc/os-release
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        info_parts.append(line.split("=", 1)[1].strip().strip('"'))
                        break
        except Exception:
            info_parts.append(platform.system() + " " + platform.release())
    
    info_parts.append(f"Arch: {platform.machine()}")
    return ", ".join(info_parts)

OS_INFO = _detect_os_info()

# ── Ensure logs directory exists ───────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "execution_log.jsonl")


# ── Helper schemas ─────────────────────────────────────────────────────────
class PlannerDecision(BaseModel):
    needs_search: bool = Field(description="True if web search is needed based on criteria.")
    search_query: str = Field(
        default="",
        description="If needs_search is True, provide a clean, concise search query. Example: 'install yay AUR helper on Ubuntu 24.04'"
    )


# ── Nodes ──────────────────────────────────────────────────────────────────
def planner_node(state: AgentState, llm):
    """Decides if web search is needed and generates a clean search query."""
    print("\n--- PLANNER ---")
    print(f"OS: {OS_INFO}")
    prompt = f"""
    You are a Linux Agent Planner.
    The host operating system is: {OS_INFO}
    
    Analyze this goal: '{state['goal']}'.
    
    Decide if a web search is necessary.
    DO NOT search for basic commands (ls, pwd, mkdir, rm, mv, cp, git, cat, echo, touch).
    DO search for: software installation, OS-specific setup, drivers, CUDA, Docker, GNOME config, unknown software, latest CLI syntax.
    
    If search IS needed, generate a clean, concise search query.
    - Strip conversational filler words (like "refer internet", "please", "I want to").
    - Include the OS name from above.
    - Focus on the core task.
    
    Example:
      User goal: "install yay refer internet!"
      search_query: "install yay AUR helper Ubuntu 24.04"
    """
    
    structured_llm = llm.with_structured_output(PlannerDecision)
    result = structured_llm.invoke([SystemMessage(content=prompt)])
    
    print(f"Needs Search: {result.needs_search}")
    if result.needs_search:
        print(f"Search Query: {result.search_query}")
    
    return {"needs_search": result.needs_search, "search_results": result.search_query if result.needs_search else ""}


def web_search_node(state: AgentState):
    """Performs a web search using the clean query from the planner."""
    print("\n--- WEB SEARCH ---")
    search_tool = DuckDuckGoSearchResults()
    # Use the clean query from the planner, not the raw user input
    query = state.get("search_results", state["goal"])
    print(f"Searching: {query}")
    results = search_tool.invoke({"query": query})
    return {"search_results": results}


def command_generator_node(state: AgentState, llm):
    """Generates the command plan."""
    print("\n--- COMMAND GENERATOR ---")
    
    error_context = ""
    if state.get('error_reasoning'):
        error_context = f"\nPREVIOUS FAILURE REASONING:\n{state['error_reasoning']}\n\nYou must generate a DIFFERENT fix for this failure."
        
    search_context = ""
    if state.get('search_results'):
        search_context = f"\nSEARCH RESULTS:\n{state['search_results']}"

    tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in ALL_TOOLS])
    prompt = f"""
    Goal: {state['goal']}
    Host OS: {OS_INFO}
    {search_context}
    {error_context}
    
    You have access to the following tools:
    {tool_descriptions}
    
    RULES:
    1. Pick the MOST DIRECT tool to accomplish the goal. Do NOT explore or list directories first — go straight to the action.
       For example, if the goal is "write a file", use 'write_file' directly. If it's "run a bash command", use 'run_command'.
    2. The 'verification_command' field MUST be a real Linux bash command (e.g., "ls -l test/file.py", "python3 --version", "cat file.txt").
       It must NOT be a tool name. It will be executed in a bash shell to verify the result.
    3. Classify the safety level:
       - SAFE: (ls, pwd, mkdir, touch, pip install, read_file, write_file, list_directory)
       - WARNING: (sudo, apt install, chmod, mv)
       - BLOCKED: (rm -rf /, mkfs, dd, shutdown, reboot)
    4. CRITICAL: All commands MUST be compatible with the host OS ({OS_INFO}).
       Do NOT suggest Arch Linux commands (pacman, makepkg, yay) on Ubuntu/Debian.
       Do NOT suggest apt commands on Arch Linux.
       Use the correct package manager for this OS.
    5. NEVER use markdown formatting in command strings or URLs. 
       Write plain URLs like: https://example.com/repo.git
       NEVER write: [https://example.com/repo.git](https://example.com/repo.git)
    """
    
    structured_llm = llm.with_structured_output(CommandPlan)
    plan = structured_llm.invoke([SystemMessage(content=prompt)])
    
    print(f"Selected Tool: {plan.tool_name}")
    print(f"Tool Args: {plan.tool_args}")
    print(f"Safety Level: {plan.safety_level}")
    
    return {"command_plan": plan}


def execution_node(state: AgentState):
    """Executes the generated command."""
    print("\n--- EXECUTION ---")
    plan = state['command_plan']
    
    if plan.safety_level == "BLOCKED":
        print(f"\n[BLOCKED] This command is too dangerous and has been blocked: {plan.tool_args}")
        return {"status": "aborted"}
    
    if plan.safety_level == "WARNING":
        print(f"\n[WARNING] Action requires approval: {plan.tool_name} with args {plan.tool_args}")
        print(f"Explanation: {plan.explanation}")
        user_input = input("Proceed? (y/n): ")
        if user_input.lower() not in ['y', 'yes']:
            print("Execution aborted by user.")
            return {"status": "aborted"}

    print(f"Running Tool: {plan.tool_name} with {plan.tool_args}")
    
    # Find the tool
    tool_to_run = next((t for t in ALL_TOOLS if t.name == plan.tool_name), None)
    
    if not tool_to_run:
        print(f"Error: Tool '{plan.tool_name}' not found.")
        result_dict = {"success": False, "stderr": f"Tool '{plan.tool_name}' not found.", "tool_name": plan.tool_name}
    else:
        # Invoke the tool
        try:
            result_dict = tool_to_run.invoke(plan.tool_args)
        except Exception as e:
            result_dict = {"success": False, "stderr": str(e), "tool_name": plan.tool_name}
    
    # Log to a file (LOG_FILE path is absolute, always works)
    try:
        with open(LOG_FILE, "a") as f:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool_name": plan.tool_name,
                "tool_args": plan.tool_args,
                "result": result_dict,
                "retry_count": state.get('retry_count', 0)
            }
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"[LOG WARNING] Could not write log: {e}")
        
    history = state.get('history', [])
    history.append(result_dict)
        
    return {"history": history, "status": "executed"}


def verification_node(state: AgentState):
    """Verifies the command execution."""
    if state.get('status') == "aborted":
        return {"status": "failed"}
        
    print("\n--- VERIFICATION ---")
    plan = state['command_plan']
    
    print(f"Running Verification: {plan.verification_command}")
    result_dict = run_command.invoke({"command": plan.verification_command})
    
    success = result_dict['success']
    
    print(f"Verification Success: {success}")
    
    return {"status": "success" if success else "failed"}


def reflection_node(state: AgentState, llm):
    """Reflects on a failure and plans a fix."""
    print("\n--- REFLECTION ---")
    
    retry_count = state.get('retry_count', 0) + 1
    if retry_count > 5:
        print("Max retries exceeded.")
        return {"status": "max_retries", "retry_count": retry_count}
        
    last_exec = state['history'][-1] if state.get('history') else {}
    
    prompt = f"""
    Host OS: {OS_INFO}
    Action failed: {state['command_plan'].tool_name} with args {state['command_plan'].tool_args}
    Stderr: {last_exec.get('stderr', '')}
    Stdout: {last_exec.get('stdout', '')}
    
    Analyze why this failed and provide a brief reasoning for how to fix it on the next attempt.
    Remember: all commands must be compatible with {OS_INFO}.
    """
    
    result = llm.invoke([SystemMessage(content=prompt)])
    reasoning = result.content
    print(f"Reasoning: {reasoning}")
    
    return {"error_reasoning": reasoning, "retry_count": retry_count, "status": "retrying"}
