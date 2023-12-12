import pytest
from toolkit import ToolKit
from tools.exec_tool import ExecTool, ExecToolInput


@pytest.mark.asyncio
async def test_exec_tool_execute_simple_code():
    toolkit = ToolKit()
    tool = ExecTool(toolkit)

    code = "x = 10\nprint(x)"
    input_data = ExecToolInput(code=code)
    result = await tool.execute(input_data)

    assert "10" in result  # Check if the output contains the expected result

@pytest.mark.asyncio
async def test_exec_tool_variable_persistence():
    toolkit = ToolKit()
    tool = ExecTool(toolkit)

    code_1 = "x = 10"
    code_2 = "print(x)"

    result_1 = await tool.execute(ExecToolInput(code=code_1))
    result_2 = await tool.execute(ExecToolInput(code=code_2))
    
    assert result_2.strip() == "10"

@pytest.mark.asyncio
async def test_exec_tool_import_function_def():
    toolkit = ToolKit()
    tool = ExecTool(toolkit)

    code_1 = "import random\n\ndef get_random_number():\n    return random.random()\n\nresult = get_random_number()\nresult"
    code_2 = "print(get_random_number())"

    _ = await tool.execute(ExecToolInput(code=code_1))
    result_2 = await tool.execute(ExecToolInput(code=code_2))

    random_number = float(result_2)
    
    assert 0 < random_number < 1
