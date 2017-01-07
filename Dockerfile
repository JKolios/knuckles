FROM alpine:3.5
MAINTAINER Jason Kolios <jasonkolios@gmail.com>

RUN apk add --update gcc make musl-dev python3 python3-dev

COPY ./app /app
WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000
CMD python3 app.py
