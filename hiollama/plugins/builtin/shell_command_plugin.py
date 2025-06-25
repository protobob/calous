"""
Shell Command Plugin for HiOllama

Allows execution of shell commands prefixed with '!' in user input.
This plugin is for private, trusted environments only.
"""

import subprocess
import os
from typing import Dict, Any
from ..base import HookPlugin

class ShellCommandPlugin(HookPlugin):
    def __init__(self):
        super().__init__(
            name="shell_command",
            version="1.0.0",
            description="Executes shell commands prefixed with ! in user input."
        )
        self.shell_env = None

    def initialize(self) -> bool:
        # Detect user's login shell and fetch full environment
        shell = os.environ.get("SHELL", "/bin/bash")
        try:
            # Fetch environment using login shell
            result = subprocess.run(
                [shell, "-l", "-c", "env"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                env_lines = result.stdout.strip().split("\n")
                env_dict = {}
                for line in env_lines:
                    if "=" in line and line.strip():
                        try:
                            key, value = line.split("=", 1)
                            env_dict[key] = value
                        except ValueError:
                            continue
                # Explicitly append /usr/local/bin to PATH
                env_dict["PATH"] = f"{env_dict.get('PATH', '')}:/usr/local/bin"
                self.shell_env = env_dict
                print("[DEBUG] Updated environment PATH:", self.shell_env["PATH"])
            else:
                self.shell_env = dict(os.environ)
        except Exception as e:
            print(f"Shell plugin initialization error: {e}")
            self.shell_env = dict(os.environ)
        return True

    def pre_message_hook(self, user_input: str, context: Dict[str, Any]) -> str:
        user_input = user_input.strip()
        if user_input.startswith("!") and len(user_input) > 1:
            command = user_input[1:].strip()
            shell = None
            if self.shell_env and "SHELL" in self.shell_env and self.shell_env["SHELL"]:
                shell = self.shell_env["SHELL"]
            else:
                shell = os.environ.get("SHELL") or "/bin/bash"
            
            try:
                # Source shell config files before running the command
                full_cmd = f"source ~/.bashrc 2>/dev/null || true; source ~/.bash_profile 2>/dev/null || true; source ~/.profile 2>/dev/null || true; {command}"
                result = subprocess.run(
                    [shell, "-l", "-c", full_cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10,
                    env=self.shell_env or dict(os.environ)
                )
                
                output = ""
                if result.stdout:
                    output += result.stdout.strip()
                if result.stderr:
                    if output:
                        output += "\n"
                    output += result.stderr.strip()
                
                if not output:
                    output = "[No output]"
                
                return f"[shell: {command}]\n{output}"
            except subprocess.TimeoutExpired:
                return f"[shell: {command}]\nError: Command timed out"
            except Exception as e:
                return f"[shell: {command}]\nError: {e}"
        return user_input
