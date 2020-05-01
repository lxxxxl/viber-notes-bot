FROM python:3.7.7-alpine

WORKDIR /app
COPY . /app

EXPOSE 5000

CMD FLASK_APP=api.py flask run --host="::"
