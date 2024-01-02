from typing import Final


WORDS_IN_STR: Final = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
WORDS_IN_DICT: Final = {word: index for index, word in enumerate(WORDS_IN_STR)}


def parse_letters_range(raw_range_str: str) -> str:
    range_str = raw_range_str.lower().split("-")
    if len(range_str) != 2:
        raise ValueError
    indices = [WORDS_IN_DICT[i] for i in range_str]
    return WORDS_IN_STR[indices[0] : indices[1] + 1]
