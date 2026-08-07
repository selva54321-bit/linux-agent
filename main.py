import os
import sys
from agent.graph import create_agent

def main():
    print("Initializing Agent...")
    try:
        agent = create_agent()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please export GEMINI_API_KEY='your_api_key'")
        sys.exit(1)
        
    print("🤖 Agent initialized! Specialized tools loaded. (Type 'exit' to quit)")
    
    # Configuration for conversation memory (if using a checkpointer)
    config = {"configurable": {"thread_id": "repl_session_1"}}
    
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            print("\nAgent is thinking...")
            
            # Stream the agent's thought process and tool actions
            # langgraph prebuilt agent streams state updates
            events = agent.stream(
                {"messages": [("user", user_input)]}, 
                config=config, 
                stream_mode="updates"
            )
            
            for event in events:
                for node_name, node_state in event.items():
                    messages = node_state.get("messages", [])
                    if not messages:
                        continue
                        
                    message = messages[-1]
                    
                    if node_name == "agent" and hasattr(message, "tool_calls") and message.tool_calls:
                        for tool_call in message.tool_calls:
                            print(f"  [Calling Tool]: {tool_call['name']} with args: {tool_call['args']}")
                            
                    elif node_name == "tools":
                        # Tool result
                        # Truncate for display
                        display_content = message.content[:200] + "..." if len(message.content) > 200 else message.content
                        print(f"  [Tool Result]: {display_content}")
                        
            # After the stream finishes, print the final AI response
            # The agent mutates the state, so the last message is from the AI.
            state = agent.get_state(config)
            final_message = state.values["messages"][-1]
            if final_message.type == "ai" and final_message.content:
                print(f"\nAgent: {final_message.content}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            break

if __name__ == "__main__":
    main()
