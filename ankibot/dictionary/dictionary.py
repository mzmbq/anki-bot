from abc import ABC, abstractmethod

from ankibot.dictionary.word_definition import WordEntry
from ankibot.errors import AnkiBotError



class Dictionary(ABC):
    """Base class for all dictionary implementations."""

    @staticmethod
    @abstractmethod
    def display_name() -> str:
        """
        Display name of the dictionary.
        """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __contains__(self, word: str) -> bool:
        return False

    @abstractmethod
    def __getitem__(self, word: str) -> list[WordEntry]:
        return []


class DictionaryError(AnkiBotError):
    """Base class for all dictionary errors."""
