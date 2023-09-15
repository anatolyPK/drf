FROM python:3.10.2-alpine3.14

COPY requirements.txt /temp/requirements.txt

EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

RUN mkdir /code
WORKDIR /code
COPY . /code

RUN adduser --disabled-password src-user

USER src-user