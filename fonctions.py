from security import *


def donnees_dico(liste):
    """
    Transforme une liste de données en dictionnaire de données
    """
    l_comptes = liste[::2]
    l_mdp = liste[1::2]
    repertoire = {k[:-1]: v[:-1] for k, v in zip(l_comptes, l_mdp)}
    return repertoire


def donnees_liste(mdp_maitre):
    """
    Récupère les données du fichier et les transforme en liste
    """
    with open('.data/store.txt', "r") as fichier:
        elements = fichier.read().splitlines()
        l_comptes = elements[::2]
        l_mdp = elements[1::2]
        l_comptes = [decrypt(compte, mdp_maitre)
                     for compte in l_comptes]
        liste = []
        for i in range(len(l_comptes)):
            liste.append(f"{l_comptes[i]}\n")
            liste.append(f"{l_mdp[i]}\n")
    return liste


def donnees_dico_liste(data, mdp_maitre):
    """
    Transforme un dictionnaire de données en deux listes de données :
        - une chiffrée, pour écrire directement dans le fichier
        - une non-chiffrée, pour l'attribut donnees_liste de l'application
    """
    liste = []
    liste_chiffre = []
    for compte in data.keys():
        liste.append(f"{compte}\n")
        liste.append(f"{data[compte]}\n")
        liste_chiffre.append(f"{encrypt(compte, mdp_maitre)}\n")
        liste_chiffre.append(f"{data[compte]}\n")
    return liste, liste_chiffre


def index_liste(liste, compte):
    """
    Renvoie l'index d'un compte dans la liste des comptes
    """
    return liste[::2].index(compte) * 2


def domaine(link):
    """
    Renvoie le domaine d'un lien, ex : https://www.google.com -> google.com
    """
    link = link.split("/")[2]
    link = '.'.join(link.split('.')[-2:])
    return link


def link_login(chaine):
    """
    Sépare la partie correspondant au login et la partie correspondant au lien dans une chaine
    """
    len_link = int(chaine[-3:])
    chaine = chaine[:-3]
    if len_link == 0:
        login = chaine
        link = ''
    else:
        link = chaine[-len_link:]
        login = chaine[:-len_link]
    return link, login


def doubleauth_wait_prio_link(chaine):
    """
    Sépare la partie correspondant au temps d'attente, la partie correspondant à la priorité
    et la partie correspondant au lien dans une chaine
    """
    return chaine[0], chaine[1], chaine[2], chaine[3:]


def user_mdp(chaine):
    """
    Sépare la partie correspondant au login et la partie correspondant au mot de passe dans une chaine
    """
    len_user = int(chaine[-2:])
    chaine = chaine[:-2]
    if len_user == 0:
        mdp_recup = chaine
        user_recup = ''
    else:
        user_recup = chaine[-len_user:]
        mdp_recup = chaine[:-len_user]
    return user_recup, mdp_recup


def lien_valide(link):
    """
    Vérifie si un lien a un format valide
    """
    if link != '':
        if (link[:7] != 'http://' and link[:8] != 'https://') or len(link) > 997:
            return False
        else:
            domaine = link.split("/")[2]
            parties_domaines = domaine.split(".")
            parties_domaines = [partie for partie in parties_domaines if partie != '']
            if len(parties_domaines) < 2:
                return False
            else:
                return True
    return False


def donnees_valides(data):
    """
    Vérifie si un jeu de données est valide
    """
    try:
        for compte in data.keys():
            if type(compte) != str:
                return False

            if len(data[compte].keys()) == 2:
                if "user" not in data[compte].keys() or "password" not in data[compte].keys():
                    return False

                if len(data[compte]["user"]) > 99:
                    print(data[compte])
                    return False

                if type(data[compte]["user"]) != str or type(data[compte]["password"]) != str:
                    return False

            elif len(data[compte].keys()) == 6:
                cles = ["user", "password", "link", "doubleauth", "wait", "prio"]
                for cle in cles:
                    if cle not in data[compte].keys():
                        return False

                if not lien_valide(data[compte]["link"]):
                    return False

                if len(data[compte]["user"]) > 99:
                    return False

                if (data[compte]["wait"] not in ["0", "1"] or
                        data[compte]["prio"] not in ["0", "1"] or
                        data[compte]["doubleauth"] not in ["0", "1"]):
                    return False

                if (type(data[compte]["user"]) != str or type(data[compte]["password"]) != str or
                    type(data[compte]["link"]) != str or type(data[compte]["wait"]) != str or
                        type(data[compte]["prio"]) != str or type(data[compte]["doubleauth"]) != str):
                    return False

            else:
                return False

        return True
    except:
        return False
