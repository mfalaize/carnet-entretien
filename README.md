HomeLab
=======

Site web Django contenant plusieurs applications pour la gestion de la vie quotidienne

### Installation via Docker

<code>wget https://raw.githubusercontent.com/mfalaize/homelab/master/docker_install.sh</code>

<code>chmod +x docker_install.sh</code>

<code>sudo ./docker_install.sh</code>

### Activation du HTTPS

<code>wget https://raw.githubusercontent.com/mfalaize/homelab/master/cert_install.sh</code>

<code>chmod +x cert_install.sh</code>

<code>sudo ./cert_install.sh votredomaine votremail</code>

Voilà l'application est disponible sur [https://votredomaine](#) ! Vous pouvez vous connecter avec l'utilisateur par défaut : <code>admin/s3cr3t</code>

Pour changer le mot de passe de l'utilisateur et ajouter des utilisateurs rendez-vous sur l'application admin de Django via l'URL [https://votredomaine/admin/](#).

### Mise à jour via Docker

Reéexcuter la procédure de [Installation via Docker](#installation-via-docker).