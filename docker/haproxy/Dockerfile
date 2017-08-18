FROM haproxy:1.7

COPY haproxy.cfg /usr/local/etc/haproxy/

# Installation des packages
RUN apt-get update && apt-get install -y --no-install-recommends cron \
    && apt-get install -y --no-install-recommends -t jessie-backports certbot \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

VOLUME /etc/letsencrypt
VOLUME /usr/local/etc/haproxy