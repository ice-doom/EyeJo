FROM ubuntu:20.04

ENV LANG="C.UTF-8"
ENV LC_ALL="C.UTF-8"
ENV LANGUAGE="C.UTF-8"
ENV DEBIAN_FRONTEND=noninteractive

COPY eyejo/requirements.txt /root/requirements.txt
COPY eyejo/ /root/eyejo/
COPY docker/install.sh /root/install.sh

WORKDIR /root/

RUN apt update && \
apt install -yq --no-install-recommends wget unzip python3.8 python3-pip libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 libnss3 libmysqlclient-dev python3-dev build-essential libffi-dev libxml2-dev libxslt1-dev zlib1g-dev python3-magic nginx apache2-utils libcurl4-openssl-dev wfuzz  fonts-wqy-microhei ttf-wqy-zenhei libssh-dev libidn11-dev libpcre3-dev libgtk2.0-dev libpq-dev libsvn-dev firebird-dev libmemcached-dev libgpg-error-dev libgcrypt20-dev && \
apt-get install libsqlite3-dev libpcap-dev libssl-dev -y && \
sed -i 's/user www-data/user root/' /etc/nginx/nginx.conf && \
mkdir /var/log/celery/ && \
pip3 install setuptools && \
pip3 install -r requirements.txt && \
sed -i 's/{k.lower(): v for k, v in headers.items()}/{k: v for k, v in headers.items()}/' /usr/local/lib/python3.8/dist-packages/pyppeteer/network_manager.py && \
/root/install.sh && \
rm -rf  /var/lib/apt/lists/*

COPY docker/default /etc/nginx/sites-available/default
