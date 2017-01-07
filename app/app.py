import asyncio
import uvloop

from sanic import Sanic
from sanic.response import text
from sanic.log import log

from simplecrud import simplecrud

from settings import config

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
event_loop = asyncio.get_event_loop()

app = Sanic(__name__)
app.blueprint(simplecrud)


@app.route("/status")
async def status(request):
    log.debug('Status request received')
    return text("All systems nominal.")

if __name__ == "__main__":
    app.run(host=config['host'],
            port=config['port'],
            debug=config['debug'],
            workers=config['workers'],
            loop=event_loop)
