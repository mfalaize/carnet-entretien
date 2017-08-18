#!/bin/sh
HOMELAB_PATH=/opt/homelab

rm -Rf ${HOMELAB_PATH}
mkdir -p ${HOMELAB_PATH}
cd ${HOMELAB_PATH}
wget -O master.tar.gz "https://github.com/mfalaize/homelab/archive/master.tar.gz" && tar -xzf master.tar.gz --strip-components=1

cd docker/homelab
docker build --no-cache -t mfalaize/homelab .

cd ../haproxy
docker build --no-cache -t mfalaize/homelab-haproxy .

docker volume create homelab
docker volume create haproxy-config
docker volume create haproxy-certs

docker network create -d bridge homelab

docker stop homelab && docker rm homelab
docker stop haproxy && docker rm haproxy

docker run --name homelab -d -v homelab:/usr/src/app/data --network=homelab mfalaize/homelab
docker run --name haproxy -d -v haproxy-config:/usr/local/etc/haproxy -v haproxy-certs:/etc/letsencrypt --network=homelab -p 80:80 -p 443:443 mfalaize/homelab-haproxy