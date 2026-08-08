import os
os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")
# from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from functools import partial

from agent.state import AgentState
from agent.nodes import (
    planner_node,
    web_search_node,
    command_generator_node,
    execution_node,
    verification_node,
    reflection_node
)

def create_agent():
    # Initialize the Ollama LLM
    llm = ChatOllama(
        model="gemma4:e4b",
        base_url="http://localhost:11434",
        temperature=0.0,
    )
    
    # Initialize StateGraph
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    # We use functools.partial to pass the llm instance where needed
    workflow.add_node("planner", partial(planner_node, llm=llm))
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("command_generator", partial(command_generator_node, llm=llm))
    workflow.add_node("executor", execution_node)
    workflow.add_node("verifier", verification_node)
    workflow.add_node("reflector", partial(reflection_node, llm=llm))
    
    # Define Edges
    workflow.set_entry_point("planner")
    
    # Planner -> Web Search or Command Generator
    workflow.add_conditional_edges(
        "planner",
        lambda state: "web_search" if state.get("needs_search") else "command_generator",
        {
            "web_search": "web_search",
            "command_generator": "command_generator"
        }
    )
    
    workflow.add_edge("web_search", "command_generator")
    workflow.add_edge("command_generator", "executor")
    workflow.add_edge("executor", "verifier")
    
    # Verifier -> END or Reflector
    workflow.add_conditional_edges(
        "verifier",
        lambda state: "end" if state.get("status") == "success" else ("end" if state.get("status") == "aborted" else "reflector"),
        {
            "end": END,
            "reflector": "reflector"
        }
    )
    
    # Reflector -> Command Generator (retry) or END (max retries)
    workflow.add_conditional_edges(
        "reflector",
        lambda state: "command_generator" if state.get("status") == "retrying" else "end",
        {
            "command_generator": "command_generator",
            "end": END
        }
    )
    
    # Checkpointer for session memory
    memory = MemorySaver()
    
    # Compile the graph
    app = workflow.compile(checkpointer=memory)
    
    return app