#!/usr/bin/env python3
from gest import *
import socket
import sys


def get_lock(process_name):
    """
    Vériﬁe si le processus est déjà lancé :
    - Si oui, envoie un message au processus
    - Si non, lance le processus
    """
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        get_lock._lock_socket.bind('\0' + process_name)
        # print('I got the lock')

        os.system("python3 control.py")

    except socket.error:  # Erreur : le processus est déjà lancé
        # print('lock exists')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        try:
            sock.connect(('localhost', 9999))

            message = "lancer"  # message par défaut
            if len(sys.argv) > 1:  # Sinon, on envoie le message passé en argument (ex : "shutdown")
                message = sys.argv[1]

            sock.send(message.encode())
            sock.close()
        except:
            pass

        sys.exit()


def main():
    """
    Programme principal
    """
    # On se place dans le dossier du script
    file_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(file_directory)

    # L'unicité du processus et la connexion persitante n'est que prise en charge sur Linux
    if platform.system() != "Windows":
        get_lock('gestionnaire_mdp')
    else:
        app = Application()
        app.first_run()


if __name__ == '__main__':
    main()
