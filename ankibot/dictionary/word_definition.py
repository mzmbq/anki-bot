from dataclasses import dataclass

@dataclass
class WordDefinition:
    word: str
    definition: str
    examples: list[str]