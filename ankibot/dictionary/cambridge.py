from ankibot.dictionary.word_definition import WordDefinition
from ankibot.dictionary.dictionary import Dictionary
from ankibot.dictionary.dictionary import DictionaryError

import requests
from bs4 import BeautifulSoup


class CambridgeDictionary(Dictionary):
    """
    This dictionary gets definitions from the Cambridge Dictionary page
    """

    def __init__(self) -> None:
        self.url = "https://dictionary.cambridge.org/dictionary/english/"
        self.cache: dict[str, list[WordDefinition]] = {}

    def contains(self, word: str) -> bool:
        word_page = self.url + word

        try:
            response = requests.get(word_page, headers={
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"})
        except Exception as e:
            # TODO: add logging
            print(e)
            return False

        # response url = "https://dictionary.cambridge.org/dictionary/english/" if the page doesn't exist
        # "https://dictionary.cambridge.org/dictionary/english/word" otherwise

        page_exists = response.url.split("/")[-1] != ""

        if page_exists:
            self.cache[word] = self.parse_definitions(response.text)

        return page_exists

    def get_definitions(self, word: str) -> list[WordDefinition]:
        if word not in self.cache:
            if not self.contains(word):
                return []

        return self.cache[word]

    def parse_definitions(self, html_doc: str) -> list[WordDefinition]:
        soup = BeautifulSoup(html_doc, "html.parser")

        result = []
        word = soup.find("div", {"span": "hw dhw"})
        blocks = soup.find_all("div", {"class": "def-block ddef_block"})
        
        if len(blocks) == 0:
            raise DictionaryError("Parser failed")
        
        for b in blocks:
            definition = b.find("div", {"class": "def ddef_d db"}).get_text()
            definition = definition[:-1]

            examples = []
            for ex in b.find_all("span", {"class": "eg deg"}):
                examples.append(ex.get_text())

            result.append(WordDefinition(word, definition, examples))

        return result


# CambridgeDictionary().get_definitions("fixture")
