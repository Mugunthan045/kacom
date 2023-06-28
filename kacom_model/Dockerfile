FROM python:3.8.10-slim

WORKDIR /app

COPY . /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install gcc -y \
    && apt-get clean

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt \
    && rm -rf /root/.cache/pip


