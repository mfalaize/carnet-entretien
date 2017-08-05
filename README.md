HomeLab
=======

Site web Django contenant plusieurs applications pour la gestion de la vie quotidienne

###Installation via Docker

<code>git clone https://github.com/mfalaize/homelab /opt/homelab</code>

<code>cd /opt/homelab</code>

<code>cp data/conf/config_template.ini data/conf/config.ini</code>

Modifiez le fichier <code>config.ini</code> pour y mettre vos propres paramètres.

<code>docker build --rm=true --tag="mfalaize/homelab:latest" .</code>

<code>docker create volume homelab</code>

<code>docker run --name homelab -d -v homelab:/usr/src/app/data -p 80:80 mfalaize/homelab</code>

Voilà l'application est disponible sur [http://votredomaine/carnet-auto/](#) ! Vous pouvez vous connecter avec l'utilisateur par défaut : <code>admin/s3cr3t</code>

Pour changer le mot de passe de l'utilisateur et ajouter des utilisateurs rendez-vous sur l'application admin de Django via l'URL [http://votredomaine/admin/](#).
