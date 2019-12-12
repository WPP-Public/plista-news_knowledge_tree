import pymysql
from typing import Set
import hashlib
from pymysql.cursors import Cursor
import json
db = pymysql.connect(host="db", user="root", password="password")
cursor = db.cursor()

try:
    cursor.execute("CREATE DATABASE opendigitalworld")
except pymysql.err.ProgrammingError:
    print("Database already exists")

cursor.execute("USE opendigitalworld")

# try:
#     cursor.execute("DROP TABLE opendigitalworld.article;")
# except pymysql.err.InternalError:
#     print("no table already")


cursor.execute("""CREATE TABLE IF NOT EXISTS `opendigitalworld`.`article` (
    `hash` VARCHAR(255),
    `url` TEXT  ,
    `entities` TEXT,
    PRIMARY KEY (`hash`)
) CHARSET=utf8;
""")


def get_cached_entities(url: str, cursor: Cursor = cursor) -> Set[str]:
    hash = hashlib.sha256()
    hash.update(url.encode("utf-8"))
    hash_result = hash.hexdigest()
    get_sql = """SELECT hash, entities FROM opendigitalworld.article WHERE hash='{}'""".format(hash_result)
    cursor.execute(get_sql)
    result = cursor.fetchone()
    if result is not None:
        entities = result[1]
        return set(entities.split("|"))

def set_cache_entities(url, entities: Set[str], db = db):
    hash = hashlib.sha256()
    hash.update(url.encode("utf-8"))
    hash_result = hash.hexdigest()
    str_entities = "|".join(entities)

    insert_sql = """INSERT INTO `opendigitalworld`.`article` (hash, url, entities) VALUES ('{}', '{}', '{}');""".format(hash_result, url, str_entities)
    print(insert_sql)
    cursor = db.cursor()
    cursor.execute(insert_sql)
    db.commit()



if __name__ == "__main__":
    set_cache_entities("qwerty", set(["a", "b"]))
    entities = get_cached_entities("qwerty")
    print(entities)



