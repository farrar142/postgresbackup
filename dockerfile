FROM postgres:12
WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED=0
USER root
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install postgis* -y
RUN apt-get install python3 -y
COPY . .
RUN apt-get install pip -y
RUN pip install -r requirements.txt
RUN python3 -m pip install 'boto3-stubs[s3,ec2]'
RUN mkdir /root/archives /root/backups