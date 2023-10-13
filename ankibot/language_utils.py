import logging

import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

def init_nltk():
    """Download required NLTK packages."""
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')


def _search_word(word: str, sentence: str) -> tuple[int, int] | None:
    """Find the first occurrence of a word in a sentence."""

    start_pos = sentence.find(word)
    if start_pos == -1:
        return None

    return (start_pos, start_pos + len(word))


def search_lemma(word: str, sentence: str, language: str) -> tuple[int, int] | None:
    """Find the first occurrence of a word (in any form) in a sentence.
        Returns a tuple (start, end+1) if the word is found, None otherwise."""

    if language.lower() == "en":
        return _search_lemma_en(word, sentence)
    else:
        raise NotImplementedError("Only english language is currently supported")


def _search_lemma_en(word: str, sentence: str) -> tuple[int, int] | None:
    """Find the first occurrence of a word (in any form) in a sentence.
        Returns a tuple (start, end+1) if the word is found, None otherwise."""

    tokens = word_tokenize(sentence)
    pos_tags = pos_tag(tokens)

    target_pos_tag = pos_tag([word])[0][1]

    lemmatizer = WordNetLemmatizer()

    target_lemma: str
    if target_pos_tag.startswith('V'):
        target_lemma = lemmatizer.lemmatize(word, pos='v')
    else:
        target_lemma = lemmatizer.lemmatize(word)
    target_lemma = target_lemma.lower()

    for i, (token, tag) in enumerate(pos_tags):
        if tag.startswith('V'):
            lemma = lemmatizer.lemmatize(token, pos='v')
        else:
            lemma = lemmatizer.lemmatize(token)

        if lemma.lower() == target_lemma:
            return _search_word(tokens[i], sentence)

    logger.info("Could not find word '%s' in sentence '%s'.", word, sentence)

    return None


# TODO: setup tests # pylint: disable=fixme
# # _word = "say"
# # sent = "Say what again said goodbye to all her friends and left."
# _word = "sein"
# sent = "Sie waren daußen"
# print(search_lemma(_word, sent))
