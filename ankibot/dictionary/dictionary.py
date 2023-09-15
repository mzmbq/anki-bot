from ankibot.dictionary.word_definition import WordEntry

from abc import ABC, abstractmethod


class Dictionary(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __contains__(self, word: str) -> bool:
        return False

    @abstractmethod
    def __getitem__(self, word: str) -> list[WordEntry]:
        return []


class DictionaryError(Exception):
    pass
