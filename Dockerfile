FROM python:2.7.14-alpine

WORKDIR /app
COPY . /app

EXPOSE 8080

CMD python ./api.py
