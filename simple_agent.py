import os
import subprocess
from google import genai
from google.genai import types

def execute_command(command: str) -> str:
    """Executes a bash command on the Linux terminal and returns its output. Use this to perform actions on the system."""
    print(f"\n[Agent executing]: {command}")
    try:
        # We use shell=True to allow normal bash syntax (pipes, &&, etc.)
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30 # Prevent hanging on commands like 'top'
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
            
        if not output.strip():
            return "Command executed successfully with no output."
            
        # Truncate output if it's too long
        if len(output) > 4000:
            output = output[:4000] + "\n...[Output truncated]..."
            
        print(f"[Command Output]:\n{output}")
        return output
    except subprocess.TimeoutExpired:
        print("[Command Output]: Error: Command timed out after 30 seconds.")
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        error_msg = f"Failed to execute command: {str(e)}"
        print(f"[Command Output]: {error_msg}")
        return error_msg

def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY environment variable is not set.")
        print("Please export it before running this script: export GEMINI_API_KEY='your_api_key'")
        return

    # Initialize the new google-genai client
    client = genai.Client()

    system_prompt = """You are an AI assistant that controls a Linux terminal.
You have access to a tool to execute bash commands.
Follow these rules:
1. When asked to perform a task, use the execute_command tool to do it.
2. Review the output of the command. If there is an error, think about why it failed and run a new command to fix it (Debug loop).
3. Be careful with destructive commands (like rm).
4. Break down complex tasks into multiple commands if necessary.
5. Once the task is fully complete, respond with a final message explaining what you did.
"""

    # We use automatic function calling feature of the new SDK
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[execute_command], # Pass the python function directly
        temperature=0.0,
    )
    
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=config
    )

    print("🤖 Gemini Linux Agent initialized! (Type 'exit' to quit)")
    
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            # In the google-genai SDK, passing callables to tools automatically executes them 
            # and returns the final response when it's done reasoning.
            response = chat.send_message(user_input)
            
            if response.text:
                print(f"\nAgent: {response.text}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            break

if __name__ == "__main__":
    main()
