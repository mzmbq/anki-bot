from ankibot.dictionary.word_definition import WordDefinition


class Dictionary:
    def __init__(self):
        pass

    def contains(self, word: str) -> bool:
        return False

    def get_definitions(self, word: str) -> list[WordDefinition]:
        return []


# CambridgeDictionary().contains("fixture")
