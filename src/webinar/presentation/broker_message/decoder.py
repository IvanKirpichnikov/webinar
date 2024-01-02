from typing import Awaitable, Callable, cast

import lz4.frame
from faststream.nats import NatsMessage
from faststream.types import DecodedMessage
from orjson import loads


OriginalDecoder = Callable[[NatsMessage], Awaitable[DecodedMessage]]


async def decoder(
    msg: NatsMessage,
    original_decoder: OriginalDecoder,
) -> DecodedMessage:
    return cast(DecodedMessage, loads(lz4.frame.decompress(msg.body)))
