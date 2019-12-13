import functools
import sys
from typing import Set

import nltk
from flair.data import Sentence
from flair.models import SequenceTagger
from langdetect import detect

tagger = {"de": SequenceTagger.load("de-ner"), "en": SequenceTagger.load("ner")}


def filter_text(text: str) -> str:
    """remove unwanted character from the text which can disturb NER"""
    filtered = text
    for s in "\\\xa0\"'[]()’“”\xad":
        filtered = filtered.replace(s, "")
    return filtered


def format_entities(entity: Set[str]) -> Set[str]:
    """
    Remove
    :param entity:
    :return:
    """
    if entity[-1] in [".", ",", "?", "!", ":"]:
        entity = entity[0:-1]
    entity = entity.replace("\n", " ")
    if entity == "German":
        entity = "Germany"
    return entity


@functools.lru_cache(maxsize=512)
def find_entity(text: str) -> Set[str]:
    """extract entity using flair"""
    global tagger
    filtered = filter_text(text)
    language = detect(filtered)
    if language not in tagger:
        return set()
    sent_tokens = nltk.sent_tokenize(filtered)
    sentences = [Sentence(i) for i in sent_tokens]
    tagger[language].predict(sentences)
    flair_entities = []
    for sentence in sentences:
        flair_entities.extend(
            [format_entities(entity.text) for entity in sentence.get_spans("ner")]
        )
    result = set(flair_entities)
    return result


if __name__ == "__main__":
    text = sys.argv[1]
    print(find_entity(text))
