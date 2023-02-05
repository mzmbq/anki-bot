from ankibot.dictionary.word_definition import WordDefinition

import requests


class Dictionary:
    def __init__(self):
        pass

    def contains(self, word: str) -> bool:
        return False

    def get_definitions(self, word: str) -> list[WordDefinition]:
        return []


class CambridgeDictionary(Dictionary):
    """
    This dictionary gets definitions from the Cambridge Dictionary page
    """

    def __init__(self):
        self.url = "https://dictionary.cambridge.org/dictionary/english/"

    def contains(self, word: str) -> bool:
        word_page = self.url + word

        try:
            response = requests.get(word_page, headers={"User-Agent": "Mozilla/5.0"})
        except Exception as e:
            # TODO: add logging
            print(e.message)
            return False

        # response url = "https://dictionary.cambridge.org/dictionary/english/" if the page doesn't exist
        # "https://dictionary.cambridge.org/dictionary/english/word" otherwise

        return response.url.split("/")[-1] != ""

    def get_definitions(self, word: str) -> list[WordDefinition]:
        return []


# CambridgeDictionary().contains("fixture")
