import os
import pickle
from copy import deepcopy
import random
import json
from pandas import DataFrame
import pandas as pd
from typing import Tuple, Dict
import urllib
random.seed(30)


class NoValidArticle(Exception):
    """no article can be found with the given constraints"""
    pass

MAX_WIDTH = 7
MAX_LENGTH = 10

def process_dataframe(language, country):
    jdf = urllib.request.urlopen(f"http://data_processing:5001/get_headlines?language={language}&country={country}").read()
    df = pd.read_json(json.loads(jdf.decode("utf-8")))
    df["lower_entities"] = df.entities.apply(
        lambda entities_set: set([i.lower() for i in entities_set])
    )
    return df


def init_entity_counters(df: DataFrame) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    init the article
    :param df:
    :return:
    """
    article_entity_counter = {}
    for ent in df.lower_entities:
        for entity in ent:
            article_entity_counter[entity] = article_entity_counter.get(entity, 0) + 1

    text_entity_counter = {}
    for _, row in df.iterrows():
        text = row.text
        for entity in row.entities:
            text_entity_counter[entity.lower()] = text.count(
                entity
            ) + text_entity_counter.get(entity.lower(), 0)
    return article_entity_counter, text_entity_counter


def get_cased_entities(df: DataFrame) -> Dict[str, str]:
    """
    build dictionary to get upper cased entity from lower cased one
    :param df:
    :return:
    """
    cased_entities = {}
    for entities in df.entities:
        for entity in entities:
            if entity.lower() not in cased_entities:
                cased_entities[entity.lower()] = entity
            else:
                old_entity = cased_entities[entity.lower()]
                if n_uppercase(old_entity) < n_uppercase(entity):
                    cased_entities[entity.lower()] = entity
    return cased_entities


def n_uppercase(text):
    """
    Count number of upper case character in the text
    :param text: text to analise
    :return: number of upper case character
    """
    return sum([char.isupper() for char in text])



def validate_tree_size(tree, level=MAX_LENGTH, width=MAX_WIDTH):
    """
    Verify recursively than the tree is valid (ie each node has MAX_WIDTH)
    :param tree: tree to verify
    :param level: level on the tree we are (for recursion)
    :param width: number of children each node should have
    :return: Boolean to indicate if the tree is correct
    """
    if level == 1:
        return len(tree.get("children", [])) == width
    elif len(tree["children"]) != width:
        return False
    else:
        return all(
            [validate_tree_size(children, level - 1) for children in tree["children"]]
        )


def find_values(tree, key):
    """
    Find in the tree all the value associated with the key
    :param tree: tree to parse
    :param key: key for which we are looking for the values
    :return: list of values
    """
    results = []

    def _decode_dict(a_dict):
        try:
            results.append(a_dict[key])
        except KeyError:
            pass
        return a_dict

    json.loads(json.dumps(tree), object_hook=_decode_dict)  # Return value ignored.
    return results


def validate_tree_leaves(tree):
    articles = find_values(tree, "url")
    return len(articles) == len(set(articles))


def get_recommendations_with_article(language: str, country: str):
    """
    Build a recommendation tree

    :return: recommendation tree for the specified article
    """
    df = process_dataframe(language, country)
    article_entity_counter, text_entity_counter = init_entity_counters(df)
    cased_entities = get_cased_entities(df)

    blacklist_articles = set()
    blacklist_entities = set()

    entities = set(cased_entities.keys())
    possible_first_level_entities = select_most_frequent_entities(
        entities, article_entity_counter, text_entity_counter
    )

    children = []
    for child in possible_first_level_entities:
        if child in blacklist_entities:
            continue
        try:
            next_step_tree = rec_build_tree(
                child,
                set(),
                blacklist_entities,
                blacklist_articles,
                df["lower_entities"],
                article_entity_counter,
                cased_entities,
                article_entity_counter,
                text_entity_counter,
                df,
                MAX_LENGTH - 1,
            )
        except NoValidArticle:
            continue
        blacklist_articles.update(find_values(next_step_tree, "id"))
        blacklist_entities.update(
            [s.lower() for s in find_values(next_step_tree, "name")]
        )
        children.append(next_step_tree)
        if len(children) == MAX_WIDTH:
            break

    result = {"children": children, "name": "Source", "collapsed": True}
    if validate_tree_size(result) and validate_tree_leaves(result):
        return result
    else:
        return result


def build_leaf(id, df):
    """
    Build the leaf of the tree with the id specified
    :param id: object id to use for the leaf
    :return: dictionary for the leaf
    """
    recommended_article = df.loc[id]
    text = recommended_article.text
    i = text.find(".")  # we take the second sentence to avoid to repeat the title
    abstract = text[i + 1 : i + 451].strip()
    result = {
        "name": "<b>{}</b><br><a href=\"{}\"> Read the article </a>".format(recommended_article.title, recommended_article.url),
        "abstract": abstract,
        "id": int(id),
        "collapsed": False,
        "value": 1,
    }
    return result


def rec_build_tree(
    step_entity,
    entities,
    blacklist_entities,
    blacklist_articles,
    serie,
    entity_counter,
    cased_entities,
    article_entity_counter,
    text_entity_counter,
    df,
    max_rec=MAX_WIDTH,
):
    """
    recursively build the tree
    :param step_entity: entity to use at this recursion
    :param entities: previous entities used to build this path
    :param blacklist_entities: entities which should not appear in the tree
    :param blacklist_articles: articles which should not appear in the tree
    :param serie: pandas series with object id as index and entities as values
    :param entity_counter: dictionary of entity as key and count as value. It is used to rank the entities.
    :param max_rec: maximum number of recursion allowed for the tree
    :return: recommendation tree
    """
    step_tree = {}
    step_tree["name"] = cased_entities[step_entity]
    new_entities = deepcopy(entities)
    new_entities.add(step_entity)

    if max_rec == 0:
        id = give_random_article(new_entities, blacklist_articles, serie)
        step_tree["children"] = [build_leaf(id, df)]
    else:
        unique_id = has_unique_result(new_entities, blacklist_articles, serie)
        if unique_id is None:
            next_entities = extract_selected_entity(
                new_entities, blacklist_entities, serie, article_entity_counter, text_entity_counter
            )
            children = []
            for child in next_entities:
                if child in blacklist_entities:
                    continue
                try:
                    next_step_tree = rec_build_tree(
                        child,
                        new_entities,
                        blacklist_entities,
                        blacklist_articles,
                        serie,
                        entity_counter,
                        cased_entities,
                        article_entity_counter,
                        text_entity_counter,
                        df,
                        max_rec - 1,
                    )
                except NoValidArticle:
                    continue
                blacklist_articles.update(find_values(next_step_tree, "id"))
                blacklist_entities.update(
                    [s.lower() for s in find_values(next_step_tree, "name")]
                )
                children.append(next_step_tree)
                if len(children) == MAX_WIDTH:
                    break
            step_tree["children"] = children
            step_tree["collapsed"] = True
        elif unique_id == -1:
            raise NoValidArticle
        else:
            step_tree["children"] = [build_leaf(unique_id, df)]
    return step_tree


def give_random_article(entities, blacklist_articles, serie):
    """
    give a article which has the
    :param entities: entity set which should
    :param blacklist_articles: articles which should not appear in the tree
    :param serie: pandas series with object id as index and entities as values
    :return:
    """
    filtered_serie = serie.loc[
        (serie.apply(lambda x: entities.issubset(x)))
        & (~serie.index.isin(blacklist_articles))
    ]
    if len(filtered_serie) == 0:
        raise NoValidArticle
    else:
        return filtered_serie.index[random.randint(0, len(filtered_serie) - 1,)]


def has_unique_result(entities, blacklist_articles, serie):
    """
    Check if the set of entities lead to a unique article selection
    :param entities: entity set to verify
    :param blacklist_articles: articles which should not appear in the tree
    :param serie: pandas series with object id as index and entities as values
    :return:
    """
    filtered_serie = serie.loc[
        (serie.apply(lambda x: entities.issubset(x)))
        & (~serie.index.isin(blacklist_articles))
    ]
    result = set(filtered_serie.index)
    if len(result) == 0:
        return -1
    elif len(result) == 1:
        return result.pop()
    else:
        return None


def select_most_frequent_entities(
    entities, article_entity_counter, text_entity_counter
):
    """
    Decreasingly order the given entities using the article_entity_counter and text_entity_counter
    :param entities: entities to order
    :return: ordered entities
    """
    weighted_result = {}
    for entity in entities:
        weighted_result[entity] = (
            article_entity_counter[entity] * 10 + text_entity_counter[entity]
        )
    tuple_ent_weight = sorted(weighted_result.items(), key=lambda x: x[1], reverse=True)
    result = [ent[0] for ent in tuple_ent_weight]
    return result


def extract_selected_entity(entities, blacklist_entities, serie, article_entity_counter, text_entity_counter):
    """
    Select the entities for the next level tree
    :param entities: entities to use to select the next article
    :param blacklist_entities: entities which should not appear in the tree
    :param serie: pandas series with object id as index and entities as values
    :return: entity for the next level tree
    """
    filtered_serie = serie.loc[serie.apply(lambda x: entities.issubset(x))]
    full_result = (
        set()
        .union(*[s for s in filtered_serie])
        .difference(entities.union(blacklist_entities))
    )
    return select_most_frequent_entities(full_result, article_entity_counter, text_entity_counter)


if __name__ == "__main__":
    pass
