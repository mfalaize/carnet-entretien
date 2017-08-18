#!/bin/sh
HAPROXY_CONFIG_PATH=/usr/local/etc/haproxy

if [ -z ${1+x} ] || [ -z ${2+x} ] ; then
    echo "Le script prend en paramètre le nom de domaine en première position et l'adresse mail en deuxième position"
    exit 1
fi

docker exec -it haproxy test -f /etc/letsencrypt/live/$1/fullchain.pem || certbot certonly --standalone -n --agree-tos -m $2 -d $1 --preferred-challenges http --http-01-port 54321
docker exec -it haproxy sed -i 's/#//' ${HAPROXY_CONFIG_PATH}/haproxy.cfg
docker exec -it haproxy test -f ${HAPROXY_CONFIG_PATH}/fullchain.pem || ln -s /etc/letsencrypt/live/$1/fullchain.pem ${HAPROXY_CONFIG_PATH}/fullchain.pem
docker exec -it haproxy test -f ${HAPROXY_CONFIG_PATH}/privkey.pem || ln -s /etc/letsencrypt/live/$1/privkey.pem ${HAPROXY_CONFIG_PATH}/privkey.pem
docker exec -it haproxy /etc/cron.daily/letsencrypt
docker restart haproxy