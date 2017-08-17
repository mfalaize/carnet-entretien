FROM python:3.4
MAINTAINER Maxime Falaize <maxime.falaize@gmail.com>

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Installation des packages
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    apache2 libapache2-mod-wsgi-py3 cron \
	--no-install-recommends \
	&& apt-get install -y python-certbot-apache -t jessie-backports \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Activation du site sur apache
COPY 000-default.conf /etc/apache2/sites-available/

# Activation des crons
COPY crontab_root /var/spool/cron/crontabs/root
RUN chmod 600 /var/spool/cron/crontabs/root && chown root:crontab /var/spool/cron/crontabs/root

RUN mkdir -p static data/logs data/media
VOLUME data/

EXPOSE 80 443

RUN chmod +x docker_entrypoint.sh
ENTRYPOINT ["./docker_entrypoint.sh"]
