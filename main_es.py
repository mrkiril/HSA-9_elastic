import logging

from aiorun import run

from app.es import bulk_insert_items, create_index, BOOK_INDEX
from main import es_init
from settings import Config

logger = logging.getLogger(__name__)


FIELDS = ("book_name", "lines", "url")

mapping = {
    "settings": {
        "index": {
            "analysis": {
                "filter": {},
                "analyzer": {
                    "projector_analyzer": {
                        "filter": ["lowercase", "stop", "trim"],
                        "tokenizer": "projector_search_tokenizer",
                    },
                    "projector_search_analyzer": {
                        "filter": ["lowercase", "stop", "trim"],
                        "tokenizer": "lowercase"
                    },
                },
                "tokenizer": {
                    "projector_search_tokenizer": {
                        "type": "edge_ngram",
                        "min_gram": 2,
                        "max_gram": 10,
                        "token_chars": ["letter"],
                    }
                },
            }
        }
    },
    "mappings": {
        "properties": {
            "book_name": {
                "type": "text",
                "fields": {
                    "edgengram": {
                        "type": "text",
                        "analyzer": "projector_analyzer",
                        "search_analyzer": "projector_search_analyzer",
                    }
                },
                "analyzer": "standard",
            },
            "lines": {
                "type": "integer",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "url": {
                "type": "text"
            }
        }
    },
}


async def main():
    conf = Config()
    logging.basicConfig(level=logging.DEBUG)
    logging.config.dictConfig(conf.DEFAULT_LOGGING)
    es_conn = es_init(conf)
    logger.info("Start create index")
    await create_index(elastic_search=es_conn, index_name=BOOK_INDEX, mapping=mapping)
    logger.info("Finish create index")
    with open("datasets/data-00000-of-00010") as f:
        bulk_ = []
        inc = 0

        while True:
            line = f.readline()
            if line.startswith("MENTION"):
                inc += 1
                line_arr = line.replace("MENTION", '').replace('\t', ' ').replace('\n', '').strip().split(' ')
                bulk_.append({
                    "_id": inc,
                    "_index": BOOK_INDEX,
                    '_op_type': "create",
                    "book_name": " ".join(line_arr[:-2]),
                    "lines": line_arr[-2],
                    "url": line_arr[-1]
                })
            if not line:
                break

            if inc % 500 == 0:
                logger.info(f"Load {inc} rows")
                await bulk_insert_items(es_conn, bulk_)
                bulk_ = []

    await es_conn.close()


if __name__ == '__main__':

    print('= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =')
    print('= = = = = = = = = = = = = S T A R T   C R E A T E   E S = = = = = = = = = = = = = = = =')
    print('= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =')
    run(main(), stop_on_unhandled_errors=True, use_uvloop=True)
    logger.info("BYE ...")
