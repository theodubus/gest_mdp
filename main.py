#!/usr/bin/env python3
from gest import *


def ensure_data_files():
    """
    Crée le dossier .data et les fichiers de données vides s'ils n'existent pas.
    Un fichier vide correspond à l'état "aucune donnée" attendu par l'application
    (même état qu'après une suppression totale des données).
    """
    os.makedirs('.data', exist_ok=True)
    for nom in ('master_password.txt', 'preferences.txt', 'salt.txt', 'store.txt'):
        chemin = os.path.join('.data', nom)
        if not os.path.exists(chemin):
            with open(chemin, 'w'):
                pass


def main():
    """
    Programme principal
    """
    # On se place dans le dossier du script
    file_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(file_directory)

    # Les données ne sont pas versionnées, on les initialise si besoin
    ensure_data_files()

    app = Application()
    app.first_run()


if __name__ == '__main__':
    main()

    