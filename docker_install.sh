#!/bin/sh
# Ce script est lancé sur le serveur de déploiement

docker volume create homelab
docker volume create haproxy-config
docker volume create haproxy-certs

docker network create -d bridge homelab

docker stop homelab && docker rm homelab
docker stop haproxy && docker rm haproxy

docker run --name homelab -d -v homelab:/usr/src/app/data --network=homelab mfalaize/homelab
docker run --name haproxy -d -v haproxy-config:/usr/local/etc/haproxy -v haproxy-certs:/etc/letsencrypt --network=homelab -p 80:80 -p 443:443 mfalaize/homelab-haproxy
