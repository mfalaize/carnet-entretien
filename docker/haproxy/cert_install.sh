#!/bin/sh
HAPROXY_CONFIG_PATH=/usr/local/etc/haproxy

test -f ${HAPROXY_CONFIG_PATH}/cert.pem && echo "Un certificat existe déjà pour ce serveur" && exit 0

read -p "Nom de domaine du serveur : " nom_domaine
read -p "Adresse mail de l'administrateur du certificat : " adresse_mail

test -f /etc/letsencrypt/live/${nom_domaine}/fullchain.pem || certbot certonly --standalone -n --agree-tos -m ${adresse_mail} -d ${nom_domaine} --preferred-challenges http --http-01-port 54321
sed -i 's/#//' ${HAPROXY_CONFIG_PATH}/haproxy.cfg
test -f ${HAPROXY_CONFIG_PATH}/fullchain.pem || ln -s /etc/letsencrypt/live/${nom_domaine}/fullchain.pem ${HAPROXY_CONFIG_PATH}/fullchain.pem
test -f ${HAPROXY_CONFIG_PATH}/privkey.pem || ln -s /etc/letsencrypt/live/${nom_domaine}/privkey.pem ${HAPROXY_CONFIG_PATH}/privkey.pem
cat ${HAPROXY_CONFIG_PATH}/fullchain.pem ${HAPROXY_CONFIG_PATH}/privkey.pem > ${HAPROXY_CONFIG_PATH}/cert.pem
