from conversation import Conversation
import argparse
import asyncio


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
    args = parser.parse_args()

    conversation = Conversation(args)
    await conversation.run()


if __name__ == "__main__":
    asyncio.run(main())
