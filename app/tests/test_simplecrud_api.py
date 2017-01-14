"""Tests for the "simplecrud" application blueprint"""
import inject
from sanic.utils import sanic_endpoint_test
from ujson import loads, dumps
from bson import json_util
import pytest

from app import app
from simplecrud import simplecrud
from dependencies.mongo import Mongo


@pytest.fixture
def reset_mocked_mongo(request):
    yield None  # Mocked fixture, used to run a finalizer after test exec
    mocked_mongo.reset()


class MockedMongo(object):
    default_docs = [{'test': 'doc'},
                    {'hello': 'world'}]

    def __init__(self):
        self.docs = self.default_docs

    async def get_all_docs(self, db=None, collection=None, length=10):
        return self.docs

    async def get_doc(self, doc_id, db=None, collection=None):
        doc_id = int(doc_id)
        try:
            return self.docs[doc_id]
        except IndexError:
            return None

    async def insert_or_update(self, doc, doc_id=None, db=None,
                               collection=None):
        if doc_id:
            doc_id = int(doc_id)
            if doc_id < len(self.docs):
                self.docs[doc_id].update(doc)
                return {'result': 'updated',
                        'updated_id': doc_id}
            else:
                return {'result': 'failed'}
        else:
            self.docs.append(doc)
            return {'result': 'inserted',
                    'inserted_id': len(self.docs) - 1}

    async def delete_doc(self, doc_id, db=None, collection=None):
        try:
            del self.docs[int(doc_id)]
        except IndexError:
            return False
        return True

    @staticmethod
    def docs_to_json(doc_or_docs):
        return json_util.dumps(doc_or_docs)

    def reset(self):
        self.docs = self.default_docs


mocked_mongo = MockedMongo()


def config_for_tests(binder):
    binder.bind(Mongo, mocked_mongo)


inject.configure(config_for_tests)

app.blueprint(simplecrud)


def test_get_all_docs():
    request, response = sanic_endpoint_test(app,
                                            uri='/crud/',
                                            method='get')

    assert response.status == 200
    assert loads(response.text) == mocked_mongo.docs


def test_get_doc():
    # Test a successful document fetch
    request, response = sanic_endpoint_test(app,
                                            uri='/crud/0',
                                            method='get')

    assert response.status == 200
    assert loads(response.text) == mocked_mongo.docs[0]

    # Test a failed document fetch expecting a 404

    request, response = sanic_endpoint_test(app,
                                            uri='/crud/10',
                                            method='get')

    assert response.status == 404
    assert response.text == 'Error: Cannot find document with id:10'


def test_insert(reset_mocked_mongo):
    doc_to_insert = {'hello': 'world'}
    pre_insert_doc_count = len(mocked_mongo.docs)
    request, response = sanic_endpoint_test(app,
                                            uri='/crud/',
                                            method='post',
                                            data=dumps(doc_to_insert)
                                            )

    assert response.status == 200
    assert response.text == 'Successfully inserted document ' \
                            'with id:{0}'.format(pre_insert_doc_count)
    assert doc_to_insert in mocked_mongo.docs
    assert len(mocked_mongo.docs) == pre_insert_doc_count + 1


def test_update(reset_mocked_mongo):
    doc_to_insert = {'hello': 'world'}
    pre_insert_doc_count = len(mocked_mongo.docs)
    request, response = sanic_endpoint_test(app,
                                            uri='/crud/0',
                                            method='post',
                                            data=dumps(doc_to_insert)
                                            )

    assert response.status == 200
    assert response.text == 'Successfully updated document with id:0'
    assert mocked_mongo.docs[0]['hello'] == 'world'
    assert len(mocked_mongo.docs) == pre_insert_doc_count


def test_delete(reset_mocked_mongo):
    request, response = sanic_endpoint_test(app,
                                            uri='/crud/0',
                                            method='delete')
    assert response.status == 200
    assert response.text == 'Successfully deleted document with id:0'

    request, response = sanic_endpoint_test(app,
                                            uri='/crud/99',
                                            method='delete')
    assert response.status == 404
    assert response.text == 'Error: Cannot find document with id:99'
