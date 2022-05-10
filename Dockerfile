# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y wait-for-it
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY /tandem /code/

# Source: https://docs.docker.com/samples/django/