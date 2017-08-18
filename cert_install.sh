#!/bin/sh
set -e

HAPROXY_CONFIG_PATH=/usr/local/etc/haproxy

docker exec -it haproxy certbot certonly --standalone -n --agree-tos -m $2 -d $1 --preferred-challenges http --http-01-port 54321 \
    && docker exec -it haproxy sed -i 's/#//' ${HAPROXY_CONFIG_PATH}/haproxy.cfg \
    && docker exec -it haproxy ln -s /etc/letsencrypt/live/$1/fullchain.pem ${HAPROXY_CONFIG_PATH}/fullchain.pem \
    && docker exec -it haproxy ln -s /etc/letsencrypt/live/$1/privkey.pem ${HAPROXY_CONFIG_PATH}/privkey.pem \
    && docker exec -it haproxy /etc/cron.daily/letsencrypt \
    && docker restart haproxy