#!/usr/bin/env python3
from gest import *


def main():
    """
    Programme principal
    """
    # On se place dans le dossier du script
    file_directory = os.path.dirname(os.path.realpath(__file__))
    os.chdir(file_directory)

    app = Application()
    app.first_run()


if __name__ == '__main__':
    main()

    