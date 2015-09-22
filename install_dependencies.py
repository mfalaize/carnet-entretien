from pydepenv import install, upgrade_pip

if __name__ == '__main__':
    upgrade_pip()
    install('Django', '1.8.4')
    install('python-dateutil', '2.4.2')
    install('django-bootstrap3', '6.2.2')
    install('django-widget-tweaks', '1.4.1')
    install('Pillow', '2.9.0')
    install('django-extra-views', '0.7.1')
    install('django-formset-js', '0.5.0')
    install('mysqlclient', '1.3.6', 'Installer les librairies mysql clientes avant d\'installer le carnet d\'entretien')
