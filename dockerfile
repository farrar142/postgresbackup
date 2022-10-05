FROM postgres:12
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED=0
USER root
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install postgis* -y
RUN apt-get install python3 -y
COPY . .
COPY .pgpass /root/.pgpass
RUN chmod 0600 /root/.pgpass
RUN apt-get install pip -y
RUN pip install -r requirements.txt