HomeLab
=======

Site web Django contenant plusieurs applications pour la gestion de la vie quotidienne

### Installation via Docker

Sur le serveur de production, lancer cette commande :

<code>bash <(curl -s https://gitlab.com/mfalaize/homelab/raw/master/docker_install.sh)</code>

### Activation du HTTPS avec letsencrypt

Une fois l'installation via docker effectuée. Lancer cette commande sur le serveur de production :

<code>docker exec -it haproxy /cert_install.sh</code>

Voilà l'application est disponible sur [https://votredomaine](#) ! Vous pouvez vous connecter avec l'utilisateur par défaut : <code>admin/s3cr3t</code>

Pour changer le mot de passe de l'utilisateur et ajouter des utilisateurs rendez-vous sur l'application admin de Django via l'URL [https://votredomaine/admin/](#).

### Mise à jour via Docker

Reéexcuter la procédure de [Installation via Docker](#installation-via-docker).