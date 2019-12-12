import mysql.connector
from find_entity import find_entity, tagger
from db_connection import cassdb, get_mysql_connection

import pandas as pd
import pickle
from requests import get
from pprint import pprint

# load all the articles from cassandra in the blog (ie domain id of the blog is 1282)
rows = cassdb.execute(
    "SELECT domainid, itemid, created_at, fulltext, published_at, updated_at\n"
    "FROM articledata.fulltext\n"
    "WHERE domainid=1282;"
)


# mycursor = mydb.cursor()
#
# try:
#     # lets delete the table before to try to create it again
#     mycursor.execute("DROP TABLE knldgetreeentity")
# except mysql.connector.errors.ProgrammingError:
#     print("no table yet")
#
# mycursor.execute("""CREATE TABLE `knldgetreeentity` (
#   `itemid` int(10) unsigned NOT NULL,
#   `domainid` int(10) unsigned NOT NULL,
#   `entities` text NOT NULL,
#   `url` varchar(1024),
#   `img` varchar(255),
#   PRIMARY KEY (`itemid`)
# ) ENGINE=InnoDB AUTO_INCREMENT=541596424 DEFAULT CHARSET=utf8""")


def is_url_available(url):
    """
    Check if the url exists or not.
    :param url: String. Url
    :return: Boolean. True if the url exists else false
    """
    try:
        result = get(url).status_code == 200
    except:
        result = False
    return result


def return_available_url(
    url,
    default_url="https://www.plista.com/wp-content/uploads/2018/08/plista_Web-Background.jpg",
):
    """
    Check if url exists else return default url.
    :param url: String. Url
    :param default_img: String. Default url
    :return: String. Url which exists.
    """
    return url if (is_url_available(url)) else default_url


def get_articles_urls(article_id):
    """
    Get the url id of the article
    :param article_id_list: list of article id g
    :return: list containing itemid, domainid, objectid, item, url, img, text, created_at, weight, version, updated_at
    """
    c = get_mysql_connection()
    con = c.cursor()
    con.execute("select * from db_youfilter.item where itemid={}".format(article_id))
    rows = con.fetchall()
    # list[row] where row is a tuple with elements (itemid, domainid, objectid, item,url,img,text,created_at,weight,version,updated_at)
    if rows:
        row = rows[0]
        result = dict(
            itemid=row[0],
            domainid=row[1],
            objectid=row[2],
            item=row[3],
            url=row[4],
            img=row[5],
            text=row[6],
            created_at=row[7],
            weight=row[8],
        )
        return result
    else:
        return {}


def find_more_entities(text, entities):
    """
    Try to extract more entities from the text using all entities present in the corpus of text
    :param text: text to process
    :param entities: set  of entites to look for in the text
    :return: subset of entities present in the set
    """
    return set([entity for entity in entities if entity in text])


if __name__ == "__main__":
    vals = []
    i = 0
    for row in rows:
        article_info = get_articles_urls(row.itemid)
        print(article_info, flush=True)
        if article_info:
            entities = find_entity(row.fulltext)

            i += 1
            val = {
                "itemid": row.itemid,
                "domainid": row.domainid,
                "text": row.fulltext,
                "objectid": article_info["objectid"],
                "heading": article_info["item"],
                "url": article_info["url"],
                "img_url": return_available_url(article_info["img"]),
                "entities": entities,
            }
            pprint(val)
            print("", flush=True)
            vals.append(val)

            if i > 5:
                break

    df = pd.DataFrame(vals)

    entities = set()
    for ent in df.entities:
        entities.update(ent)
    df["enlarged_entities"] = df.text.apply(lambda x: find_more_entities(x, entities))

    with open("plista_blog_post.pickle", "wb") as output_file:
        pickle.dump(df, output_file)
