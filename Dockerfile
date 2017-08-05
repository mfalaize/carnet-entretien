FROM python:3.4
MAINTAINER Maxime Falaize <maxime.falaize@gmail.com>

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Installation des packages
RUN apt-get update && apt-get install -y \
    apache2 libapache2-mod-wsgi-py3 cron \
	--no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Activation du site sur apache
COPY homelab.conf /etc/apache2/sites-available/
RUN a2dissite 000-default && a2ensite homelab

# Activation des crons
COPY crontab_root /var/spool/cron/crontabs/root
RUN chmod 600 /var/spool/cron/crontabs/root && chown root:crontab /var/spool/cron/crontabs/root

RUN mkdir static
VOLUME data/

EXPOSE 80

RUN chmod +x docker_entrypoint.sh
ENTRYPOINT ["./docker_entrypoint.sh"]
