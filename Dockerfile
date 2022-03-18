FROM ubuntu:20.04
LABEL org.opencontainers.image.authors="salvatore.torsello08@gmail.com"

RUN apt-get update -y && \
	apt-get upgrade -y

	
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome
RUN apt-get install -y tzdata

RUN	apt-get install python3 -y && \
	apt-get install python3-pip -y && \
	apt-get install python3.8-venv

RUN pip install pipenv

WORKDIR /myApp
RUN python3 -m venv venv
RUN . venv/bin/activate
RUN pip install Flask

# Angular dependencies installation
RUN apt-get update -y && \
	apt-get install nodejs -y && \
	apt-get install npm -y

RUN nodejs -v && npm -v

RUN npm install -g @angular/cli

# Install SQLAlchemy ORM
RUN pip install sqlalchemy psycopg2-binary

# Start developing creating a template structure
WORKDIR /myApps
RUN mkdir appTemplate
WORKDIR /appTemplate
RUN mkdir database && mkdir backend && mkdir frontend && mkdir static && mkdir templates
COPY /.gitignoreTemplate /appTemplate/.gitignore
COPY /mainTemplate.py /appTemplate/main.py

RUN apt-get install -y git
RUN git init
RUN git add .

