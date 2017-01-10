import inject
import sanic.exceptions
from sanic import Blueprint
from sanic.response import text
from sanic.views import HTTPMethodView
from sanic.response import HTTPResponse

from dependencies.mongo import Mongo

simplecrud = Blueprint('simplecrud', url_prefix='/crud')


class NoIDHandlers(HTTPMethodView):
    mongo = inject.attr(Mongo)

    async def get(self, request):
        all_docs = await self.mongo.get_all_docs(length=None)
        return HTTPResponse(body=self.mongo.docs_to_json(all_docs),
                            content_type="application/json")

    async def post(self, request):
        new_doc = request.json
        insert_result = await self.mongo.insert_or_update(doc=new_doc)
        if insert_result['result'] == 'inserted':
            return text('Successfully inserted doc with id:{0}'.
                        format(insert_result['inserted_id']))
        else:
            raise sanic.exceptions.ServerError(
                message='Failed to insert document')


simplecrud.add_route(NoIDHandlers(), '/')


class IDHAndlers(HTTPMethodView):
    mongo = inject.attr(Mongo)

    async def get(self, request, doc_id):
        doc = await self.mongo.get_doc(doc_id=doc_id)
        if doc:
            return HTTPResponse(body=self.mongo.docs_to_json(doc),
                                content_type="application/json")
        else:
            raise sanic.exceptions.NotFound(
                message='Cannot find document with'
                        ' id:{0}'.format(doc_id))

    async def post(self, request, doc_id):
        new_doc = request.json
        update_result = await self.mongo.insert_or_update(doc=new_doc,
                                                          doc_id=doc_id)
        if update_result["result"] == "updated":
            return text('Successfully updated doc with id:{0}'.
                        format(update_result['updated_id']))
        else:
            raise sanic.exceptions.ServerError(
                message='Failed to update document')

    async def delete(self, request, doc_id):
        delete_result = await self.mongo.delete_doc(doc_id=doc_id)
        if delete_result:
            return text(body='Successfully deleted document with id:{'
                             '0}.'.format(doc_id))
        else:
            raise sanic.exceptions.NotFound(message='Cannot find document with'
                                                    ' id:{0}'.format(doc_id))


simplecrud.add_route(IDHAndlers(), '/<doc_id>')
