"""Tests for the "simplecrud" application blueprint"""
import inject
from sanic.utils import sanic_endpoint_test
from ujson import loads

from app import app
from simplecrud import simplecrud
from dependencies.mongo import Mongo


class MockedMongo(object):
    mocked_docs = [{'test': 'doc'},
                   {'hello': 'world'}]

    def get_all_docs(self, db=None, collection=None, length=10):
        return self.mocked_docs

    def get_doc(self, doc_id, db=None, collection=None):
        if doc_id == 'success':
            return self.mocked_docs[0]
        else:
            return None

    def insert_or_update(self, doc, doc_id=None, db=None,
                         collection=None):
        if doc_id:
            return {'result': 'updated',
                    'updated_id': 'foo'}
        else:
            return {'result': 'inserted',
                    'inserted_id': 'bar'}

    def delete_doc(self, doc_id, db=None, collection=None):
        return True


def inject_config(binder):
    binder.bind(Mongo, MockedMongo())


# Configure a shared injector.
inject.configure(inject_config)

app.blueprint(simplecrud)


def test_get_all_docs():
    request, response = sanic_endpoint_test(app,
                                            uri='/crud/',
                                            method='get')

    print(response.text)
    assert loads(response.text) == MockedMongo.mocked_docs
