from openai_service import OpenAIService
from toolkit import ToolKit
from models import Message
from typing import List
from rich import print
import argparse
import asyncio
import json


class Conversation:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.messages: List[Message] = self.initialize_messages()
        self.toolkit = ToolKit()
        # assume we always want to use the latest model, gpt-4-1106-preview
        self.openai_service = OpenAIService(
            self.toolkit.get_tools_json(), verbose=False
        )

    async def run(self):
        while True:
            # get a message from GPT
            message = await self.openai_service.get_message(self.messages, tools=True)
            self.messages.append(message)

            if message.tool_calls:
                tool_call_tasks = []
                for tool_call in message.tool_calls:
                    tool_call_tasks.append(
                        asyncio.create_task(self.toolkit.execute_tool(tool_call))
                    )
                results = await asyncio.gather(*tool_call_tasks)

                print("=> ")
                for result in results:
                    try:
                        result_json = json.loads(result.replace("\n", ""))
                        print(json.dumps(result_json, indent=4))
                    except json.JSONDecodeError:
                        print(result)

                for result, tool_call in zip(results, message.tool_calls):
                    self.add_message(
                        Message(
                            role="tool",
                            content=result,
                            tool_call_id=tool_call.id,
                            name=tool_call.function.name,
                        )
                    )

                # Now get a message without tool calls
                message = await self.openai_service.get_message(
                    self.messages, tools=False
                )

            user_input = self.get_input()
            self.messages.append(Message(role="user", content=user_input))

    def get_input(self) -> str:
        while True:
            user_input = input("> ")
            if user_input == "list tools":
                print("Available tools:")
                for tool_name, tool in self.toolkit.tools.items():
                    print(f"{tool_name} --- {tool.description}")
            else:
                break
        return user_input

    def initialize_messages(self):
        messages = []
        system_prompt = "You are an AI program with agency. You can choose to respond to the user with text, or use the tools that are exposed to you. Do not use tools if you can answer the question easily, such as `what is 2+2`."
        if self.args.state:
            print("including system state")
            system_prompt += f"Current project source code:\n{open('state.txt').read()}"
        messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=self.args.prompt))

        return messages

    def get_messages_json(self):
        jsons = []
        for message in self.messages:
            jsons.append(message.model_dump(exclude_unset=True, exclude_none=True))
        return jsons

    def add_message(self, message: Message):
        self.messages.append(message)
