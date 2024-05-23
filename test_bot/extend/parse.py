import re

# pip install thefuzz
from thefuzz import process

music_alias = ["поставь музыку", "включи музыку", "вруби музыку", "ёбни на пол карасика",
               "ёбни", "включ", "включи", "поставь", "вруби"]
prefix = "френд"
commands = [("music", music_alias)]


def strip_command(key: str, text: str) -> None | str:
    m = re.search(re.escape(key), text)
    if m is not None:
        index = m.end()
        # обрежем до пробела?
        while index < len(text) and text[index] != " ":
            index += 1
        return text[index + 1:]
    # TODO: не None
    return None


def parse_command(text: str) -> (str, str):
    """Parses a command from the given text.

    Returns:
        tuple: A tuple containing the command type (str) and the command parameters (str).
               If the text does not start with the prefix or if no command is found,
               returns (None, None)."""

    if text[:len(prefix)] != prefix:
        return None, None
    text = text[len(prefix):]

    # pr_index = text.find(prefix)
    # if pr_index == -1:
    #     return None, None
    # text = text[pr_index + len(prefix):]

    text = text.lower()
    for c_type, aliases in commands:
        key_word, score = process.extractOne(text, aliases) or ("", 0)
        if score >= 75:
            res = strip_command(key_word, text)
            if res is not None:
                return c_type, res

    return "gpt", text


if __name__ == '__main__':
    test = ["френд поставь музыку", "тест тест говорю говорю",
            "френд hui",
            "френд поставь музыку мейби бейби",
            "алё френд Алё бля ВключЭ мейбибейби",
            "френд Алё бля ВключЭ мейбибейби",
            "френд ёбни на пол карасика мейби бейби",
            "френд поставь слиппинг поудер гориллаз"]
    for i, v in enumerate(test, 1):
        print(f"{i}.", v, parse_command(v))
