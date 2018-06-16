FROM haproxy:1-alpine
MAINTAINER Maxime Falaize <pro@maxime-falaize.fr>

COPY . /

# Installation des packages
RUN apk add --no-cache certbot

VOLUME /etc/letsencrypt /usr/local/etc/haproxy

ENTRYPOINT ["/docker-entrypoint-homelab.sh"]
CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]
