FROM ubuntu:14.04
RUN apt-get update && apt-get install -y nodejs nodejs-legacy npm git && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /srv/application
ADD . /srv/application

WORKDIR /srv/application
RUN rm -rf node_modules && npm install

ENV APP_BIND 0.0.0.0:8080
ENTRYPOINT ["/usr/bin/npm", "start"]

