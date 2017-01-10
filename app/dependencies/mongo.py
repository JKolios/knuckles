from bson import json_util
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


class Mongo(object):
    async def get_all_docs(self, db=None, collection=None, length=10):
        pass

    async def get_doc(self, doc_id, db=None, collection=None):
        pass

    async def insert_or_update(self, doc, doc_id=None, db=None,
                               collection=None):
        pass

    def delete_doc(self, doc_id, db=None, collection=None):
        pass

    @staticmethod
    def docs_to_json(doc_or_docs):
        return json_util.dumps(doc_or_docs)


class MongoConnection(object):
    def __init__(self, uri, default_db=None, default_collection=None):

        if not isinstance(uri, str):
            raise ValueError('A valid connection URI must be given.')

        if isinstance(default_collection, str) and not isinstance(
                default_db, str):
            raise ValueError('A default collection cannot be specified '
                             'without a default DB')

        self.connection_uri = uri
        self._db_connection = None
        self.default_db = default_db
        self.default_collection = default_collection

    @property
    def connection(self):
        if self._db_connection is None:
            self._setup_connection(self.connection_uri)
        return self._db_connection

    @staticmethod
    def docs_to_json(doc_or_docs):
        return json_util.dumps(doc_or_docs)

    def _query_object(self, db=None, collection=None):
        target_db = db or self.default_db
        target_collection = collection or self.default_collection

        target_obj = self.connection
        target_obj = getattr(target_obj, target_db, target_obj)
        target_obj = getattr(target_obj, target_collection, target_obj)
        return target_obj

    async def get_all_docs(self, db=None, collection=None, length=10):
        all_docs = self._query_object(db=db, collection=collection).find()
        doc_listing = await all_docs.to_list(length=length)
        return doc_listing

    async def get_doc(self, doc_id, db=None, collection=None):
        query_object = self._query_object(db=db, collection=collection)
        doc = await query_object.find_one({"_id": ObjectId(doc_id)})
        return doc if doc else None

    async def insert_or_update(self, doc, doc_id=None, db=None,
                               collection=None):
        query_object = self._query_object(db=db, collection=collection)

        update_result = await query_object.replace_one(
            filter={"_id": ObjectId(doc_id)},
            replacement=doc,
            upsert=True)

        result = {'raw_result': update_result.raw_result}

        if update_result.upserted_id:
            result["result"] = "inserted"
            result["inserted_id"] = update_result.upserted_id
        elif update_result.modified_count:
            result["result"] = "updated"
            result["updated_id"] = doc_id
        else:
            result["result"] = "failed"

        return result

    async def delete_doc(self, doc_id, db=None, collection=None):
        query_object = self._query_object(db=db, collection=collection)
        delete_result = await query_object.delete_one({"_id": ObjectId(
            doc_id)})
        if delete_result.deleted_count:
            return True
        else:
            return False

    def close(self):
        self._teardown_connection()

    def _setup_connection(self, mongo_uri):
        self._db_connection = AsyncIOMotorClient(mongo_uri)

    def _teardown_connection(self):
        self._db_connection.close()
