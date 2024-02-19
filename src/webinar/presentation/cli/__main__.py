import asyncio
import sys
from argparse import ArgumentParser

from webinar.presentation.cli import start


def start_handler(arg: str) -> None:
    if arg == "tgbot":
        return asyncio.run(start.tgbot())
    if arg == "broker_message":
        return asyncio.run(start.broker_message())
    if arg == "application":
        return asyncio.run(start.application())
    raise KeyError


def main() -> None:
    argparse = ArgumentParser(description="webinar application")
    argparse.add_argument("--start", dest="start", type=str)
    args = argparse.parse_args()
    
    if sys.platform == "win32":
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    
    if start_arg := args.start:
        try:
            start_handler(start_arg)
        except KeyError:
            argparse.error("not found start argument: %s" % (start_arg,))
    return None


if __name__ == "__main__":
    main()
