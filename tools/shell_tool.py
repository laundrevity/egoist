from tools.base_tool import BaseTool

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import subprocess
import json


class ShellCommand(BaseModel):
    command: str = Field(description="Command to execute")
    arguments: Optional[List[str]] = Field(
        default=None, description="Optional arguments to pass to command"
    )


class ShellToolInput(BaseModel):
    commands: List[ShellCommand] = Field(
        description="List of shell commands to execute"
    )


class ShellTool(BaseTool):
    input_model = ShellToolInput
    description = "Execute a list of shell commands and return stdout (and stderr if returncode is nonzero)"

    async def execute(self, input_data: ShellToolInput) -> str:
        # input_data = ShellToolInput.model_validate_json(args)
        commands = input_data.commands

        results = []

        for shell_command in commands:
            command_str = (
                shell_command.command
                + " "
                + " ".join(shell_command.arguments if shell_command.arguments else [])
            )
            result = subprocess.run(command_str, capture_output=True, shell=True)

            if result.returncode != 0:
                results.append(
                    f"Got error in shell command! {result.stdout=}, {result.stderr=}"
                )
            else:
                results.append(result.stdout.decode())

        return json.dumps(results)


if __name__ == "__main__":
    print(ShellToolInput.model_json_schema())
