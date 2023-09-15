from dataclasses import dataclass

@dataclass
class WordEntry:
    word: str
    definition: str
    examples: list[str]
    
    def __str__(self) -> str:
        examples_list = "\n".join(["- " + e for e in self.examples])
        return f"{self.word}\n{self.definition}\n{examples_list}"