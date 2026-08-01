import pexpect
import time
from langchain.tools import tool
import sys
import os

# Add the parent directory to sys.path so we can import agent.state
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.state import ToolResult

class PersistentShell:
    def __init__(self):
        # We use a very unique prompt so we know when the command finishes
        self.PROMPT = "[[AGENT_PROMPT_END]]"
        
        # Spawn bash without user profiles to keep it clean and predictable
        self.child = pexpect.spawn(
            '/bin/bash --norc --noprofile',
            encoding='utf-8',
            echo=False,
            timeout=30,
            dimensions=(24, 80)
        )
        
        # Set the prompt first so we can reliably wait for it
        self.child.sendline(f"export PS1='{self.PROMPT}'")
        self.child.expect_exact(self.PROMPT)
        
        # Disable echo so the command isn't repeated in the output
        self.child.sendline("stty -echo")
        self.child.expect_exact(self.PROMPT)
        
        # Also disable history and other noise
        self.child.sendline("export HISTFILE=/dev/null")
        self.child.expect_exact(self.PROMPT)
        
        # Set a clean environment
        self.child.sendline("export TERM=dumb")
        self.child.expect_exact(self.PROMPT)
        
        # clear buffer
        self.child.before = ""

    def run(self, command: str) -> ToolResult:
        start_time = time.time()
        try:
            # Send the command
            self.child.sendline(command)
            
            # Wait for the prompt to reappear
            match_index = self.child.expect_exact([self.PROMPT, pexpect.EOF, pexpect.TIMEOUT])
            
            if match_index == 1:
                return ToolResult(
                    success=False,
                    stderr="Error: Shell closed unexpectedly (EOF).",
                    tool_name="terminal",
                    duration=time.time() - start_time
                )
            elif match_index == 2:
                # If it times out, we should interrupt it so it doesn't bleed into the next command
                self.child.sendintr()
                self.child.expect_exact(self.PROMPT, timeout=5)
                return ToolResult(
                    success=False,
                    stderr="Error: Command timed out after 30 seconds. Process was interrupted.",
                    tool_name="terminal",
                    duration=time.time() - start_time
                )
                
            # The output includes the command's stdout and stderr interleaved
            output = self.child.before.strip()
            
            # Get the exit code
            self.child.sendline("echo $?")
            self.child.expect_exact(self.PROMPT)
            exit_code_str = self.child.before.strip()
            
            try:
                # Sometimes there are extra newlines, get the last line
                exit_code = int(exit_code_str.split('\n')[-1].strip())
            except:
                exit_code = -1
                
            # Get current working directory
            self.child.sendline("pwd")
            self.child.expect_exact(self.PROMPT)
            cwd = self.child.before.strip().split('\n')[-1].strip()

            # Clean up the output a bit
            lines = output.split('\r\n')
            if lines and command in lines[0]:
                lines = lines[1:]
            
            final_output = '\n'.join(lines).strip()
            
            if len(final_output) > 4000:
                final_output = final_output[:4000] + "\n...[Truncated]"

            return ToolResult(
                success=exit_code == 0,
                stdout=final_output if exit_code == 0 else "",
                stderr=final_output if exit_code != 0 else "",
                exit_code=exit_code,
                cwd=cwd,
                duration=time.time() - start_time,
                tool_name="terminal"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                stderr=f"Exception during execution: {str(e)}",
                tool_name="terminal",
                duration=time.time() - start_time
            )

# Create a singleton instance
try:
    shell_engine = PersistentShell()
except pexpect.exceptions.TIMEOUT:
    # Fallback initialization logic if the prompt setup fails
    shell_engine = None

@tool
def run_command(command: str) -> dict:
    """Executes a bash command in the persistent Linux terminal.
    Commands like 'cd' and 'export' will affect subsequent commands.
    """
    if shell_engine is None:
        return ToolResult(success=False, stderr="Shell engine failed to initialize.", tool_name="terminal").to_dict()
        
    result = shell_engine.run(command)
    return result.to_dict()
