from openai_service import OpenAIService, InterruptFlag
from toolkit import ToolKit
from models import Message
from typing import List
from rich import print
import datetime
import argparse
import asyncio
import json
import os


class Conversation:
    def __init__(self, args: argparse.Namespace, flag: InterruptFlag) -> None:
        self.args = args
        self.flag = flag
        self.messages: List[Message] = []
        self.conversation_id = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.initialize_messages()
        self.toolkit = ToolKit()
        # assume we always want to use the latest model, gpt-4-1106-preview
        self.openai_service = OpenAIService(
            self.toolkit.get_tools_json(), flag, verbose=False
        )
        self.force = False

    async def run(self):
        while True:
            # get a message from GPT
            message = await self.openai_service.get_message(self.messages, tools=True, force=self.force)
            self.add_message(message)

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
                self.add_message(message)

            if self.args.return_mode:
                return message.content

            user_input = self.get_input()

            self.add_message(Message(role="user", content=user_input))

    def get_input(self) -> str:
        self.force = False
        while True:
            try:
                user_input = input("> ")
                if user_input == "list tools":
                    print(f"Tool menu:")
                    for tool_name, tool in self.toolkit.tools.items():
                        print(f"{tool_name} --- {tool.description}")

                elif user_input == "read":
                    return open("prompt.txt").read()
                
                elif user_input.startswith("force "):
                    self.force = True
                    return user_input[len("force "):]

                else:
                    return user_input
            except EOFError:
                print(f"CTRL+D detected, exiting program...")
                exit(0)

    def initialize_messages(self):
        system_prompt = "You are an AI program with agency. You can choose to respond to the user with text, or use the tools that are exposed to you. Do not use tools if you can answer the question easily, such as `what is 2+2`."
        if self.args.state:
            print("including system state")
            system_prompt += f"Current project source code:\n{open('state.txt').read()}"

        self.add_message(Message(role="system", content=system_prompt))
        self.add_message(Message(role="user", content=self.args.prompt))

    def get_messages_json(self):
        jsons = []
        for message in self.messages:
            jsons.append(message.model_dump(exclude_unset=True, exclude_none=True))
        return jsons

    def add_message(self, message: Message):
        conversations_dir = os.path.join(os.getcwd(), "conversations")
        if not os.path.exists(conversations_dir):
            os.makedirs(conversations_dir)
        self.messages.append(message)

        conversation_path = os.path.join(
            conversations_dir, f"{self.conversation_id}.json"
        )
        with open(conversation_path, "w") as fp:
            json.dump(self.get_messages_json(), fp, indent=4)
