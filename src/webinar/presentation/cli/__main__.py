import asyncio
import sys
from argparse import ArgumentParser
from asyncio import WindowsSelectorEventLoopPolicy

from webinar.presentation.cli import start


def start_handler(arg: str) -> None:
    if arg == "tgbot":
        return asyncio.run(start.tgbot())
    if arg == "broker_message":
        return asyncio.run(start.broker_message())
    if arg == "application":
        return asyncio.run(start.application())
    raise ValueError


def main() -> None:
    argparse = ArgumentParser(description="webinar application")
    argparse.add_argument("--start", dest="start", type=str)
    args = argparse.parse_args()

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    if start_arg := args.start:
        try:
            start_handler(start_arg)
        except ValueError:
            argparse.error("Not Found argument: %s" % (start_arg,))
    return None


if __name__ == "__main__":
    main()
