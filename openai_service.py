from models import Message, StreamChunk, ToolCall

from pydantic import ValidationError
from typing import List, Dict
from rich import print
import asyncio
import httpx
import json
import os


class StreamingInterruptedException(Exception):
    def ___init__(self, message):
        super().__init__(message)


class InterruptFlag:
    def __init__(self):
        self.streaming_interrupted = False
        self.user_input_interrupted = False

    def set_streaming_interrupt(self, value: bool):
        self.streaming_interrupted = value

    def get_streaming_interrupt(self) -> bool:
        return self.streaming_interrupted

    def set_user_input_interrupt(self, value: bool):
        self.user_input_interrupted = value

    def get_user_input_interrupt(self) -> bool:
        return self.user_input_interrupted


class OpenAIService:
    def __init__(self, tools_json: List[Dict], flag: InterruptFlag, verbose=False):
        self.tools_json = tools_json
        self.flag = flag
        self.verbose = verbose
        self.timeout = 300

        self.client = httpx.AsyncClient()
        bearer_token = f"Bearer {os.getenv('OPENAI_API_KEY')}"
        self.headers = {
            "Authorization": bearer_token,
            "Content-Type": "application/json",
        }
        self.url = "https://api.openai.com/v1/chat/completions"

    async def get_message(self, messages: List[Message], tools: bool = False):
        payload = {
            "messages": [
                message.model_dump(exclude_unset=True) for message in messages
            ],
            "model": "gpt-4-1106-preview",
            "stream": True,
        }
        if tools:
            payload["tools"] = self.tools_json

        try:
            stream_chunks = await self.get_stream_chunks(payload)
            message = self.parse_stream_chunks(stream_chunks)
        except StreamingInterruptedException as e:
            print(e)
            message = Message(
                role="system", content="\nStreaming response interrupted by user."
            )

        if self.verbose:
            print(f"Received message: {message}")

        return message

    async def get_stream_chunks(self, payload: Dict) -> List[StreamChunk]:
        print("Assistant: ", end="")
        chunks = []
        bad_status_code = False

        async with self.client.stream(
            "POST", self.url, json=payload, headers=self.headers, timeout=300
        ) as response:
            if response.status_code != 200:
                bad_status_code = True
                await response.aread()

            if not bad_status_code:
                self.flag.set_streaming_interrupt(False)

                async for line in response.aiter_lines():
                    # print(line, flush=True)

                    trim_line = line[6:]

                    if trim_line and not self.flag.get_streaming_interrupt():
                        try:
                            line_json = json.loads(trim_line)

                            try:
                                stream_chunk = StreamChunk.model_validate(line_json)

                                content = stream_chunk.choices[0].delta.content
                                if content:
                                    print(content, end="")

                                tool_calls = stream_chunk.choices[0].delta.tool_calls
                                if tool_calls:
                                    tool_call_function = tool_calls[0].function
                                    if tool_call_function.name:
                                        print(f"{tool_call_function}: ", end="")
                                    if tool_call_function.arguments:
                                        print(tool_call_function.arguments, end="")

                                chunks.append(stream_chunk)
                                if self.verbose:
                                    print(stream_chunk)

                            except ValidationError as e:
                                if self.verbose:
                                    print(f"ValidationError parsing {line_json}: {e}")

                            # print(json.dumps(line_json, indent=4), flush=True)

                        except json.JSONDecodeError:
                            if trim_line == "[DONE]":
                                if self.verbose:
                                    print(f"Finished consuming stream.")
                            else:
                                if self.verbose:
                                    print(f"Got JSON decode error on line: {trim_line}")

                    if self.flag.get_streaming_interrupt():
                        raise StreamingInterruptedException(
                            "Streaming interrupted by user."
                        )

        if bad_status_code:
            print(
                f"Got bad status code: {response.status_code}, {response.content=}\npayload: {json.dumps(payload, indent=4)}"
            )

        print("")

        return chunks

    def parse_stream_chunks(self, chunks: List[StreamChunk]) -> Message:
        # Initialize empty Message object
        message = Message(role="assistant")

        # Initialize empty content string and tool_calls list
        content = ""
        tool_calls: List[ToolCall] = []

        # We will track whether we are inside a tool call or not
        inside_tool_call = False

        if chunks:
            first_choice = chunks[0].choices[0]
            if first_choice.delta.role == "assistant" and first_choice.delta.tool_calls:
                tool_calls.append(first_choice.delta.tool_calls[0])
                inside_tool_call = True

        for chunk in chunks:
            # Assume that we only care about the first choice in each chunk
            choice = chunk.choices[0]
            delta = choice.delta

            if (
                delta.role == "assistant"
                and delta.content is None
                and delta.tool_calls is None
            ):
                # The beginning of either text response or tool call sequence
                continue
            elif delta.role is None and delta.content is not None:
                # Accumulate the text response content
                content += delta.content
            elif delta.role is None and delta.tool_calls:
                # Handle the tool call sequence
                for tool_call in delta.tool_calls:
                    # If we encounter a new full ToolCall object, we are starting a new tool call
                    if tool_call.id:
                        tool_calls.append(tool_call)
                        inside_tool_call = True

                    elif inside_tool_call:
                        # We are in the middle of processing a tool call, so we accumulate argument data
                        # NOTE: This assumes that `arguments` are being sent in the correct sequence
                        last_tool_call = tool_calls[-1]
                        if last_tool_call.function.arguments is None:
                            last_tool_call.function.arguments = ""
                        last_tool_call.function.arguments += (
                            tool_call.function.arguments
                        )
            elif choice.finish_reason == "stop":
                # End of a text response sequence
                break
            elif choice.finish_reason == "tool_calls":
                # End of a tool call sequence
                break

        if content:
            message.content = content
        else:
            message.tool_calls = tool_calls

        return message
