from tools.meta_tool import MetaTool, MetaToolInput
from toolkit import ToolKit
import pytest
import json

@pytest.mark.asyncio
async def test_meta_tool_valid_call():
    toolkit = ToolKit()
    meta_tool = MetaTool(toolkit)

    # Prepare the input data for the SnapTool,
    # which is a known valid tool with a sample valid argument
    snap_tool_args = {
        "line_numbers": True,
        "infra_files": False,
    }

    # Create a MetaToolInput with the tool_name set to "SnapTool"
    # and the arguments for the SnapTool
    input_data = MetaToolInput(tool_name="SnapTool", tool_args=snap_tool_args)
    
    # Execute the MetaTool
    result = await meta_tool.execute(input_data)

    # Verify the result contains some expected output characteristics
    assert isinstance(result, str)
    assert "--- toolkit.py ---" in result   # Check for a known file header in the output

@pytest.mark.asyncio
async def test_meta_tool_invalid_tool_name():
    toolkit = ToolKit()
    meta_tool = MetaTool(toolkit)

    # Purposefully use an invalid tool name to test error handling
    input_data = MetaToolInput(tool_name="InvalidToolName", tool_args={})

    # Execute the MetaTool
    result = await meta_tool.execute(input_data)

    # The result should contain an error message indicating the tool name is invalid
    assert "Error" in result
    assert "InvalidToolName" in result

@pytest.mark.asyncio
async def test_meta_tool_invalid_tool_args():
    toolkit = ToolKit()
    meta_tool = MetaTool(toolkit)

    # Use a valid tool name but provide invalid arguments to test error handling
    input_data = MetaToolInput(tool_name="SnapTool", tool_args={"nonexistent_arg": True})

    # Execute the MetaTool
    result = await meta_tool.execute(input_data)

    # The result should contain an error message indicating the tool arguments are invalid
    assert "Error" in result
    assert "nonexistent_arg" in result

@pytest.mark.asyncio
async def test_meta_tool_call_shell_tool_echo():
    toolkit = ToolKit()
    meta_tool = MetaTool(toolkit)

    # Prepare the input data for the ShellTool to perform the echo command
    shell_tool_args = {
        "commands": [{
            "command": "echo",
            "arguments": ["hello world"]
        }]
    }

    # Create a MetaToolInput with the tool_name set to "ShellTool"
    # and the arguments for the ShellTool
    input_data = MetaToolInput(tool_name="ShellTool", tool_args=shell_tool_args)
    
    # Execute the MetaTool
    result = await meta_tool.execute(input_data)

    # The ShellTool returns array of outputs as a JSON string.
    # Load the result to work with the actual list of outputs
    result_list = json.loads(result)

    # Verify the execution result of the shell command
    assert len(result_list) == 1
    assert result_list[0].strip() == "hello world", "The shell did not return the expected output."