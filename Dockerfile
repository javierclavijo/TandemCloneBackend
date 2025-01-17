# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY /tandem /code/
COPY wait /
RUN chmod +x /wait


# Source: https://docs.docker.com/samples/django/