from typing import Literal, NewType, TypeAlias


HomeWorkNumber: TypeAlias = Literal[1, 2, 3, 4, 5, 6, 7]
UserDataBaseId = NewType("UserDataBaseId", int)
DataBaseId = NewType("DataBaseId", int)
TelegramUserId = NewType("TelegramUserId", int)
TelegramChatId = NewType("TelegramChatId", int)
