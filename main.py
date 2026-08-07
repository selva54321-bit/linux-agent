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
            
            # The agent takes "goal" as input
            events = agent.stream(
                {"goal": user_input, "retry_count": 0, "history": []}, 
                config=config, 
                stream_mode="updates"
            )
            
            for event in events:
                for node_name, node_state in event.items():
                    print(f"\n[Completed Node: {node_name.upper()}]")
                    if "status" in node_state:
                        print(f"Status: {node_state['status']}")
                        
            state = agent.get_state(config)
            if state.values.get("status") == "success":
                print("\nAgent: Task completed successfully.")
            elif state.values.get("status") == "aborted":
                print("\nAgent: Task aborted.")
            else:
                print(f"\nAgent: Task failed or ended with status: {state.values.get('status')}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            break

if __name__ == "__main__":
    main()
