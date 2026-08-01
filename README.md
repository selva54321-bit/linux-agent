# Linux Terminal AI Agent

A robust, modular AI agent that operates in a Linux environment. Built using **LangChain**, **LangGraph**, and the **Google Gemini API**, this agent can reason about tasks, execute commands, manipulate files, and debug its own errors in a loop.

## Overview

This project was originally a simple, single-file script that blindly executed bash commands for every task. It has since been refactored into a **Phase 2 Architecture**—similar to professional agents like OpenHands or Cursor—where the agent has access to a suite of specialized tools instead of relying solely on a single raw shell execution tool.

### Key Features
* **ReAct Loop (Reason & Act):** Uses `langgraph.prebuilt.create_react_agent` to continuously reason, act, observe tool outputs, and adjust its approach until the goal is achieved.
* **Specialized Tools:** Distinct tools for filesystem manipulation, Git operations, and Python environments, leading to safer and more predictable behavior.
* **Session Memory:** Uses a LangGraph `MemorySaver` checkpointer so the agent remembers context during your active session.
* **Streamlined Output:** You can see exactly what tools the agent is calling and the results it's getting in real-time.

## Project Structure

```text
linux-agent/
├── main.py                 # The entry point and interactive REPL chat loop
├── agent.py                # Initializes the Gemini LLM, tools, and the LangGraph agent
├── tools/
│   ├── __init__.py         # Exports ALL_TOOLS for the agent to bind
│   ├── terminal.py         # run_command(): The fallback terminal execution tool
│   ├── filesystem.py       # read_file(), write_file(), append_file(), list_directory()
│   ├── python_tools.py     # create_virtualenv(), pip_install()
│   └── git_tools.py        # git_status(), git_log()
├── prompts/
│   └── system_prompt.txt   # The core instruction set governing the agent's behavior
└── README.md               # You are here
```

## Setup & Installation

This project uses `uv` (or standard `pip`) for dependency management.

1. **Install Dependencies:**
   ```bash
   # Using uv:
   uv add langchain langchain-google-genai langgraph
   
   # Or using pip:
   pip install langchain langchain-google-genai langgraph
   ```

2. **Set your API Key:**
   The agent requires a Google Gemini API key to run.
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

3. **Run the Agent:**
   ```bash
   python main.py
   ```

## Recent Changes (Phase 2 Refactor)
* **Modularization:** Moved away from a single `simple_agent.py` to a structured directory (`main.py`, `agent.py`, `tools/`).
* **Tool Specialization:** Replaced a single monolithic shell tool with modular tools (e.g., `read_file` instead of running `cat file.txt`).
* **Upgraded LangGraph Syntax:** Updated the agent creation logic to use `prompt=` instead of the deprecated `state_modifier=` for `create_react_agent` in `langgraph-prebuilt>=1.1.0`.
* **State Persistence:** Added `MemorySaver()` to `agent.py` so the agent remembers past inputs within the same session.

## Future Roadmap (Phase 3)
* **Persistent Shell Environment:** Upgrade `terminal.py` to use a persistent subprocess (e.g., `pexpect`), allowing commands like `cd` or `export` to persist state across consecutive terminal tool calls.
* **Execution Logging:** Implement structured JSON logging into a `logs/` directory to keep historical records of all agent actions.
* **Safety Guardrails:** Add a pre-execution hook requiring user confirmation before running highly destructive bash commands (e.g., `rm -rf`).
