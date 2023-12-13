from conversation import Conversation
from openai_service import InterruptFlag
import argparse
import asyncio
import signal


def stream_signal_handler(flag: InterruptFlag):
    flag.set_streaming_interrupt(True)


async def main():
    parser = argparse.ArgumentParser(
        prog="egoist",
        description="An agent capable of taking actions in its environment via tool calls and communicating with a user",
    )
    parser.add_argument("prompt")
    parser.add_argument(
        "-s",
        "--state",
        action="store_true",
        help="Include state data in initial system prompt",
    )
    parser.add_argument(
        "-r",
        "--return-mode",
        action="store_true",
        help="Return the response to the initial prompt, rather than initiating an interactive session",
    )
    args = parser.parse_args()

    # Prevent default asyncio CTRL+C handling so Conversation can handle it
    flag = InterruptFlag()
    # Set up the CTRL+C handler for streaming interruption
    asyncio.get_running_loop().add_signal_handler(
        signal.SIGINT, stream_signal_handler, flag
    )
    conversation = Conversation(args, flag)
    result = await conversation.run()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
