FROM python:3.10.2
RUN pip install pipenv
RUN mkdir /code
WORKDIR /code
COPY Pipfile* /code/



RUN pipenv install celery
RUN pipenv install --system --deploy --ignore-pipfile
ADD config /code/