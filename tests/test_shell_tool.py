from tools.shell_tool import ShellTool, ShellToolInput, ShellCommand
from toolkit import ToolKit

import pytest
import json


@pytest.mark.asyncio
async def test_shell_tool_echo_command():
    toolkit = ToolKit()
    tool = ShellTool(toolkit)

    command = ShellCommand(command="echo", arguments=["Hello World"])
    input_data = ShellToolInput(commands=[command])
    result = await tool.execute(input_data)

    # Note that we are using json.loads because ShellTool returns a json string.
    result_list = json.loads(result)
    assert len(result_list) == 1
    assert "Hello World" in result_list[0]
