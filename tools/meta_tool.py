from tools.base_tool import BaseTool
from pydantic import BaseModel, Field, ValidationError
from typing import Dict


class MetaToolInput(BaseModel):
    tool_name: str = Field(..., description="Name of tool to call")
    tool_args: Dict = Field(..., description="Required JSON of arguments to pass to tool, must conform to tool input schema")

class MetaTool(BaseTool):
    input_model = MetaToolInput
    description = "Call a specified tool with the provided arguments. DO NOT USE THIS TOOL WITHOUT PROVIDING tool_args -- IT IS REQUIRED. Only use this tool if you provide both tool_name and tool_args in the input."

    async def execute(self, input_data: MetaToolInput) -> str:
        tool_name = input_data.tool_name
        if tool_name.startswith("functions."):
            tool_name = tool_name[len("functions."):]

        if tool_name == "MetaTool":
            return "I'm sorry but I cannot use the MetaTool to call the MetaTool as it might lead to infinite recursion."
        try:
            tool = self.toolkit.tools[tool_name]
            try:
                tool_input = tool.input_model.model_validate(input_data.tool_args)
                return await tool.execute(tool_input)
            except ValidationError as e:
                return f"Error validating input {input_data.tool_args} for {tool_name}: {e}"
        except KeyError:
            return f"Error: Could not execute MetaTool: {tool_name} not found in {self.toolkit.tools.keys()=}"
