FROM  python:3.8

ENV FLASK_APP="run.py"

WORKDIR /app

ADD . /app

#RUN apt-get update && apt-get install cifs-utils -y && apt-get install smbclient -y 

RUN pip install pip --upgrade

RUN pip install -r requeriments.txt


ENTRYPOINT ["uwsgi","--ini","app.ini"]



