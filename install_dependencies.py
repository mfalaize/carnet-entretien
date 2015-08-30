from pydepenv import install, upgrade_pip

if __name__ == '__main__':
    upgrade_pip()
    install('Django', '1.8.4')
    install('python-dateutil', '2.4.2')
    install('mysqlclient', '1.3.6', 'Installer les librairies mysql clientes avant d\'installer le carnet d\'entretien')
