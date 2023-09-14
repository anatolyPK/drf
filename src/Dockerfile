FROM python:3.10.2-alpine3.14

COPY requirements.txt /temp/requirements.txt

EXPOSE 8000

RUN pip install -r /temp/requirements.txt

COPY . /src

RUN adduser --disabled-password src-user

USER src-user