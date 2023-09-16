from ankibot.dictionary.word_definition import WordEntry
from ankibot.dictionary.dictionary import Dictionary
from ankibot.dictionary.dictionary import DictionaryError

import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

URL_PREFIX = "https://dictionary.cambridge.org/dictionary/english/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"}

class CambridgeDictionary(Dictionary):
    """
    This dictionary gets definitions from the Cambridge Dictionary page
    """

    def __init__(self) -> None:
        self.cache: dict[str, list[WordEntry]] = {}


    def __contains__(self, word: str) -> bool:
        if word in self.cache:
            return True

        word_url = URL_PREFIX + word
        try:
            response = requests.get(word_url, headers=HEADERS)
        except Exception as e:
            logger.exception(f"Get request failed for word: '{word}'")
            raise
        
        # if there is no page for the word we are getting redirected to https://dictionary.cambridge.org/dictionary/english/
        page_exists = response.url.split("/")[-1] != ""

        if page_exists:
            self.cache[word] = self.parse_definitions(response.text)
        return page_exists


    def __getitem__(self, word: str) -> list[WordEntry]:
        if word not in self.cache:
            if not self.__contains__(word):
                return []
        return self.cache[word]


    def parse_definitions(self, html_doc: str) -> list[WordEntry]:
        soup = BeautifulSoup(html_doc, "html.parser")

        # TODO: fix missing word
        result = []
        word_element = soup.find("div", {"span": "hw dhw"})
        definition_blocks = soup.find_all("div", {"class": "def-block ddef_block"})

        if len(definition_blocks) == 0:
            raise DictionaryError("Parser failed")

        for b in definition_blocks:
            definition_element = b.find("div", {"class": "def ddef_d db"}).get_text()
            definition_element = definition_element[:-1]

            examples = []
            for ex in b.find_all("span", {"class": "eg deg"}):
                examples.append(ex.get_text())

            result.append(WordEntry(word_element, definition_element, examples))
        return result


# CambridgeDictionary().get_definitions("fixture")
