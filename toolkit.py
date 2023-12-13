from tools.base_tool import BaseTool
from pydantic import ValidationError
from typing import List, Dict
from models import ToolCall
from rich import print
import importlib
import pkgutil
import inspect
import json


class ToolKit:
    def __init__(self) -> None:
        self.tools: Dict[str, BaseTool] = self.load_tools()

    # Separate discovery into atomic and complex tools
    def load_tools(self):
        tools_package = importlib.import_module("tools")
        tools = {}
        for _, name, ispkg in pkgutil.iter_modules(
            tools_package.__path__, tools_package.__name__ + "."
        ):
            if not ispkg:
                module = importlib.import_module(name)
                for member_name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, BaseTool)
                        and member_name != "BaseTool"
                    ):
                        tools[member_name] = obj(self)

        return tools

    def get_tools_json(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool.description,
                    "parameters": tool.input_model.model_json_schema(),
                },
            }
            for tool_name, tool in self.tools.items()
        ]

    async def execute_tool(self, tool_call: ToolCall) -> str:
        user_allowed = input(f"execute {tool_call}?\n(y/n) ")
        if user_allowed.lower() == "y":
            name = tool_call.function.name
            if name not in self.tools:
                return f"Error: {name} not in {self.tools.keys()=}"
            else:
                print(f"{tool_call.function.arguments=}")
                tool = self.tools[name]

                try:
                    tool_input = tool.input_model.model_validate(
                        json.loads(tool_call.function.arguments)
                    )
                    return await tool.execute(tool_input)
                except ValidationError as e:
                    error_str = f"Error validating {tool_call.function.arguments=}: {e}"
                    print(error_str)
                    return error_str
        else:
            return f"User rejected tool call: {tool_call}"


if __name__ == "__main__":
    tk = ToolKit()
    print(tk.get_tools_json())
