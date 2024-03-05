from typing import Literal, NewType


HomeWorkNumber = Literal[1, 2, 3, 4, 5, 6, 7]
UserDataBaseId = NewType("UserDataBaseId", int)
DataBaseId = NewType("DataBaseId", int)
TgUserId = NewType("TgUserId", int)
TgChatId = NewType("TgChatId", int)
