from sanic import Blueprint
import sanic.exceptions
from sanic.response import text, HTTPResponse
from sanic.log import log
from motor.motor_asyncio import AsyncIOMotorClient
from bson import json_util
from bson.objectid import ObjectId

from settings import config

simplecrud = Blueprint('simplecrud', url_prefix='/crud')
db_connection = None
collection = None


def mongo_compatible_json(body, status=200, headers=None):
    return HTTPResponse(json_util.dumps(body), headers=headers,
                        status=status,
                        content_type="application/json")


@simplecrud.listener('before_server_start')
async def setup_connection(loop, app):
    log.debug('starting setup_connection')
    global db_connection
    global collection
    db_connection = AsyncIOMotorClient(config['mongo_connection_string'])
    collection = db_connection.local.crud_docs
    log.debug('ending setup_connection')


@simplecrud.listener('after_server_stop')
async def teardown_connection(loop, app):
    db_connection.close()


@simplecrud.route('/', methods=['GET', 'POST'])
async def no_id_handler(request):
    method_handlers = {'GET': get_all_docs,
                       'POST': add_doc}

    return await method_handlers[request.method](request)


async def get_all_docs(request):
    all_docs = collection.find()
    doc_listing = await all_docs.to_list(length=10)
    return mongo_compatible_json(doc_listing)


async def add_doc(request):
    new_doc = request.json
    insert_result = await collection.insert_one(new_doc)
    if insert_result.inserted_id:
        return text('Successfully inserted doc with id:{0}'.
                    format(insert_result.inserted_id))
    else:
        raise sanic.exceptions.ServerError(
            message='Failed to insert document')


@simplecrud.route('/<doc_id>', methods=['GET', 'POST', 'DELETE'])
async def id_handler(request, doc_id):
    method_handlers = {'GET': get_doc,
                       'POST': update_doc,
                       'DELETE': delete}

    return await method_handlers[request.method](request, doc_id)

async def get_doc(request, doc_id):
    doc = await collection.find_one({"_id": ObjectId(doc_id)})
    if doc:
        return mongo_compatible_json(doc)
    else:
        raise sanic.exceptions.NotFound(
            message='Cannot find document with'
                    ' id:{0}'.format(doc_id))


async def update_doc(request, doc_id):
    new_doc = request.json
    update_result = await collection.replace_one(
        filter={"_id": ObjectId(doc_id)},
        replacement=new_doc,
        upsert=True)
    if update_result.modified_count:
        return text('Successfully updated doc with id:{0}'.
                    format(update_result.upserted_id))
    else:
        raise sanic.exceptions.ServerError(
            message='Failed to update document')


async def delete(request, doc_id):
    delete_result = await collection.delete_one({"_id": ObjectId(doc_id)})
    if delete_result.deleted_count:
        return text(body='Successfully deleted document with id:{'
                         '0}.'.format(doc_id))
    else:
        raise sanic.exceptions.NotFound(message='Cannot find document with'
                                                ' id:{0}'.format(doc_id))
