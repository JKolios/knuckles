# Knuckles

A barebones app backend core in Python 3. Uses channelcat/sanic and
mongodb/motor to provide async HTTP request handlers paired with async DB
access. Docker Compose is used for (hopefully) quick and easy deployment.

## Running

* Install a recent version of docker compose (tested on 1.9.0).
* `docker-compose up -d`

Uses MagicStack/uvloop. Uvloop has poor windows support at the time of writing,
so no guarantees there.