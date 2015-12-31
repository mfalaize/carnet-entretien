FROM django:python3-onbuild
MAINTAINER Maxime Falaize <maxime.falaize@gmail.com>

ENV PYTHONUNBUFFERED 1

# Installation des packages
RUN apt-get update && apt-get install -y \
    apache2 libapache2-mod-wsgi-py3 cron \
	--no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Activation du site sur apache
ADD homelab.conf /etc/apache2/sites-available/
RUN a2dissite 000-default && a2ensite homelab

# Activation des crons
ADD crontab_root /var/spool/cron/crontabs/root
RUN chmod 600 /var/spool/cron/crontabs/root && chown root:crontab /var/spool/cron/crontabs/root

RUN mkdir media static logs
VOLUME media/
VOLUME logs/
VOLUME conf/

EXPOSE 80

RUN chmod +x docker_entrypoint.sh
ENTRYPOINT ["./docker_entrypoint.sh"]
