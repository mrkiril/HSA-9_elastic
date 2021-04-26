import logging

from elasticsearch import AsyncElasticsearch
from elasticsearch._async.helpers import async_bulk


logger = logging.getLogger(__name__)

BOOK_INDEX = "projector"


async def bulk_insert_items(elastic_search: AsyncElasticsearch, data):
    try:
        errors = await async_bulk(
            elastic_search,
            actions=data,
            raise_on_error=False,
        )

        already_existed = [
            int(i['_id']) for i in errors[1] if i['status'] == 409
        ]

        return True

    except Exception as e:
        logger.error(e)
    return False


async def create_index(elastic_search: AsyncElasticsearch, index_name, mapping):
    created = False

    try:
        is_exists = await elastic_search.indices.exists(index_name)
        if not is_exists:
            # Ignore 400 means to ignore "Index Already Exist" error.
            await elastic_search.indices.create(
                index=index_name, ignore=400, body=mapping
            )
            logging.info("Created index for books")
        created = True
    except Exception as ex:
        logging.error(str(ex))
    finally:
        return created


async def search(elastic_search: AsyncElasticsearch, index, body):
    return await elastic_search.search(index=index, body=body)


async def search_fuzzy(elastic_search: AsyncElasticsearch, index, search_string):
    """
    {
          "query": {
           "multi_match" : {
              "query":      "Jon",
              "type":       "cross_fields",
              "analyzer":   "standard",
              "fields":     [ "first", "last", "*.edge" ]
            }
          }
        }
    :param elastic_search:
    :param index:
    :param search_string:
    :return:
    """
    query = {
        "query": {
            "multi_match": {
                "fields": ["book_name"],
                "query": search_string,
                "boost": 1.0,
                "fuzziness": 4,
                "prefix_length": 2,
                "max_expansions": 100,
                "analyzer": 'standard'
                }
            }
        }
    return await search(elastic_search, index, query)

