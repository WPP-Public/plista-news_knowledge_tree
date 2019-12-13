from dotenv import load_dotenv
from pprint import pprint
from newsapi import NewsApiClient
import urllib
import os
from bs4 import BeautifulSoup
from readability import Document
from find_entity import find_entity, tagger
import pickle
import pandas as pd
from mysql_caching import set_cache_entities, get_cached_entities
import functools

load_dotenv()

newsapi = NewsApiClient(api_key=os.environ.get("GOOGLE_NEWS_API"))


@functools.lru_cache(maxsize=512)
def html2text(url: str) -> str:
    html = urllib.request.urlopen(url).read()
    doc = Document(html)
    cleaned = "<h2>" + doc.short_title() + "</h2><br/>" + doc.summary()
    soup = BeautifulSoup(cleaned, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)
    return text


def process_headlines(language="en", country="gb"):
    top_headline = newsapi.get_top_headlines(
        language=language, country=country, page_size=100
    )
    result = []
    for article in top_headline["articles"]:
        try:

            article["text"] = html2text(article["url"])
            entities = get_cached_entities(article["url"])
            if entities is None:
                entities = find_entity(article["text"])
                set_cache_entities(article["url"], entities)
            article["entities"] = entities
            print("Worked for", article["url"], flush=True)
            result.append(article)
        except urllib.error.HTTPError as e:
            print(f"cannot fetch for", article["url"], e, flush=True)

    df = pd.DataFrame(result)
    with open("headline_google.pickle", "wb") as output_file:
        pickle.dump(df, output_file)
    return df.to_json()


if __name__ == "__main__":
    process_headlines()
