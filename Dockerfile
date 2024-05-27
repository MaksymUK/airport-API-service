FROM python:alpine3.19
LABEL maintainer="max_andreytsiv@yahoo.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /media

RUN adduser \
        --disabled-password \
        --no-create-home \
        django-user \
    && chown -R django-user /media

RUN chmod -R 755 /media

USER django-user
