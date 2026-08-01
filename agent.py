import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from tools import ALL_TOOLS

def load_system_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful Linux agent."

def create_agent():
    # Ensure API key is set
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.0
    )
    
    system_prompt = load_system_prompt()
    
    # Checkpointer for session memory
    memory = MemorySaver()
    
    # Create the React Agent using LangGraph
    agent_executor = create_react_agent(
        llm, 
        ALL_TOOLS,
        state_modifier=system_prompt,
        checkpointer=memory
    )
    
    return agent_executor
