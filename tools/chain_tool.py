from tools.base_tool import BaseTool

from pydantic import BaseModel, Field
from typing import List, Dict
import traceback
import json


class ChainToolStep(BaseModel):
    tool_name: str = Field(..., description="Name of tool to call")
    tool_args: Dict = Field(
        description="Arguments to pass to tool, possibly including ${prevStepId} placeholders",
    )
    step_id: str = Field(
        "id of the step in the chain, so that its value can be propagated to placeholders in subsequent steps",
    )


class ChainToolInput(BaseModel):
    steps: List[ChainToolStep] = Field(
        ...,
        description="list of steps to execute",
        examples=[
            {
                "steps": [
                    {
                        "tool_name": "ShellTool",
                        "tool_args": {
                            "commands": [{"command": "echo", "arguments": "hello"}]
                        },
                        "step_id": "generateString",
                    },
                    {
                        "tool_name": "ShellTool",
                        "tool_args": {
                            "commands": [
                                {
                                    "command": "echo",
                                    "arguments": "${generateString} world",
                                }
                            ]
                        },
                        "step_id": "echoGeneratedString",
                    },
                ]
            }
        ],
    )


class ChainTool(BaseTool):
    input_model = ChainToolInput
    description = "Execute the given chain of tool calls with provided arguments, with the possibility of using placeholders ${prevStepId} to pass output from earlier steps to later ones."

    async def execute(self, input_data: ChainToolInput) -> str:
        results = {}
        for i, step in enumerate(input_data.steps):
            self.resolve_parameters(results, input_data.steps[i:])
            try:
                tool = self.toolkit.tools[step.tool_name]
                tool_input = tool.input_model.model_validate(step.tool_args)
                result = await tool.execute(tool_input)

                try:
                    result = json.loads(result)
                    if isinstance(result, List) and len(result) == 1:
                        result = result[0].strip()
                except:
                    pass

            except Exception as e:
                result = f"Error executing {step}: {e} {traceback.format_exc()}".strip()

            results[step.step_id] = result

        return json.dumps(results, indent=4)

    def resolve_parameters(
        self, results: Dict[str, str], remaining_steps: List[ChainToolStep]
    ):
        for step_id in results:
            placeholder = f"${{{step_id}}}"
            replacement = results[step_id]

            for step in remaining_steps:
                self.substitute_placeholder(placeholder, replacement, step.tool_args)

    def substitute_placeholder(
        self, placeholder: str, replacement: str, args: Dict | List
    ):
        if isinstance(args, Dict):
            for k, v in args.items():
                if isinstance(v, str):
                    args[k] = v.replace(placeholder, replacement)
                elif isinstance(v, Dict) or isinstance(v, List):
                    self.substitute_placeholder(placeholder, replacement, v)
        elif isinstance(args, List):
            for i, item in enumerate(args):
                if isinstance(item, str):
                    args[i] = item.replace(placeholder, replacement)
                elif isinstance(item, Dict) or isinstance(item, List):
                    self.substitute_placeholder(placeholder, replacement, item)
