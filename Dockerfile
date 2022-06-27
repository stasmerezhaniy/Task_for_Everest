FROM python:3.8

RUN pip install pipenv

COPY . /backend
WORKDIR /backend

RUN pipenv check


RUN pip install flask
RUN pip install flask_admin
RUN pip install flask_security
RUN pip install celery
RUN pip install redis
RUN pip install flask_sqlalchemy
RUN pip install email_validator
RUN pip install rabbitmq
RUN pip install gunicorn
RUN pip install flask_bootstrap

COPY . /backend

EXPOSE 5000


