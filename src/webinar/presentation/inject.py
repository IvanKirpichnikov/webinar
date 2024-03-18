from enum import auto, IntEnum
from inspect import Parameter
from typing import Any, Callable, cast, Container, Final

from dishka.integrations.base import wrap_injection


class InjectStrategy(IntEnum):
    GETTER = auto()
    HANDLER = auto()
    RENDER_KB = auto()
    RENDER_TEXT = auto()
    AIOGD_HANDLER = auto()
    AIOHTTP_HANDLER = auto()


CONTAINER_KEY: Final = 'dishka_container'
CONTAINER_GETTERS: Final = {
    InjectStrategy.HANDLER: lambda _, p: p[CONTAINER_KEY],
}


def inject(strategy: InjectStrategy) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        additional_params = []
        
        if strategy == InjectStrategy.HANDLER:
            additional_params = [
                Parameter(
                    name="dishka_container",
                    annotation=Container,
                    kind=Parameter.KEYWORD_ONLY,
                )
            ]
        return cast(
            Callable[..., Any], wrap_injection(
                func=func,
                remove_depends=True,
                container_getter=CONTAINER_GETTERS[strategy],
                additional_params=additional_params,
                is_async=True,
            )
        )
    
    return wrapper
