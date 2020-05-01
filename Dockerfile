FROM python:2.7.14-alpine

WORKDIR /app
COPY . /app

EXPOSE 5000

CMD python ./api.py
