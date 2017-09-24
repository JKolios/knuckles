import asyncio
import uvloop
import inject

from sanic import Sanic
from sanic.response import text
from sanic.log import log

from simplecrud import simplecrud

from settings import config
from dependencies.mongo import MongoConnection, Mongo

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
event_loop = asyncio.get_event_loop()

app = Sanic(__name__)


def injection_config(binder):
    binder.bind(Mongo, MongoConnection(uri=config['mongo_uri'],
                                       default_db=config['mongo_db_name'],
                                       default_collection=config['mongo_collection_name']))


@app.route("/status")
async def status(request):
    log.debug('Status request received')
    return text("All systems nominal.")

if __name__ == "__main__":
    # Configure a shared injector.
    inject.configure(injection_config)

    app.blueprint(simplecrud)

    app.run(host=config['host'],
            port=config['port'],
            debug=config['debug'],
            workers=config['workers'])
