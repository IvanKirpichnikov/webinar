from typing import Awaitable, Callable, cast

import lz4.frame
from faststream.nats import NatsMessage
from faststream.types import DecodedMessage
from orjson import orjson


async def decoder(
    msg: NatsMessage,
    original_decoder: Callable[[NatsMessage], Awaitable[DecodedMessage]],
) -> DecodedMessage:
    print(msg)
    return cast(
        DecodedMessage,
        orjson.loads(lz4.frame.decompress(msg.body))
    )
