from tools.chain_tool import ChainTool, ChainToolInput, ChainToolStep
from toolkit import ToolKit

import pytest
import json


@pytest.mark.asyncio
async def test_chain_tool_single_step():
    tk = ToolKit()
    tool = ChainTool(tk)

    # Define the chain with a single step.
    input_data = ChainToolInput(
        steps=[
            ChainToolStep(
                tool_name="ShellTool",
                step_id="singleStep",
                tool_args={
                    "commands": [{"command": "echo", "arguments": ["Hello, World!"]}]
                },
            )
        ]
    )

    # Execute the ChainTool with the defined single step.
    result = await tool.execute(input_data)

    # Deserialize the JSON result to check the individual step result.
    results = json.loads(result)
    assert (
        "Hello, World!" in results["singleStep"]
    ), "The chain did not execute the single step correctly."


@pytest.mark.asyncio
async def test_chain_tool_two_steps_with_substitution():
    tk = ToolKit()
    tool = ChainTool(tk)

    step1_id = "firstStep"
    step2_id = "secondStep"

    # Define the chain with two steps where the second step uses the result of the first.
    input_data = ChainToolInput(
        steps=[
            ChainToolStep(
                tool_name="ShellTool",
                step_id=step1_id,
                tool_args={
                    "commands": [{"command": "echo", "arguments": ["First Step"]}]
                },
            ),
            ChainToolStep(
                tool_name="ShellTool",
                step_id=step2_id,
                tool_args={
                    "commands": [
                        {
                            "command": "echo",
                            "arguments": ["${firstStep} then Second Step"],
                        }
                    ]
                },
            ),
        ]
    )

    # Execute the ChainTool with the defined steps.
    result = await tool.execute(input_data)

    # Deserialize the JSON result to check the individual step result.
    results = json.loads(result)
    result_str = results[step2_id]
    assert (
        "First Step then Second Step" == result_str
    ), "The chain did not execute the two steps with substitution correctly."
