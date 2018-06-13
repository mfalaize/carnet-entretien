FROM python:3.4
MAINTAINER Maxime Falaize <maxime.falaize@gmail.com>

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get update \
    && apt-get install -y --no-install-recommends apache2 libapache2-mod-wsgi-py3 cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p static data/logs data/media

COPY docker/homelab/. /

RUN chmod 600 /etc/cron.d/homelab

VOLUME data/

EXPOSE 80

ENTRYPOINT ["/docker_entrypoint.sh"]
