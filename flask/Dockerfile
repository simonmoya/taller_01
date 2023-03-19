FROM  python:3.9.7

ENV FLASK_APP="run.py"

RUN mkdir -p /var/www/model

WORKDIR /app

ADD . /app

RUN pip install pip --upgrade

RUN pip install -r requeriments.txt

ENTRYPOINT ["uwsgi","--ini","app.ini"]



