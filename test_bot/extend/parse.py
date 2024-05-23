# pip install thefuzz
import re

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


def parse_command(text) -> (str, str):
    text.find(prefix)
    if text.find(prefix) == -1:
        return None, None
    text = text[text.find(prefix) + len(prefix):]
    text = text.lower()
    for type, aliases in commands:
        key_word, score = process.extractOne(text, aliases) or ("", 0)
        if score >= 75:
            res = strip_command(key_word, text)
            if res is not None:
                return type, res

    return "gpt", text


if __name__ == '__main__':
    test = ["поставь музыку", "тест тест говорю говорю",
            "hui",
            "поставь музыку мейби бейби",
            "Алё бля ВключЭ мейбибейби",
            "ёбни на пол карасика мейби бейби",
            "поставь слиппинг поудер гориллаз"]
    for i, v in enumerate(test, 1):
        print(parse_command(v), v)
