HomeLab
=======

Site web Django contenant plusieurs applications pour la gestion de la vie quotidienne

###Installation via Docker

Avant de commencer créez une base de données <code>homelab</code> vide.

<code>git clone https://github.com/mfalaize/homelab /opt/homelab</code>

<code>cd /opt/homelab</code>

<code>cp conf/config_template.ini /conf/config.ini</code>

Modifiez le fichier <code>config.ini</code> pour y mettre vos propres paramètres.

<code>docker build --rm=true --tag="mfalaize/homelab:latest" .</code>

<code>docker run --name homelab -d -v /opt/homelab/conf:/usr/src/app/conf --link votre_container_db:db -p 80:80 mfalaize/homelab init</code>

Pour les prochaines commandes run si la base est déjà créée vous pouvez vous contentez d'un :

<code>docker run --name homelab -d -v /opt/homelab/conf:/usr/src/app/conf --link votre_container_db:db -p 80:80 mfalaize/homelab</code>

Voilà l'application est disponible sur [http://votredomaine/carnet-auto/](#) ! Vous pouvez vous connecter avec l'utilisateur par défaut : <code>admin/s3cr3t</code>

Pour changer le mot de passe de l'utilisateur et ajouter des utilisateurs rendez-vous sur l'application admin de Django via l'URL [http://votredomaine/admin/](#).
