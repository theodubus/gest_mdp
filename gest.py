# imports
from tkinter import *
from tkinter import filedialog
from functools import partial
from fonctions import *
from string import *
import time
import random
import pyperclip
import os
import scroll
import threading
from time import sleep
import platform
import json
from copy import copy
import ttkthemes
from screeninfo import get_monitors
from customtkinter import *
from PIL import Image
from server import *
import webbrowser

set_appearance_mode("Light")

# Gestionnaire (codé en objet)
class Application:
    def __init__(self):
        """
        Init : initialisation des variables
        """

        # web
        self.server = None
        self.login_urls = dict()
        self.login_links = []
        self.temp = dict()

        # preferences
        keys = ['chiffres', 'lettresmin', 'lettresmaj', 'ponctuation', 'cara_spe', 'no_similar',
                'taille', 'autoconnexion']
        elements = ['1', '1', '1', '0', '0', '1', '25', '1']
        self.preferences = {k: v for k, v in zip(keys, elements)}

        # Tkinter
        self.label = dict()
        self.input = dict()
        self.button = dict()
        self.visible = dict()
        self.frame = dict()
        self.stringvar = dict()
        self.slider = dict()
        self.menu_deroulant = dict()
        self.frames_comptes = dict()
        self.checkBouton = dict()
        self.radioBouton = dict()
        self.generer_f = None
        self.confirmer_f = None
        self.appui_valider = False

        # Sécurité / mot de passe
        self.mdp_gen = ''
        self.mdp_maitre = None
        self.mdp_user = None
        self.f = '.data/store.txt'

        # Définition des logos
        self.oeil = None
        self.oeil_disabled = None
        self.crayon = None
        self.copier = None
        self.copier_disabled = None
        self.poubelle = None
        self.web = None
        self.web_disabled = None
        self.oeil_a = None
        self.logo = None

        # Initialisation des autres données
        self.accueil = None
        self.menu = None
        self.donnees = dict()
        self.copie_donnees = dict()
        self.donnees_liste = list()
        self.stop = False
        self.deconnexion = False
        self.daemon_server_thread = None
        self.server_thread = None

    def first_run(self):
        """
        Première ouverture du programme

        Déroulé :
        - Création de la fenêtre d'acceuil (première connexion ou page de login)
        - Si première connexion ou authentification réussie :
        - Création et lancement de la fenêtre de menu (fenêtre principale)
        """

        self.mdp_maitre = None
        self.accueil = Fenetre(600, 400, 'Accueil')
        self.oeil_a = CTkImage(Image.open("images/oeil_a.png"), size=(25, 20))
        self.logo = PhotoImage(file="images/logo.png")
        self.accueil.iconphoto(True, self.logo)

        # Pas de mot de passe maître = première connexion
        if current_password() == "":

            self.accueil.configure(padx=105, pady=30)

            # Construction de la fenêtre
            self.build_accueil_premiere()

            # Ajout d'un raccourci clavier
            self.accueil.bind('<Return>', partial(self.creer_mdp_maitre))

        # Sinon, ouverture avec page de login
        else:
            self.accueil.configure(padx=105, pady=80)

            # Construction de la fenêtre
            self.build_accueil()

            # Ajout d'un raccourci clavier
            self.accueil.bind('<Return>', partial(self.valider, 'mdp_accueil', self.accueil))

        # Taille non modifiable
        self.accueil.resizable(width=False, height=False)

        # Ajout d'un raccourci clavier
        self.accueil.bind('<Control-BackSpace>', partial(self.effacer, self.accueil))
        self.accueil.bind('<Control-Delete>', partial(self.effacer_fin, self.accueil))
        self.accueil.bind('<Control-a>', partial(self.tout_selectionner, self.accueil))


        self.accueil.protocol("WM_DELETE_WINDOW", partial(self.fermeture, "accueil"))

        # Lancement de la fenêtre
        # La véfifcation du mot de passe est faite dedans
        self.accueil.mainloop()

        # Revérification du mot de passe une fois la fenêtre fermée (car fermée soit par
        # la croix, soit par une authentification correcte)
        if not self.mdp_maitre or not get_master_password(self.mdp_user):
            if platform.system() == "Windows":
                exit()
            else:
                return


        self.run()

    def run(self):
        """
        Ouverture de la partie principale du programme : le menu
            - Accès aux données et à toutes les fonctionnalités du logiciel
        """
        self.menu = Fenetre(700, 450, 'Menu')
        self.oeil = CTkImage(Image.open("images/oeil.png"), size=(25, 20))
        self.oeil_disabled = CTkImage(Image.open("images/oeil_disabled.png"), size=(25, 20))
        self.crayon = CTkImage(Image.open("images/crayon.png"), size=(25, 21))
        self.copier = CTkImage(Image.open("images/copier.png"), size=(20, 25))
        self.copier_disabled = CTkImage(Image.open("images/copier_disabled.png"), size=(20, 25))
        self.poubelle = CTkImage(Image.open("images/poubelle.png"), size=(25, 25))
        self.web = CTkImage(Image.open("images/web.png"), size=(25, 25))
        self.web_disabled = CTkImage(Image.open("images/web_disabled.png"), size=(25, 25))
        self.logo = PhotoImage(file="images/logo.png")
        self.menu.iconphoto(True, self.logo)

        # Données sous forme de liste, compte déchiffré et mots de passes chiffrés
        # (ex : ['compte1\n', 'mdp_compte1_chiffre\n', 'compte2\n', 'mdp_compte2_chiffre\n']
        # La liste permet une insertion/modification/suppression plus facile et rapide dans le fichier
        # self.donnees_liste = donnees_liste(self.mdp_maitre)
        if not self.donnees_liste:
            self.donnees_liste = donnees_liste(self.mdp_maitre)

            # Données sous forme de dictionnaire, compte déchiffré et mots de passes chiffrés
            # (ex : {'compte1': 'mdp_compte1_chiffre', 'compte2' : 'mdp_compte2_chiffre'})
            # Le dictionnaire permet un accès aux données plus simple dans le programme
            self.donnees = donnees_dico(self.donnees_liste)

        self.menu.configure(padx=60, pady=40)

        # Construction de la fenêtre
        self.build_menu()

        # Ajout de raccourcis clavier
        self.menu.bind('<Control-BackSpace>', partial(self.effacer_update))
        self.menu.bind('<Control-Delete>', partial(self.effacer_fin_update))
        self.menu.bind('<Control-a>', partial(self.tout_selectionner, self.menu))
        self.menu.bind('<KeyPress>', partial(self.update))
        self.menu.resizable(width=False, height=False)

        self.menu.protocol("WM_DELETE_WINDOW", partial(self.fermeture, "menu"))

        # Lancement de la fenêtre
        self.menu.mainloop()

    def fermeture(self, fenetre):
        """
        Méthode qui gère le nettoyage des données après fermeture de l'application
        → Nécessaire pour la connexion persistante sous Linux
        """
        if fenetre == "accueil":
            self.accueil.destroy()
        elif fenetre == "menu":
            self.menu.destroy()

        # remise à zéro des données
        self.menu = None
        self.accueil = None
        self.stop = True
        self.deconnexion = False
        self.oeil_a = None
        self.oeil = None
        self.crayon = None
        self.copier = None
        self.poubelle = None
        self.web = None
        self.label = dict()
        self.input = dict()
        self.button = dict()
        self.visible = dict()
        self.frame = dict()
        self.stringvar = dict()
        self.slider = dict()
        self.menu_deroulant = dict()
        self.frames_comptes = dict()
        self.checkBouton = dict()
        self.radioBouton = dict()
        self.generer_f = None
        self.confirmer_f = None
        self.appui_valider = False
        self.login_urls = dict()
        self.login_links = []
        self.temp = dict()
        self.delete_server()

    def build_accueil(self):
        """
        Construction de la fenêtre d'accueil

        Déroulé :
            - Création des différents éléments :
                - Label descriptif
                - Input mot de passe
                - Bouton "voir"
                - Bouton valider
                - Label caché en cas de mauvais mot de passe
            - L'interaction se fait avec les fonctions appelées par les boutons
        """

        self.mdp_user = None

        self.create_label(self.accueil, 'label_accueil', "Entrez votre mot de passe :",
                          0, 0, columnspan=2, pady=(0, 50), font=("arial", 20))
        self.add_input(self.accueil, 'mdp_accueil', 1, 0, width=350, focus=True, show=False, sticky='news', placeholder="Mot de passe")
        self.create_button(self.accueil, 'valider_accueil', 'Valider', 2, 0, columnspan=2,
                           commande=partial(self.valider, 'mdp_accueil', self.accueil), bg='green',
                           fg='white', abg='#009020', afg='white', pady=(50, 0), font=("arial", 15))
        self.create_button(self.accueil, 'voir_accueil', '', 1, 1,
                           commande=partial(self.voir, 'mdp_accueil'), image=self.oeil_a, bg="#DEDEDE", abg="#ECECEC", height=34)

        self.stringvar['erreur'] = StringVar()
        self.label['mauvais_mdp'] = CTkLabel(self.accueil,
                                             textvariable=self.stringvar['erreur'], text_color='red', font=("arial", 20, "bold"))
        self.label['mauvais_mdp'].grid(row=3, column=0, columnspan=2, pady=30)

    def build_accueil_premiere(self):
        """
        Construction de la fenêtre d'accueil (première connexion)

        Déroulé :
            - Création des différents éléments :
                - Label descriptif
                - Input mot de passe (*2 pour la confirmation)
                - Bouton "voir" (*2)
                - Bouton valider
            - L'interaction se fait avec les fonctions appelées par les boutons
        """
        self.mdp_user = None

        self.create_label(self.accueil, 'bienvenue', 'Bienvenue', 0, 0,
                          columnspan=2, pady=(0, 25), font=("arial", 20, "bold"))

        self.create_label(self.accueil, 'label_accueil', "Nouveau mot de passe :", 1, 0, sticky='w', pady=(0, 10))
        self.add_input(self.accueil, 'mdp_accueil', 2, 0, width=350, focus=True, show=False, sticky='news', placeholder="Mot de passe")

        self.create_button(self.accueil, 'voir_accueil', '', 2, 1,
                           commande=partial(self.voir, 'mdp_accueil'), image=self.oeil_a, bg="#DEDEDE", abg="#ECECEC", height=34)

        self.create_label(self.accueil, 'label_accueil_conf',
                          "Confirmation mot de passe :", 3, 0, sticky='w', pady=(30, 10))
        self.add_input(self.accueil, 'mdp_accueil_conf', 4, 0, width=350, focus=False, show=False, sticky='news', placeholder="Confirmation mot de passe")

        self.create_button(self.accueil, 'voir_accueil', '', 4, 1,
                           commande=partial(self.voir, 'mdp_accueil_conf'), image=self.oeil_a, bg="#DEDEDE", abg="#ECECEC", height=34)

        self.create_button(self.accueil, 'valider_accueil', 'Valider', 5, 0, columnspan=2, fg='white', abg='#009020',
                           afg='white', commande=partial(self.creer_mdp_maitre), bg='green', pady=(30, 0))

    def build_menu(self):
        """
        Construction de la fenêtre de menu (fenêtre principale)

        Déroulé :
            - Si autocompletion activée :
                - Récupération des liens de connexion (dans un autre thread pour ne pas bloquer le programme)
                - Création du thread de connexion automatique
            - Récupération des préférences (dans un autre thread pour ne pas bloquer le programme)
            - Création des différents éléments :
                - Champ de recherche
                - Bouton d'ajout
                - Frame contenant la frame scrollable (fixe)
                - Frame contenant les données des comptes (scrollable)
                - Frame pour chaque compte, elles-mêmes dans la frame des comptes
                - Scrollbar pour la frame des comptes
                - Menu déroulant :
                    - Ajouter un compte
                    - Préférences
                    - Générer un mot de passe sans l'enregistrer
                    - Modifier le mot de passe maître
                    - Supprimer toutes les données
            - L'interaction se fait avec les fonctions appelées par les boutons
        """

        threading.Thread(target=self.update_preferences).start()
        threading.Thread(target=self.get_links).start()
        self.daemon_server_thread = threading.Thread(target=self.autoconnect)
        self.daemon_server_thread.start()

        if platform.system() != "Windows":
            largeur = 480
            self.menu.style.theme_use('ubuntu')
        else:
            largeur = 580

        self.add_input(self.menu, 'recherche', 0, 0, focus=True, sticky='news', pady=(0, 5), placeholder="Rechercher")
        self.create_button(self.menu, '+', 'Nouveau', 0, 1, pady=(0, 5),
                           commande=partial(self.create_toplevel, 450, 600, 'Créer', 'generer', 'creer', 60, 25,
                                            fc=partial(self.build_creer)), fg="white", bg=None, abg=None, width=75)

        self.add_checkbutton(self.menu, 'auto', 'autoconnexion', 1, 0, '1', '0', self.preferences['autoconnexion'],
                             font=("arial", 20))

        self.create_frame(self.menu, 'liste_handler', 2, 0, columnspan=2, pady=(5, 25), sticky='news')
        self.create_scrollable_frame(self.frame['liste_handler'], 'liste')

        self.menu_deroulant['options'] = Menu(self.menu, bg="#F1F1F1", tearoff=0, activebackground="#CCCCCC")
        self.menu_deroulant['1'] = Menu(self.menu_deroulant['options'], tearoff=0, bg="#F1F1F1", activeborderwidth=0, activebackground="#CCCCCC")
        self.menu_deroulant['donnees'] = Menu(self.menu_deroulant['1'], tearoff=0, bg="#F1F1F1", activeborderwidth=0, activebackground="#CCCCCC")
        self.menu_deroulant['profil'] = Menu(self.menu_deroulant['1'], tearoff=0, bg="#F1F1F1", activeborderwidth=0, activebackground="#CCCCCC")
        self.menu_deroulant['securite'] = Menu(self.menu_deroulant['profil'], tearoff=0, bg="#F1F1F1", activeborderwidth=0, activebackground="#CCCCCC")

        self.menu_deroulant['1'].add_command(label='Générer',
                                             command=partial(self.create_toplevel, 450, 400, 'Générer', 'generer',
                                                             'generer', 60, 40, fc=partial(self.build_generer)), underline=0, accelerator="Ctrl+G")
        self.menu.bind_all("<Control-g>", partial(self.create_toplevel, 450, 400, 'Générer', 'generer', 'generer', 60, 40, fc=partial(self.build_generer)))
        self.menu_deroulant['1'].add_command(label='Nouveau compte',
                                             command=partial(self.create_toplevel, 450, 600, 'Créer', 'generer',
                                                             'creer', 60, 25, fc=partial(self.build_creer)), underline=0, accelerator="Ctrl+N")
        self.menu.bind_all("<Control-n>", partial(self.create_toplevel, 450, 600, 'Créer', 'generer', 'creer', 60, 25, fc=partial(self.build_creer)))
        self.menu_deroulant['1'].add_separator()
        self.menu_deroulant['donnees'].add_command(label='Importer des données',
                                                   command=partial(self.importer), underline=0)
        self.menu_deroulant['donnees'].add_command(label='Exporter les données',
                                                   command=partial(self.exporter), underline=0)

        self.menu_deroulant['1'].add_cascade(label="Données", menu=self.menu_deroulant['donnees'], underline=0)
        self.menu_deroulant['securite'].add_command(label='Modifier le mot de passe utilisateur',
                                                    command=partial(self.create_toplevel, 450, 370,
                                                                    'Modifier le mot de passe utilisateur',
                                                                    'generer', 'modifier_mdp_user', 60, 30,
                                                                    fc=partial(self.build_modifier_mdp_user)), underline=0)
        self.menu_deroulant['securite'].add_command(label='Changer de clé de chiffrement',
                                                    command=partial(self.create_toplevel, largeur, 370,
                                                                    'Changer de clé de chiffrement',
                                                                    'generer', 'modifier_mdp_maitre', 60, 30,
                                                                    fc=partial(self.build_modifier_mdp_maitre)), underline=0)
        self.menu_deroulant['securite'].add_command(label='Supprimer toutes les données',
                                                    command=partial(self.create_toplevel, 600, 400,
                                                                    'Supprimer toutes les données', 'generer',
                                                                    'tout_supprimer', 145, 35,
                                                                    fc=partial(self.build_tout_supprimer)), underline=0)
        self.menu_deroulant['profil'].add_cascade(label="Sécurité", menu=self.menu_deroulant['securite'], underline=0)
        self.menu_deroulant['profil'].add_command(label='Modifier Préférences',
                                                  command=partial(self.create_toplevel, 410, 450,
                                                                  'Modifier Préférences', 'generer', 'preferences', 60,
                                                                  40, fc=partial(self.build_preferences)), underline=0, accelerator="Ctrl+P")
        self.menu.bind_all("<Control-p>", partial(self.create_toplevel, 410, 450, 'Modifier Préférences', 'generer', 'preferences', 60, 40, fc=partial(self.build_preferences)))
        self.menu_deroulant['1'].add_cascade(label="Profil", menu=self.menu_deroulant['profil'], underline=0)

        if platform.system() != "Windows":
            self.menu_deroulant['1'].add_separator()
            self.menu_deroulant['1'].add_command(label='Se déconnecter', command=partial(self.deconnecter), underline=0, accelerator="Ctrl+Q")
            self.menu.bind_all("<Control-q>", partial(self.deconnecter))

        self.menu_deroulant['options'].add_cascade(label="Options", menu=self.menu_deroulant['1'], underline=0)
        self.menu.configure(menu=self.menu_deroulant['options'])
        self.menu.grid_rowconfigure(1, weight=1)
        self.menu.grid_columnconfigure(0, weight=1)

        self.update()

    def deconnecter(self, event=None):
        """
        Méthode qui permet de se déconnecter et d'arrêter la connexion persistante
        """
        self.menu.destroy()
        self.deconnexion = True
        self.stop = True
        self.delete_server()
        self.daemon_server_thread.join()
        threading.Thread(target=os.system, args=("python3 main.py shutdown",)).start()

    def build_generer(self):
        """
        Construction de la fenêtre de génération de mot de passe (Génération sans enregistrement)

        Déroulé :
            - Création des différents éléments :
                - Label contenant le mot de passe généré
                - Bouton "voir"
                - Bouton copier
                - Checkbox d'options pour le mot de passe
                - Input pour la taille du mot de passe
                - Bouton générer
            - L'interaction se fait avec les fonctions appelées par les boutons
        """
        self.generer_f.bind('<Return>', partial(self.generer_mdp))

        self.create_label(self.generer_f, 'generer_mdp', '', 0, 0, bg='white', textvar=True,
                          sticky='ew', anchor='center', columnspan=2, font=('arial', 20), padx=(50, 0), pady=20, corner_radius=5)
        self.generer_f.grid_columnconfigure(0, weight=1)
        self.create_button(self.generer_f, 'voir', '', 0, 2, image=self.oeil,
                           width=30, commande=partial(self.voir_gen), bg="#DEDEDE", abg="#ECECEC", height=30)
        self.create_button(self.generer_f, 'copier', '', 0, 3, image=self.copier,
                           width=38, height=30, commande=partial(self.copier_gen), bg="#DEDEDE", abg="#ECECEC", padx=(0, 50), font=('arial', 20))

        self.add_checkbutton(self.generer_f, 'chiffres', '0-9', 1, 0,
                             digits, '', self.preferences['chiffres'], commande=partial(self.generer_mdp), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'lettresmin', 'a-z', 2, 0,
                             ascii_lowercase, '', self.preferences['lettresmin'], commande=partial(self.generer_mdp), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'lettresmaj', 'A-Z', 3, 0,
                             ascii_uppercase, '', self.preferences['lettresmaj'], commande=partial(self.generer_mdp), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'ponctuation', '!#/', 4, 0,
                             punctuation, '', self.preferences['ponctuation'], commande=partial(self.generer_mdp), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'cara_spe', '£çÉ', 5, 0,
                             "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨", '', self.preferences['cara_spe'], commande=partial(self.generer_mdp), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'double', 'no 0OIl', 6, 0, "on", 'off', self.preferences['no_similar'], commande=partial(self.generer_mdp), padx=(50, 0), font=('arial', 20))
        self.create_label(self.generer_f, 'taille', 'Taille (10-100) : ', 7, 0,
                          font=('arial', 15, "bold"), sticky='w', padx=(50, 0), pady=(20, 0))

        self.create_slider(self.generer_f, "taille", 8, 0, columnspan=4, default=int(self.preferences['taille']),
                           debut=10, fin=100, commande=partial(self.generer_mdp), pady=(15, 15), width=350)
        self.add_input(self.generer_f, 'taille', 7, 1, sticky='w',
                       width=30, padx=(0, 100), exists=True, focus=True)

        self.input['taille']._entry.icursor('end')
        self.create_button(self.generer_f, 'generer', 'Générer', 9, 0, columnspan=4,
                           bg='#009020', fg='white', abg='#00A030', afg='white', commande=partial(self.generer_mdp), padx=50)
        self.generer_mdp()
        self.voir_gen()

    def update_preferences(self):
        """
        Mise à jour des variables de préférences
        """
        with open(".data/preferences.txt", 'r') as f:
            elements = f.read().splitlines()
            if len(elements) != 8:
                elements = ['1', '1', '1', '0', '0', '1', '25', '1']
        keys = ['chiffres', 'lettresmin', 'lettresmaj', 'ponctuation', 'cara_spe',
                'no_similar', 'taille', 'autoconnexion']
        self.preferences = {k: v for k, v in zip(keys, elements)}

        try:
            self.preferences['taille'] = int(self.preferences['taille'])
            if self.preferences['taille'] < 10 or self.preferences['taille'] > 100:
                self.preferences['taille'] = 15
        except:
            self.preferences['taille'] = 15

        self.preferences['taille'] = str(self.preferences['taille'])

        if self.preferences['chiffres'] == '1':
            self.preferences['chiffres'] = digits
        else:
            self.preferences['chiffres'] = ''
        if self.preferences['lettresmin'] == '1':
            self.preferences['lettresmin'] = ascii_lowercase
        else:
            self.preferences['lettresmin'] = ''
        if self.preferences['lettresmaj'] == '1':
            self.preferences['lettresmaj'] = ascii_uppercase
        else:
            self.preferences['lettresmaj'] = ''
        if self.preferences['ponctuation'] == '1':
            self.preferences['ponctuation'] = punctuation
        else:
            self.preferences['ponctuation'] = ''
        if self.preferences['cara_spe'] == '1':
            self.preferences['cara_spe'] = "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨"
        else:
            self.preferences['cara_spe'] = ''
        if self.preferences['no_similar'] == '1':
            self.preferences['no_similar'] = "on"
        else:
            self.preferences['no_similar'] = 'off'
        if self.preferences['autoconnexion'] not in {'1', '0'}:
            self.preferences['autoconnexion'] = '0'

    def build_preferences(self):
        """
        Construction de la fenêtre de préférences

        Déroulé :
            - Récupération des préférences actuelles
            - Création des différents éléments :
                - fichier profil web
                - options par défaut de mot de passe
                - autoconnexion
                - bouton "modifier"
            - L'interaction se fait avec les fonctions appelées par les boutons
        """

        self.generer_f.bind('<Return>', partial(self.modifier_preferences))

        self.update_preferences()

        self.generer_f.grid_columnconfigure(0, weight=2)
        self.generer_f.grid_columnconfigure(1, weight=1)

        # label au centre
        self.create_label(self.generer_f, 'Préférences', 'Préférences', 0, 0, font=('arial', 30, "bold"), pady=(20, 20), columnspan=2, sticky='nsew')

        self.add_checkbutton(self.generer_f, 'autoconnexion', 'auto', 1, 0, "1", '0', self.preferences['autoconnexion'], font=('arial', 20), padx=(50, 0))
        self.add_checkbutton(self.generer_f, 'chiffres', '0-9', 2, 0, digits, '', self.preferences['chiffres'], font=('arial', 20), padx=(50, 0))
        self.add_checkbutton(self.generer_f, 'lettresmin', 'a-z', 3, 0,
                             ascii_lowercase, '', self.preferences['lettresmin'], font=('arial', 20), padx=(50, 0))
        self.add_checkbutton(self.generer_f, 'lettresmaj', 'A-Z', 4, 0,
                             ascii_uppercase, '', self.preferences['lettresmaj'], font=('arial', 20), padx=(50, 0))
        self.add_checkbutton(self.generer_f, 'ponctuation', '!#/', 5, 0,
                             punctuation, '', self.preferences['ponctuation'], font=('arial', 20), padx=(50, 0))
        self.add_checkbutton(self.generer_f, 'cara_spe', '£çÉ', 6, 0,
                             "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨", '', self.preferences['cara_spe'], font=('arial', 20), padx=(50, 0))
        self.add_checkbutton(self.generer_f, 'double', 'no 0OIl', 7, 0, "on", 'off', self.preferences['no_similar'], font=('arial', 20), padx=(50, 0))
        self.create_label(self.generer_f, 'taille', 'Taille (10-100) : ', 8, 0,
                          font=('arial', 15, "bold"), sticky='w', padx=(50, 0), pady=(25, 0))

        self.create_slider(self.generer_f, "taille", 9, 0, columnspan=2, default=int(self.preferences['taille']),
                           debut=10, fin=100, pady=(15, 15), width=310)
        self.add_input(self.generer_f, 'taille', 8, 1, sticky='w',
                       width=30, padx=(0, 100), exists=True, pady=(25, 0))

        self.create_button(self.generer_f, 'modifier', 'Modifier', 10, 0, columnspan=2,
                           bg='#009020', fg='white', abg='#00A030', afg='white',
                           commande=partial(self.modifier_preferences), padx=50)

    def build_modifier(self, compte):
        """
        Construction de la fenêtre de modification d'un compte

        Déroulé :
            - Création des différents éléments :
                - Label contenant le nom du compte
                - Input contenant le login
                - Input contenant le lien de connexion
                - Input contenant le mot de passe
                - Input pour la taille du mot de passe
                - Checkbox d'options pour le mot de passe
                - Checkbox de priorité de connexion (connexion auto)
                - Checkbox de délai avant tentative connexion (Si un site a un temps de chargement long)
                - Bouton "voir"
                - Bouton copier
                - Bouton générer
                - Bouton Modifier (valider la modification)
            - L'interaction se fait avec les fonctions appelées par les boutons
        """
        chaine_clair = decrypt(self.donnees[compte], self.mdp_maitre)
        link, login = link_login(chaine_clair)
        user, password = user_mdp(login)
        if link != '':
            doubleauth, wait, prio, link = doubleauth_wait_prio_link(link)
        else:
            doubleauth, wait, prio, link = '0', '0', '0', ''

        self.generer_f.bind('<Return>', partial(self.create_toplevel, 350, 200, '', 'confirmer',
                                                'confirmation', 30, 15, compte=compte))

        self.create_label(self.generer_f, 'compte_mdp', 'Compte : ', 0, 0, sticky='ew',
                          anchor='w', pady=(20, 15), font=("arial", 22, "bold"), padx=(50, 0))
        self.add_input(self.generer_f, 'nom_compte', 0, 1, sticky='ew', columnspan=3, focus=True, pady=(20, 15), placeholder="Nom du compte", padx=(0, 50), default=compte)
        self.input['nom_compte']._entry.icursor('end')

        self.create_label(self.generer_f, 'user_label', 'Utilisateur : ', 1, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 22, "bold"), padx=(50, 0))
        self.add_input(self.generer_f, 'username', 1, 1, sticky='news', columnspan=3, pady=(0, 15), padx=(0, 50), default=user, placeholder="Nom d'utilisateur")

        self.create_label(self.generer_f, 'link_label', 'Lien : ', 2, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 22, "bold"), padx=(50, 0))
        self.add_input(self.generer_f, 'link', 2, 1, sticky='news', columnspan=3, pady=(0, 10), default=link, placeholder="Lien de connexion", padx=(0, 50))
        self.add_checkbutton(self.generer_f, 'prio', 'prio', 3, 0, '1', '0', prio, pady=(0, 10), padx=(50, 0), font=("arial", 20))
        self.add_checkbutton(self.generer_f, 'long', 'submit', 3, 1, '1', '0', wait, font=("arial", 20))
        self.add_checkbutton(self.generer_f, 'doubleauth', '2FA', 3, 2, '1', '0', doubleauth, columnspan=2, font=("arial", 20))

        self.add_input(self.generer_f, 'generer_mdp', 4, 0, sticky='news', columnspan=2, pady=(10, 10), show=False, default=password, placeholder="Mot de passe", padx=(50, 0))
        self.generer_f.grid_columnconfigure(0, weight=1)
        self.create_button(self.generer_f, 'voir', '', 4, 2, image=self.oeil,
                           width=30, commande=partial(self.voir), bg="#DEDEDE", abg="#ECECEC", height=30)
        self.create_button(self.generer_f, 'copier', '', 4, 3, image=self.copier,
                           width=38, height=30, commande=partial(self.copier_gen_modif), bg="#DEDEDE", abg="#ECECEC", padx=(0, 50))

        self.add_checkbutton(self.generer_f, 'chiffres', '0-9', 5, 0,
                             digits, '', self.preferences['chiffres'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'lettresmin', 'a-z', 6, 0,
                             ascii_lowercase, '', self.preferences['lettresmin'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'lettresmaj', 'A-Z', 7, 0,
                             ascii_uppercase, '', self.preferences['lettresmaj'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'ponctuation', '!#/', 8, 0,
                             punctuation, '', self.preferences['ponctuation'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'cara_spe', '£çÉ', 9, 0,
                             "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨", '', self.preferences['cara_spe'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'double', 'no 0OIl', 10, 0, "on", 'off', self.preferences['no_similar'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.create_label(self.generer_f, 'taille', 'Taille (10-100) : ', 11, 0,
                          font=('arial', 15, "bold"), sticky='ew', anchor='w', pady=(10, 10), padx=(50, 0))
        self.create_slider(self.generer_f, "taille", 12, 0, columnspan=4, default=int(self.preferences['taille']),
                           debut=10, fin=100, commande=partial(self.generer_mdp_modif), pady=(0, 0), width=350)
        self.add_input(self.generer_f, 'taille', 11, 1, sticky='w',
                       width=30, padx=(0, 100), exists=True)
        self.create_button(self.generer_f, 'generer', 'Générer', 13, 0, columnspan=4,
                           bg='#1030EE', fg='white', abg='#2050FF', afg='white',
                           commande=partial(self.generer_mdp_modif), pady=(15, 10), padx=(50, 50))
        self.create_button(self.generer_f, 'modifier', 'Modifier', 14, 0, columnspan=4,
                           bg='#009020', fg='white', abg='#00A030', afg='white',
                           commande=partial(self.create_toplevel, 350, 200, '', 'confirmer',
                                            'confirmation', 30, 15, compte=compte), padx=(50, 50))

    def build_creer(self):
        """
        Construction de la fenêtre de modification d'un compte

        Déroulé :
            - Création des différents éléments :
                - Input pour nom du compte
                - Input pour le login
                - Input pour le lien de connexion
                - Input pour le mot de passe
                - Input pour la taille du mot de passe
                - Checkbox d'options pour le mot de passe
                - Checkbox de priorité de connexion (connexion auto)
                - Checkbox de délai avant tentative connexion (Si un site a un temps de chargement long)
                - Bouton "voir"
                - Bouton copier
                - Bouton générer
                - Bouton Créer (valider la création)
            - L'interaction se fait avec les fonctions appelées par les boutons
        """
        self.generer_f.bind('<Return>', partial(self.creer_mdp))

        self.create_label(self.generer_f, 'compte_mdp', 'Compte : ', 0, 0, sticky='ew',
                          anchor='w', pady=(20, 15), font=("arial", 22, "bold"), padx=(50, 0))
        self.add_input(self.generer_f, 'nom_compte', 0, 1, sticky='ew', columnspan=3, focus=True, pady=(20, 15), placeholder="Nom du compte", padx=(0, 50))

        self.create_label(self.generer_f, 'user_label', 'Utilisateur : ', 1, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 22, "bold"), padx=(50, 0))
        self.add_input(self.generer_f, 'username', 1, 1, sticky='ew', columnspan=3, pady=(0, 15), padx=(0, 50), placeholder="Nom d'utilisateur")

        self.create_label(self.generer_f, 'link_label', 'Lien : ', 2, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 22, "bold"), padx=(50, 0))
        self.add_input(self.generer_f, 'link', 2, 1, sticky='ew', columnspan=3, pady=(0, 10), placeholder="Lien de connexion", padx=(0, 50))

        self.add_checkbutton(self.generer_f, 'prio', 'prio', 3, 0, '1', '0', '0', pady=(0, 10), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'long', 'long', 3, 1, '1', '0', '0', font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'doubleauth', '2FA', 3, 2, '1', '0', '0', columnspan=2, font=('arial', 20))

        self.add_input(self.generer_f, 'generer_mdp', 4, 0, sticky='news', columnspan=2, pady=(10, 10), show=False, placeholder="Mot de passe", default="_", padx=(50, 0))
        self.generer_f.grid_columnconfigure(0, weight=1)
        self.create_button(self.generer_f, 'voir', '', 4, 2, image=self.oeil, width=30,
                            commande=partial(self.voir), bg="#DEDEDE", abg="#ECECEC", height=30)
        self.create_button(self.generer_f, 'copier', '', 4, 3, image=self.copier, width=38,
                            height=30, commande=partial(self.copier_gen_modif), bg="#DEDEDE", abg="#ECECEC", padx=(0, 50))

        self.add_checkbutton(self.generer_f, 'chiffres', '0-9', 5, 0, digits, '', self.preferences['chiffres'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'lettresmin', 'a-z', 6, 0,
                             ascii_lowercase, '', self.preferences['lettresmin'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'lettresmaj', 'A-Z', 7, 0,
                             ascii_uppercase, '', self.preferences['lettresmaj'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'ponctuation', '!#/', 8, 0,
                             punctuation, '', self.preferences['ponctuation'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'cara_spe', '£çÉ', 9, 0,
                             "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨", '', self.preferences['cara_spe'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))
        self.add_checkbutton(self.generer_f, 'double', 'no 0OIl', 10, 0, "on", "off", self.preferences['no_similar'], commande=partial(self.generer_mdp_modif), padx=(50, 0), font=('arial', 20))

        self.create_label(self.generer_f, 'taille', 'Taille (10-100) : ', 11, 0, sticky='ew',
                          anchor='w', pady=(10, 10), font=("arial", 15, "bold"), padx=(50, 0))
        self.create_slider(self.generer_f, "taille", 12, 0, columnspan=4, default=int(self.preferences['taille']),
                           debut=10, fin=100, commande=partial(self.generer_mdp_modif), pady=(0, 0), width=350)
        self.add_input(self.generer_f, 'taille', 11, 1, sticky='w',
                       width=30, padx=(0, 100), exists=True)
        self.input['taille']._entry.icursor('end')
        self.create_button(self.generer_f, 'generer', 'Générer', 13, 0, columnspan=4,
                           bg='#1030EE', fg='white', abg='#2050FF', afg='white',
                           commande=partial(self.generer_mdp_modif), pady=(15, 10), padx=(50, 50))
        self.create_button(self.generer_f, 'creer', 'Créer', 14, 0, columnspan=4, bg='#009020',
                           fg='white', abg='#00A030', afg='white', commande=partial(self.creer_mdp), padx=(50, 50))
        self.generer_mdp_modif()

    def add_checkbutton(self, fenetre, index, texte, row, column, on, off, default, padx=None, pady=(3, 3),
                        columnspan=1, commande=None, font=("arial", 15)):
        """
        Ajout d'une checkbox à la fenêtre

        Permet l'ajout facile, car gère tout :
            - Création de la variable de contenu de la checkbox
            - Création de la checkbox
            - Sauvegarde de la checkbox dans un dictionnaire (permettant de garder la trace des éléments)
            - Ajout de la checkbox dans la fenêtre
        """
        self.stringvar[f'check{index}'] = StringVar()
        self.stringvar[f'check{index}'].set(default)
        self.checkBouton[index] = CTkCheckBox(fenetre, text=texte, variable=self.stringvar[f'check{index}'],
                                              offvalue=off, onvalue=on, font=font, command=commande)
        self.checkBouton[index].grid(row=row, column=column, padx=padx, pady=pady, sticky='w', columnspan=columnspan)

    def add_switch(self, fenetre, index, texte, row, column, on, off, default, padx=None, pady=(3, 3),
                        columnspan=1, commande=None, font=("arial", 15)):
        """
        Ajout d'une switch à la fenêtre, fonctionne comme une checkbox

        Permet l'ajout facile, car gère tout :
            - Création de la variable de contenu de la switch
            - Création de la switch
            - Sauvegarde de la switch dans un dictionnaire (permettant de garder la trace des éléments)
            - Ajout de la switch dans la fenêtre
        """
        self.stringvar[f'check{index}'] = StringVar()
        self.stringvar[f'check{index}'].set(default)
        self.checkBouton[index] = CTkSwitch(fenetre, text=texte, variable=self.stringvar[f'check{index}'],
                                              offvalue=off, onvalue=on, font=font, command=commande)
        self.checkBouton[index].grid(row=row, column=column, padx=padx, pady=pady, sticky='w', columnspan=columnspan)

    def add_radiobutton(self, fenetre, index, texte, row, column, value, default=False, padx=None, commande=None,
                        columnspan=1, font=("arial", 15), pady=(3, 3)):
        """
        Ajout d'une radiobutton à la fenêtre

        Permet l'ajout facile, car gère tout :
            - Création de la variable de contenu de la radiobutton
            - Création de la radiobutton
            - Sauvegarde de la radiobutton dans un dictionnaire (permettant de garder la trace des éléments)
            - Ajout de la radiobutton dans la fenêtre
        """
        if f'radio{index}' not in self.stringvar.keys():
            self.stringvar[f'radio{index}'] = StringVar()

        if default:
            self.stringvar[f'radio{index}'].set(value)

        if commande is None:
            self.radioBouton[value] = CTkRadioButton(fenetre, text=texte, variable=self.stringvar[f'radio{index}'],
                                                  value=value, font=font)
        else:
            self.radioBouton[value] = CTkRadioButton(fenetre, text=texte, variable=self.stringvar[f'radio{index}'],
                                                  value=value, font=font, command=commande)

        self.radioBouton[value].grid(row=row, column=column, padx=padx, pady=pady, sticky='w', columnspan=columnspan)

    def create_scrollable_frame(self, fenetre, index):
        """
        Création d'une frame scrollable

        La frame ne fonctionne pas avec la méthode de placement grid, donc on utilise la méthode pack
        pour elle et pour les éléments contenus dedans.
        """
        self.frame[index] = scroll.VerticalScrolledFrame(fenetre)
        self.frame[index].pack(side='bottom', fill='both', expand='true')

    def create_pack_frame(self, fenetre, index, bg='#BBBBBB', pady=None, padx=None):
        """
        Création d'une frame contenue dans une frame scrollable

        Une frame correspond aux données d'un compte (une frame par compte).

        Déroulé :
            - Création de la frame
            - Ajout de la frame dans la frame scrollable
            - Création des éléments de la frame :
                - Label du compte
                - Label du login
                - Label du mot de passe
                - Bouton copier login
                - Bouton copier mot de passe
                - Bouton voir mot de passe
                - Bouton modifier compte
                - Bouton supprimer compte
                - Bouton connexion (Si lien de connexion défini)
            - L'intéraction se fait avec les fonctions appellées par les boutons
        """
        self.frame[index] = CTkFrame(fenetre, fg_color=bg, corner_radius=10)
        self.frame[index].pack(fill='both', padx=padx, pady=pady)

        # self.create_label(self.frame[index], f"compte{index}", f"{index[:15]}", 0, 0, bg='white', padx=(25, 15),
        #                   pady=20, width=12, anchor='w', font=("arial", 15, "underline"), rowspan=2, CTk=False)

        self.create_button(self.frame[index], f"compte{index}", f"{index}", 0, 0, rowspan=2, bg="white", abg="#F5F5F5",
                           font=("arial", 20, "underline"), anchor='w', width=120, pady=20, padx=(20, 15),
                           commande=partial(self.create_toplevel, 450, 600, 'Modifier', 'generer', 'modifier',
                                           60, 25, fc=partial(self.build_modifier, compte=index)), couper=True, fg='black')

        mdp_l = decrypt(self.donnees[index], self.mdp_maitre)
        link, login = link_login(mdp_l)
        user, mdp = user_mdp(login)
        user_color = None
        if user == '':
            user = '(non défini)'
            user_color = '#A0A0A0'
        password_color = None
        if mdp == '':
            mdp = False
            password_color = '#A0A0A0'

        self.create_label(self.frame[index], f"user_label{index}", user, 0, 2, bg='white', pady=(10, 0),
                          width=18, sticky='w', padx=(0, 20), anchor='w', user=True, CTk=False, fg=user_color)

        self.create_label(self.frame[index], f"points{index}", "", 1, 2, bg='white', pady=(0, 14),
                          width=18, sticky='w', padx=(0, 20), textvar=True, anchor='w', CTk=False, fg=password_color)
        if not mdp:
            self.voir_mdp(f"points{index}")
            self.stringvar[f"points{index}"].set('(non défini)')

        disabled = False
        if user_color is not None:
            disabled = self.copier_disabled
        self.create_button(self.frame[index], f"copier_user{index}", '', 0, 1, sticky='se', image=self.copier,
                           width=34, height=34, commande=partial(self.copy_user, index), padx=(0, 10), pady=(12, 6), bg="#E5E5E5", abg="#F5F5F5", disabled= disabled)

        disabled = False
        if not mdp:
            disabled = self.copier_disabled
        self.create_button(self.frame[index], f"copier{index}", '', 1, 1, sticky='en', image=self.copier,
                           width=34, height=34, commande=partial(self.copier_pp, f"points{index}"), padx=(0, 10), pady=(0, 12), bg="#E5E5E5", abg="#F5F5F5", disabled=disabled)

        disabled = False
        if not mdp:
            disabled = self.oeil_disabled
        self.create_button(self.frame[index], f"modif{index}", '', 0, 3, sticky='se', image=self.crayon, width=32,
                           height=34, rowspan=1, padx=6, pady=(12, 6),
                           commande=partial(self.create_toplevel, 450, 600, 'Modifier', 'generer', 'modifier',
                                            60, 25, fc=partial(self.build_modifier, compte=index)), bg="#E5E5E5", abg="#F5F5F5")
        self.create_button(self.frame[index], f"supprimer{index}", '', 0, 4, sticky='en', image=self.poubelle,
                           width=32, height=34, rowspan=1, padx=0, pady=(12, 6),
                           commande=partial(self.create_toplevel, 350, 200, '', 'confirmer', 'confirmation_sup', 30, 15,
                                            s='Cette opération\n est définitive.\n\nConfirmer la suppression ?\n',
                                            compte=index), bg="#E5E5E5", abg="#F5F5F5")
        self.create_button(self.frame[index], f"voir{index}", '', 1, 3, sticky='se', image=self.oeil, width=32,
                           height=34, commande=partial(self.voir_mdp, f"points{index}"), rowspan=1, padx=6, pady=(0, 12), bg="#E5E5E5", abg="#F5F5F5", disabled=disabled)
        disabled = False
        if link != '':
            self.create_button(self.frame[index], f"web{index}", '', 1, 4, sticky='en', image=self.web, width=32,
                               height=34, commande=partial(self.ouvrir_fenetre, link, index),
                               rowspan=1, padx=0, pady=(0, 12), bg="#E5E5E5", abg="#F5F5F5")
        else:
            self.create_button(self.frame[index], f"web{index}", '', 1, 4, sticky='en', image=self.web, width=32,
                               height=34, rowspan=1, padx=0, pady=(0, 12), bg="#E5E5E5", abg="#F5F5F5", disabled=self.web_disabled)


    def create_frame(self, fenetre, index, row, column, bg='#BBBBBB', columnspan=1, pady=None, padx=None, sticky=None):
        """
        Création d'une frame

        Déroulé :
            - Création de la frame
            - Ajout de la frame
        """
        self.frame[index] = CTkFrame(fenetre, width=200, height=200, fg_color=bg, corner_radius=10)
        self.frame[index].grid(row=row, column=column, sticky=sticky, columnspan=columnspan, pady=pady, padx=padx)
        self.frame[index].grid_columnconfigure(0, weight=1)

    def create_label(self, fenetre, index, texte, ligne, colonne, columnspan=1, rowspan=1, font=("arial", 15), bg=None,
                     padx=None, pady=None, width=120, sticky=None, textvar=False, anchor=None, user=False, fg=None, CTk=True, corner_radius=None):
        """
        Ajout d'un label à la fenêtre

        Permet l'ajout facile, car gère tout :
            - Création de la variable de contenu du label (si contenu variable)
            - Création du label
            - Sauvegarde du label dans un dictionnaire (permettant de garder la trace des éléments)
            - Ajout du label dans la fenêtre

        Deux types de labels :
            - Labels fixes (en-tête, titre, etc.)
            - Labels variables
                - Mots de passes : peuvent être modifiés et/ou cachés
                - Noms d'utilisateurs : peuvent être modifiés
        """

        if bg is None and CTk:
            bg = "transparent"

        if textvar:
            self.stringvar[index] = StringVar()
            self.stringvar[index].set('●●●●●●●●●●●●●●')
            self.visible[index] = False
            if CTk:
                self.label[index] = CTkLabel(fenetre, textvariable=self.stringvar[index],
                                             font=font, bg_color=bg, width=width, anchor=anchor, text_color=fg, corner_radius=corner_radius)
            else:
                self.label[index] = Label(fenetre, textvariable=self.stringvar[index],
                                          font=font, bg=bg, width=width, anchor=anchor, fg=fg)
        elif user:
            self.stringvar[index] = StringVar()
            self.stringvar[index].set(texte)
            if CTk:
                self.label[index] = CTkLabel(fenetre, textvariable=self.stringvar[index],
                                             font=font, bg_color=bg, width=width, anchor=anchor, text_color=fg, corner_radius=corner_radius)
            else:
                self.label[index] = Label(fenetre, textvariable=self.stringvar[index],
                                          font=font, bg=bg, width=width, anchor=anchor, fg=fg)
        else:
            if CTk:
                self.label[index] = CTkLabel(fenetre, text=texte, font=font, bg_color=bg, width=width, anchor=anchor, text_color=fg, corner_radius=corner_radius)
            else:
                self.label[index] = Label(fenetre, text=texte, font=font, bg=bg, width=width, anchor=anchor, fg=fg)

        self.label[index].grid(row=ligne, column=colonne, columnspan=columnspan,
                               rowspan=rowspan, padx=padx, pady=pady, sticky=sticky)

    def create_slider(self, fenetre, index, ligne, colonne, commande=None, columnspan=1, rowspan=1, padx=None, pady=None, default=None, debut=0, fin=1, width=None):
        """
        Ajout d'un slider à la fenêtre
        """
        self.stringvar[index] = IntVar()
        self.slider[index] = CTkSlider(fenetre, command=commande,
                                       from_=debut,
                                       to=fin,
                                       variable=self.stringvar[index],
                                       width=width)
        if default:
            self.slider[index].set(default)

        self.slider[index].grid(row=ligne, column=colonne, columnspan=columnspan,
                               rowspan=rowspan, padx=padx, pady=pady)

    def create_button(self, fenetre, index, texte, ligne, colonne, columnspan=1, rowspan=1,
                      commande=None, bg="white", fg="black", abg=None, afg=None, font=None,
                      sticky='ew', anchor="center", height=28, width=10, image=None, pady=None, padx=None, disabled=False, couper=False):
        """
        Ajout d'un bouton à la fenêtre

        Permet l'ajout facile, car gère tout :
            - Création du bouton
            - Sauvegarde du bouton dans un dictionnaire (permettant de garder la trace des éléments)
            - Ajout du bouton dans la fenêtre
        """
        if disabled:
            image = disabled
            bg = "#F0F0F0"

        if couper:
            while largeur_texte(texte, 20) > 3.8:
                texte = texte[:-1]

        self.button[index] = CTkButton(fenetre, text=texte, command=commande, fg_color=bg, text_color=fg, hover_color=abg,
                                    width=width, height=height, image=image, font=font, border_spacing=0, anchor=anchor)
        self.button[index].grid(row=ligne, column=colonne, columnspan=columnspan,
                                rowspan=rowspan, sticky=sticky, pady=pady, padx=padx)
        if disabled:
            self.button[index].configure(state="disabled")


    def add_input(self, fenetre, index, ligne, colonne, pady=None, padx=None, width=10,
                  focus=False, show=True, sticky=None, columnspan=1, default=None, placeholder='', exists=False):
        """
        Ajout d'un champ de saisie à la fenêtre

        Permet l'ajout facile, car gère tout :
            - Création de la variable de contenu du champ de saisie
            - Création du champ de saisie
            - Sauvegarde du champ de saisie dans un dictionnaire (permettant de garder la trace des éléments)
            - Ajout du champ de saisie dans la fenêtre

        Certains champs de saisies sont cachés ou non par défaut
        """

        recherche = False
        if index == "recherche":
            recherche = True

        if not exists:
            self.stringvar[index] = StringVar()
        if default is not None:
            self.stringvar[index].set(default)

        if placeholder == '':
            self.input[index] = CTkEntry(fenetre, textvariable=self.stringvar[index], width=width)
        else:
            if show:
                self.input[index] = CTkEntryWithPlaceholder(fenetre, textvariable=self.stringvar[index], width=width,
                                                            placeholder=placeholder, recherche=recherche)
            else:
                self.input[index] = CTkEntryWithPlaceholder(fenetre, textvariable=self.stringvar[index], width=width,
                                                            placeholder=placeholder, visible=self.visible, index=index)

        if focus:
            self.input[index].focus_force()
        self.input[index].grid(row=ligne, column=colonne, pady=pady, sticky=sticky, columnspan=columnspan, padx=padx)
        if not show:
            self.visible[index] = False

            if placeholder == '' or (default is not None and default != ''):
                self.input[index].configure(show="●")

    def voir_mdp(self, index):
        """
        Affiche ou cache un mot de passe montré dans un label

        Le fait que le mot de passe soit actuellement visible ou non est géré dans un dictionnaire (self.visible)
        Si le mot de passe était visible, il est caché, sinon il est affiché.

        Le nombre de points est fixe et ne coorespond pas à la
        vraie taille pour des raisons de sécurité et d'esthétisme.
        """
        if self.visible[index]:
            self.visible[index] = False
            self.stringvar[index].set('●●●●●●●●●●●●●●')
        else:
            self.visible[index] = True
            mdp_l = decrypt(self.donnees[index[6:]], self.mdp_maitre)
            login = link_login(mdp_l)[1]
            password = user_mdp(login)[1]
            self.stringvar[index].set(password)

    def voir_gen(self):
        """
        Fonctionne comme voir_mdp, mais pour le générateur de mot de passe
        La fonction est séparée, car il n'y a pas de mot de passe à récupérer dans le fichier
        """
        if self.visible['generer_mdp']:
            self.visible['generer_mdp'] = False
            self.stringvar['generer_mdp'].set('●●●●●●●●●●●●●●')
        else:
            self.visible['generer_mdp'] = True
            self.stringvar['generer_mdp'].set(self.mdp_gen)

    def voir(self, index="generer_mdp"):
        """
        Fonctionne comme voir_mdp, mais dans le cas de champs de saisie et non de labels
        """
        if self.visible[index]:
            self.visible[index] = False
            if not (type(self.input[index]) == CTkEntryWithPlaceholder and self.input[index].get_content() == ""):
                self.input[index].configure(show="●")
        else:
            self.visible[index] = True
            self.input[index].configure(show="")

    def copier_pp(self, index):
        """
        Copie un mot de passe dans le presse-papier
        """
        mdp_l = decrypt(self.donnees[index[6:]], self.mdp_maitre)
        login = link_login(mdp_l)[1]
        password = user_mdp(login)[1]
        pyperclip.copy(password)

    def copy_user(self, index):
        """
        Copie un login dans le presse-papier

        On copie le login depuis le dictionnaire des données et plus depuis le label :
        pyperclip.copy(self.stringvar[f"user_label{index}"].get()) fonctionnait mais copiait le texte
        affiché par défaut lorsque le nom d'utilisateur n'était pas défini.
        """
        mdp_l = decrypt(self.donnees[index], self.mdp_maitre)
        login = link_login(mdp_l)[1]
        login = user_mdp(login)[0]
        pyperclip.copy(login)

    def copier_gen(self):
        """
        Copie le mot de passe généré dans le presse-papier
        """
        pyperclip.copy(self.mdp_gen)

    def copier_gen_modif(self):
        """
        Copie le mot de passe généré dans "modifier" compte dans le presse-papier
        """
        pyperclip.copy(self.input['generer_mdp'].get())

    @staticmethod
    def effacer(fenetre, *args):
        """
        Efface le contenu d'un champ de saisie entre le début et le curseur

        Cette fonction peut être appelée en raccourci clavier, type d'appel pouvant
        créer un bug au niveau du nombre d'arguments, *args permet de gérer ce problème.
        """
        fenetre.focus_get().delete(0, 'insert')

    @staticmethod
    def tout_selectionner(fenetre, event=None):
        """
        Sert à l'implémentation du Contrôle-a (selectionne tout le texte d'un champ)
        """
        fenetre.focus_get().select_range(0, 'end')
        fenetre.focus_get().icursor('end')

    def effacer_update(self, *args):
        """
        Efface le contenu du champ de saisie du menu et met à jour les comptes affichés

        Cette fonction peut être appelée en raccourci clavier, type d'appel pouvant
        créer un bug au niveau du nombre d'arguments, *args permet de gérer ce problème.
        """
        self.effacer(self.menu)
        self.update()

    @staticmethod
    def effacer_fin(fenetre, *args):
        """
        Efface le contenu d'un champ de saisie entre le curseur et la fin

        Cette fonction peut être appelée en raccourci clavier, type d'appel pouvant
        créer un bug au niveau du nombre d'arguments, *args permet de gérer ce problème.
        """
        fenetre.focus_get().delete('insert', 'end')

    def effacer_fin_update(self, *args):
        """
        Efface le contenu du champ de saisie du menu et met à jour les comptes affichés

        Cette fonction peut être appelée en raccourci clavier, type d'appel pouvant
        créer un bug au niveau du nombre d'arguments, *args permet de gérer ce problème.
        """
        self.effacer_fin(self.menu)
        self.update()

    def valider(self, index, fenetre, *args):
        """
        Vérifie le mot de passe saisi dans le champ de saisie
        """
        if self.mdp_user != self.stringvar[index].get():
            self.mdp_user = self.stringvar[index].get()
            self.stringvar['erreur'].set('')
            fenetre.update()
            time.sleep(0.1)

            if self.input[index].get_content() == "":
                self.stringvar['erreur'].set('Mot de passe incorrect')
                return

            self.mdp_maitre = get_master_password(self.mdp_user)
            if self.mdp_maitre:
                fenetre.destroy()
            else:
                self.stringvar['erreur'].set('Mot de passe incorrect')

    def update(self, delete=False, account='', remonter=True, delete_all=False, reset=False, *args):
        """
        Met à jour les comptes affichés dans le menu :
            - supprime les frames des comptes supprimés
            - cache les frames des comptes non recherchés

        Déroulé :
            - On cache toutes les frames puis on affiche toutes celles commençant par le contenu du champ de recherche

            - Si appel avec demande de suppresion d'un compte, on supprime la frame correspondante
            - Si appel avec demande de suppression de tous les comptes (e.g. import de données),
              on supprime toutes les frames
            - Si appel avec 'reset', on efface le champ de recherche et on affiche tous les comptes
            - Si appel avec 'remonter', on remonte la scrollbar au début

        """

        self.input["recherche"].update_placeholder()

        if reset:
            self.input['recherche'].delete(0, END)

        try:
            if delete is True and account != '' and account in self.donnees.keys():
                self.frame[account].destroy()
        except:
            pass

        if delete_all:
            for i in self.donnees.keys():
                try:
                    self.frame[i].destroy()
                except:
                    pass
        else:
            for k in self.donnees.keys():
                try:
                    self.frame[k].pack_forget()
                except:
                    pass

        compte = self.input['recherche'].get_content().lower()
        keys = sorted(list(self.donnees.keys()), key=str.lower)
        for k in keys:
            if k[:len(compte)].lower() == compte:
                try:
                    self.frame[k].pack(fill='both', padx=3, pady=3)
                except:
                    self.create_pack_frame(self.frame['liste'].interior, k, bg='white', pady=3, padx=3)

        # remonter en haut de la scrollable frame
        if remonter:
            self.frame['liste'].reset()


    def create_toplevel(self, w, h, title, type_fenetre, fonction, padx, pady, event=None, compte=None,
                        s='Cette opération\n est définitive.\n\nConfirmer ?\n', fc=None):
        """
        Création d'une sur-fenêtre.

        Déroulé :
            - Supprime les autres sur-fenêtres si elles existent
            - La fenêtre est une toplevel, elle est "enfant" de la fenêtre principale
            - Création de la fenêtre
        """
        try:
            self.confirmer_f.destroy()
            if type_fenetre == 'generer':
                self.generer_f.destroy()
        except:
            try:
                if type_fenetre == 'generer':
                    self.generer_f.destroy()
            except:
                pass
        finally:
            if platform.system() == "Windows":
                h += int(h * 0.05)

            if type_fenetre != 'generer' and fonction == 'confirmation':
                if not self.verif_confirmation(compte):
                    return

            if type_fenetre != 'generer' and fonction != 'confirmation_sup':
                sur_fenetre = CTkToplevel(self.generer_f, width=w, height=h, fg_color=("#F1F1F1", "#222325"))
            else:
                sur_fenetre = CTkToplevel(self.menu, width=w, height=h, fg_color=("#F1F1F1", "#222325"))

            sur_fenetre.title(title)

            central_monitor = len(get_monitors()) // 2
            largeur_ecran = get_monitors()[central_monitor].width
            hauteur_ecran = get_monitors()[central_monitor].height
            cumulated_width = sum([get_monitors()[i].width for i in range(central_monitor)])
            pos_x = largeur_ecran // 2 - w // 2 + cumulated_width
            pos_y = hauteur_ecran // 2 - h // 2
            geometry = f"{w}x{h}+{pos_x}+{pos_y}"
            sur_fenetre.geometry(geometry)
            sur_fenetre.resizable(height=False, width=False)
            sur_fenetre.configure(padx=60, pady=60)

            if type_fenetre == 'generer':
                sur_fenetre.bind('<Control-BackSpace>', partial(self.effacer, sur_fenetre))
                sur_fenetre.bind('<Control-Delete>', partial(self.effacer_fin, sur_fenetre))
                sur_fenetre.bind('<Control-a>', partial(self.tout_selectionner, sur_fenetre))

                self.generer_f = sur_fenetre
                try:
                    if fc is not None:
                        fc()
                except TypeError:
                    pass

            else:  # type_fenetre == 'confirmer'
                sur_fenetre.grid_columnconfigure(0, weight=1)
                sur_fenetre.grid_columnconfigure(1, weight=1)
                self.confirmer_f = sur_fenetre
                self.create_label(self.confirmer_f, 'choix', s, 0, 0, columnspan=2, anchor='center', pady=(20, 0), font=("arial", 20))

                if fonction == 'confirmation':
                    self.create_button(self.confirmer_f, 'oui', 'Modifier', 1, 0,
                                       commande=partial(self.confirmation, compte), bg="#DEDEDE", abg="#ECECEC", padx=(40, 2))
                    self.create_button(self.confirmer_f, 'non', 'Annuler', 1, 1, commande=self.generer_f.destroy, bg="#DEDEDE", abg="#ECECEC", padx=(2, 40))
                    self.confirmer_f.bind('<Return>', partial(self.confirmation, compte))
                else:  # fonction == 'confirmation_sup'
                    self.create_button(self.confirmer_f, 'oui', 'Supprimer', 1, 0,
                                       commande=partial(self.confirmation_sup, compte), bg="#DEDEDE", abg="#ECECEC", padx=(40, 2))
                    self.create_button(self.confirmer_f, 'non', 'Annuler', 1, 1, commande=self.confirmer_f.destroy, bg="#DEDEDE", abg="#ECECEC", padx=(2, 40))
                    self.confirmer_f.bind('<Return>', partial(self.confirmation_sup, compte))

    def get_links(self):
        """
        Récupère les liens et domaines de connexions des comptes pour la connexion automatique
        """
        self.temp = dict()
        self.login_links = []
        self.login_urls = dict()

        for index in self.donnees.keys():
            mdp_l = decrypt(self.donnees[index], self.mdp_maitre)
            url = link_login(mdp_l)[0]
            if url != '':
                doubleauth, wait, prio, url = doubleauth_wait_prio_link(url)
                link = domaine(url)

                if link in self.temp.keys():
                    if prio == '1' and self.temp[link][2] == '0':
                        self.temp[link] = [index, url, prio]
                else:
                    self.temp[link] = [index, url, prio]

        self.login_links = [self.temp[link][1] for link in self.temp.keys()]

        for index in self.temp.keys():
            self.login_urls[index] = self.temp[index][0]

        if self.server is not None:
            self.server.update_domaines(self.login_urls, self.login_links)

    def create_server(self):
        if self.server is None:
            self.server = Server(self.login_urls, self.login_links, self.mdp_maitre, self.donnees)
        # print("Server created")

    def delete_server(self):
        if self.server is not None and not self.server.is_stopped():
            self.server.stop_server()
            self.server = None
        # print("Server deleted")

    def update_server_state(self):
        if not self.server is None:
            if self.stringvar["checkauto"].get() == '1' and self.server.is_stopped() and self.server_thread is None:
                # print("Server thread started")
                self.server_thread = threading.Thread(target=self.server.start_server)
                self.server_thread.start()
            elif self.stringvar["checkauto"].get() == '0' and not self.server.is_stopped() and not self.server_thread is None:
                self.server.stop_server()
                sleep(5)
                self.server_thread.join()
                # print("Server thread stopped")
                self.server_thread = None

            # print(f"server : {self.server is not None}")
            # print(f"checkauto : {self.stringvar['checkauto'].get()}, server stopped : {self.server.is_stopped()}, server thread : {self.server_thread is not None}")

    def autoconnect(self):
        """
        Connexion automatique :
        - Bascule sur le nouvel onglet que vient de créer l'utilisateur s'il le fait
        - Regarde s'il est sur une page de connexion et si oui, essaye de se connecter
        """
        self.create_server()
        self.stop = False

        ok = False
        while not ok:
            try:
                if self.stringvar["checkauto"].get() == '1' or self.stringvar["checkauto"].get() == '0':
                    ok = True
            except:
                pass
        

        self.update_server_state()

        while threading.main_thread().is_alive() and not self.stop:
            sleep(5)
            self.update_server_state()

        self.delete_server()

        if self.server_thread is not None:
            sleep(5)
            self.server_thread.join()

        # print("Autoconnect stopped")

        self.server_thread = None

    def ouvrir_fenetre(self, link, compte):
        """
        Ouvre une fenêtre pour se connecter à un compte
        Si la fênetre est déjà ouverte, bascule sur celle-ci
        """


        doubleauth, wait, prio, link = doubleauth_wait_prio_link(link)
        webbrowser.open(link)

    def generer_mdp(self, *args):
        """
        Fonction qui génère un mot de passe aléatoire dans "générer"
        """
        chaine = (self.stringvar['checkchiffres'].get() +
                  self.stringvar['checklettresmin'].get() +
                  self.stringvar['checklettresmaj'].get() +
                  self.stringvar['checkponctuation'].get() +
                  self.stringvar['checkcara_spe'].get())
        if chaine == '':
            self.mdp_gen = 'Aucune case sélectionnée'
            self.visible['generer_mdp'] = True
            self.stringvar['generer_mdp'].set(self.mdp_gen)
        else:
            try:
                taille = int(self.stringvar['taille'].get())
                if taille < 10:
                    taille = 10
                elif taille > 100:
                    taille = 100
            except:
                taille = 15

            if self.stringvar['checkdouble'].get() == 'on':
                confus = ['I', 'l', '|', '0', 'O']
                for lettre in confus:
                    chaine = chaine.replace(lettre, "")

            self.mdp_gen = ''.join([random.choice(chaine) for _ in range(taille)])
            if self.visible['generer_mdp']:
                self.stringvar['generer_mdp'].set(self.mdp_gen)

    def generer_mdp_modif(self, event=None):
        """
        Fonction qui génère un mot de passe aléatoire dans "modifier"
        """
        chaine = (self.stringvar['checkchiffres'].get() +
                  self.stringvar['checklettresmin'].get() +
                  self.stringvar['checklettresmaj'].get() +
                  self.stringvar['checkponctuation'].get() +
                  self.stringvar['checkcara_spe'].get())
        if chaine == '':
            self.mdp_gen = 'Aucune case sélectionnée'
            self.stringvar['generer_mdp'].set(self.mdp_gen)
            self.input['generer_mdp'].convert_placeholder()
            self.input['generer_mdp'].temp_placeholder = 'Aucune case sélectionnée'
        else:
            try:
                taille = int(self.stringvar['taille'].get())
                if taille < 10:
                    taille = 10
                elif taille > 100:
                    taille = 100
            except:
                taille = 15

            if self.stringvar['checkdouble'].get() == 'on':
                confus = ['I', 'l', '|', '0', 'O']
                for lettre in confus:
                    chaine = chaine.replace(lettre, "")

            self.mdp_gen = ''.join([random.choice(chaine) for _ in range(taille)])
            self.stringvar['generer_mdp'].set(self.mdp_gen)
            self.input['generer_mdp'].convert_real_text()

            if not self.visible['generer_mdp']:
                self.input['generer_mdp'].configure(show="●")

    def modifier_preferences(self, *args):
        """
        Fonction qui modifie les préférences de génération de mot de passe
        """
        chiffres = self.stringvar['checkchiffres'].get()
        mini = self.stringvar['checklettresmin'].get()
        maj = self.stringvar['checklettresmaj'].get()
        ponct = self.stringvar['checkponctuation'].get()
        cara = self.stringvar['checkcara_spe'].get()
        no_similar = self.stringvar['checkdouble'].get()
        autoconnexion = self.stringvar['checkautoconnexion'].get()
        profil = self.input["profil"].get_content()

        self.preferences['chiffres'] = chiffres
        self.preferences['lettresmin'] = mini
        self.preferences['lettresmaj'] = maj
        self.preferences['ponctuation'] = ponct
        self.preferences['cara_spe'] = cara
        self.preferences['no_similar'] = no_similar

        self.preferences['autoconnexion'] = autoconnexion
        self.stringvar['checkauto'].set(autoconnexion)

        elems = [chiffres, mini, maj, ponct, cara]
        for i in range(len(elems)):
            if elems[i] != '':
                elems[i] = '1'
            else:
                elems[i] = '0'

        if no_similar == 'on':
            no_similar = '1'
        else:
            no_similar = '0'

        try:
            taille = int(self.stringvar['taille'].get())
            if taille < 10:
                taille = 10
            elif taille > 100:
                taille = 100
        except:
            taille = 15
        taille = str(taille)

        self.preferences['taille'] = taille

        with open('.data/preferences.txt', 'w') as f:
            f.write(elems[0] + '\n' + elems[1] + '\n' + elems[2] + '\n' + elems[3] + '\n' + elems[4] + '\n' +
                    no_similar + '\n' +
                    taille + '\n' +
                    autoconnexion)

        self.generer_f.destroy()

    def exporter(self):
        """
        Fonction qui exporte les données dans un fichier json
        """

        file_selected = filedialog.asksaveasfile(mode='w', defaultextension=".json", initialdir=os.path.expanduser("~"),
                                                 filetypes=[("fichiers json", "*.json")], title="Enregistrer",
                                                 initialfile="export")
        if file_selected is not None:
            export = dict()
            for compte in self.donnees.keys():
                chaine_clair = decrypt(self.donnees[compte], self.mdp_maitre)
                link, login = link_login(chaine_clair)
                user, password = user_mdp(login)

                keys = ['user', 'password']
                values = [user, password]
                if link != '':
                    doubleauth, wait, prio, link = doubleauth_wait_prio_link(link)
                    keys = ['user', 'password', 'link', 'doubleauth', 'wait', 'prio']
                    values = [user, password, link, doubleauth, wait, prio]

                export[compte] = dict(zip(keys, values))

            json.dump(export, file_selected, indent=4)

    def importer(self):
        """
        Fonction qui importe les données depuis un fichier json
        En cas de conflit de données, l'utilisateur est invité à choisir entre :
            - écraser les données existantes
            - ignorer les données importées
            - renommer les données importées
            - annuler l'importation
        """
        file_selected = filedialog.askopenfile(mode='r', initialdir=os.path.expanduser("~"), title="Choisir un fichier",
                                               filetypes=[("fichiers json", "*.json")])
        if file_selected is None:
            return
        if file_selected.name[-5:] != ".json":
            return
        try:
            data = json.load(file_selected)
        except:
            return
        if not donnees_valides(data):
            return
        if len(data.keys()) == 0:
            return

        self.copie_donnees = copy(self.donnees)
        idem = '0'
        choix = 'ignorer'
        new_compte = ''

        if 'radiochoix' in self.stringvar.keys():
            self.stringvar['radiochoix'].set('ignorer')

        for compte in data.keys():
            new_compte = compte

            if compte in self.copie_donnees.keys():
                if idem == '0':
                    self.create_toplevel(500, 330, '', 'generer', 'conflit_donnees', 80, 15, compte=new_compte,
                                         fc=partial(self.build_conflit_donnees, new_compte))
                    self.menu.wait_window(self.generer_f)

                    if not self.appui_valider:
                        return

                    choix = self.stringvar['radiochoix'].get()
                    if choix == 'renommer':
                        new_compte = self.stringvar['nouveau_nom'].get()
                    else:
                        idem = self.stringvar['checkidem'].get()

                if choix == 'ignorer':
                    continue
                elif choix == 'ecraser':
                    self.copie_donnees.pop(new_compte)

            # Ici, soit il n'y a pas de conflit, soit on a choisi de renommer le compte,
            # soit on a choisi d'écraser le compte.
            username = data[compte]['user']
            mdp = data[compte]['password']
            link = ''

            if 'link' in data[compte].keys():
                link = data[compte]['link']
                doubleauth = data[compte]['doubleauth']
                wait = data[compte]['wait']
                prio = data[compte]['prio']
                link = doubleauth + wait + prio + link

            # print(f"\n\n\ncompte = {new_compte}\nmdp = {mdp}\nusername = {username}\nlink = {link}")
            mdp_e = f"{mdp}{username}{len(username):02}{link}{len(link):03}"
            mdp_e_chiffre = encrypt(mdp_e, self.mdp_maitre)
            self.copie_donnees[new_compte] = mdp_e_chiffre

        self.donnees = self.copie_donnees
        if self.server is not None:
            self.server.update_donnees(self.donnees)
        self.donnees_liste, liste_chiffree = donnees_dico_liste(self.donnees, self.mdp_maitre)

        with open(self.f, 'w') as f:
            f.write(''.join(liste_chiffree))
        self.update(remonter=False, delete_all=True, reset=True)
        threading.Thread(target=self.get_links).start()

    def build_conflit_donnees(self, compte):
        """
        Fonction qui construit la fenêtre de conflit de données en cas d'importation

        La fenêtre propose à l'utilisateur de choisir entre :
        - écraser les données existantes
        - ignorer les données importées
        - renommer les données importées
        - annuler l'importation
        """

        self.generer_f.grid_columnconfigure(0, weight=1)
        self.generer_f.grid_columnconfigure(1, weight=1)

        self.appui_valider = False
        s = f"Un compte \"{compte}\" existe déjà.\nQue voulez-vous faire ?"
        self.create_label(self.generer_f, 'conflit', s, 0, 0, anchor='center', pady=(20, 10), columnspan=2, font=('arial', 25))

        if 'radiochoix' not in self.stringvar.keys():
            self.add_radiobutton(self.generer_f, 'choix', 'Ignorer', 1, 0, 'ignorer', default=True,
                                 commande=partial(self.hide_entry), columnspan=2, padx=(50, 0), font=('arial', 20), pady=(10, 10))
        else:
            self.add_radiobutton(self.generer_f, 'choix', 'Ignorer', 1, 0, 'ignorer',
                                 commande=partial(self.hide_entry), columnspan=2, padx=(50, 0), font=('arial', 20), pady=(0, 10))
        self.add_radiobutton(self.generer_f, 'choix', 'Écraser', 2, 0, 'ecraser',
                             commande=partial(self.hide_entry), columnspan=2, padx=(50, 0), font=('arial', 20), pady=(0, 10))
        self.add_radiobutton(self.generer_f, 'choix', 'Renommer', 3, 0, 'renommer',
                             commande=partial(self.show_entry, compte), columnspan=2, padx=(50, 0), font=('arial', 20), pady=(0, 10))

        self.create_button(self.generer_f, 'conflit', 'Valider', 5, 0, padx=(50, 10), pady=(10, 0),
                           commande=partial(self.verif_conflit, self.generer_f), bg="#DEDEDE", abg="#ECECEC", font=('arial', 20))
        self.create_button(self.generer_f, 'annnuler_conflit', 'Annuler', 5, 1, pady=(10, 0),
                           commande=partial(self.generer_f.destroy), bg="#DEDEDE", abg="#ECECEC", font=('arial', 20), padx=(10, 50))

        self.generer_f.bind('<Return>', partial(self.verif_conflit, self.generer_f))

        if self.stringvar['radiochoix'].get() == 'renommer':
            self.show_entry(compte)
        else:
            self.hide_entry()

    def verif_conflit(self, fenetre, *args):
        """
        Fonction qui vérifie les données entrées dans la fenêtre de conflit de données
        """
        if self.stringvar['radiochoix'].get() == 'renommer':
            if (self.stringvar['nouveau_nom'].get() in self.copie_donnees.keys() or
                    self.input['nouveau_nom'].get_content()== ""):

                if self.input['nouveau_nom'].get_content()== "":
                    s = "Veuillez entrer un nom"
                else:
                    s = "Ce nom est déjà utilisé"

                try:
                    if 'conflit_error' in self.label.keys():
                        self.label['conflit_error'].grid_forget()
                        fenetre.update()
                        time.sleep(0.1)
                        self.label['conflit_error'].grid(row=6, column=0, pady=(10, 0), columnspan=2)
                    else:
                        self.create_label(fenetre, 'conflit_error', s, 6, 0, anchor='center',
                                          fg='red', user=True, pady=(10, 0), columnspan=2, font=('arial', 20))
                except:
                    self.create_label(fenetre, 'conflit_error', s, 6, 0, anchor='center',
                                      fg='red', user=True, pady=(10, 0), columnspan=2, font=('arial', 20))

                finally:
                    self.stringvar['conflit_error'].set(s)

            else:
                self.appui_valider = True
                self.generer_f.destroy()
        else:
            self.appui_valider = True
            self.generer_f.destroy()

    def hide_entry(self):
        """
        Fonction qui cache/affiche les entrées de la fenêtre de conflit de données en fonction du choix de l'utilisateur
        """
        try:
            if 'nouveau_nom' in self.input.keys():
                self.input['nouveau_nom'].grid_remove()
        except:
            pass

        try:
            if 'conflit_error' in self.label.keys():
                self.label['conflit_error'].grid_forget()
        except:
            pass

        try:
            if 'idem' in self.checkBouton.keys():
                self.checkBouton['idem'].grid(row=4, column=0, pady=(5, 10), columnspan=2)
            else:
                self.add_checkbutton(self.generer_f, 'idem', 'Faire pour tous',
                                     4, 0, '1', '0', '0', pady=(5, 10), columnspan=2, font=('arial', 20), padx=(50, 0))
        except:
            try:
                self.add_checkbutton(self.generer_f, 'idem', 'Faire pour tous',
                                     4, 0, '1', '0', '0', pady=(5, 10), columnspan=2, font=('arial', 20), padx=(50, 0))
            except:
                pass

    def show_entry(self, compte):
        """
        Fonction qui cache/affiche les entrées de la fenêtre de conflit de données en fonction du choix de l'utilisateur
        """
        i = 1
        while f"{compte} ({i})" in self.donnees.keys():
            i += 1

        try:
            if 'idem' in self.checkBouton.keys():
                self.checkBouton['idem'].grid_remove()
        except:
            pass

        try:
            if 'nouveau_nom' in self.input.keys():
                self.input['nouveau_nom'].grid(row=4, column=0, sticky='news', pady=(10, 10), columnspan=2)
            else:
                self.add_input(self.generer_f, 'nouveau_nom', 4, 0, sticky='news', focus=True, pady=(10, 10), padx=50,
                               placeholder='Nouveau nom', columnspan=2, default=f"{compte} ({i})")

                self.input['nouveau_nom']._entry.icursor("end")
        except:
            try:
                self.add_input(self.generer_f, 'nouveau_nom', 4, 0, sticky='news', focus=True, pady=(15, 15), padx=50,
                               placeholder='Nouveau nom', columnspan=2, default=f"{compte} ({i})")
                self.input['nouveau_nom']._entry.icursor("end")
            except:
                pass

    def creer_mdp(self, *args):
        """
        Fonction qui récupère les données après validation de création,
        vérifie la validité de ces données et les enregistre
        """
        mdp = self.input['generer_mdp'].get_content()
        username = self.stringvar['username'].get()
        link = self.stringvar['link'].get()
        wait = self.stringvar['checklong'].get()
        prio = self.stringvar['checkprio'].get()
        doubleauth = self.stringvar['checkdoubleauth'].get()


        if lien_valide(link):
            link = doubleauth + wait + prio + link
        else:
            link = ''

        compte = self.stringvar['nom_compte'].get().strip()

        compte = self.input["nom_compte"].get_content()
        username = self.input["username"].get_content()

        if compte == '':
            self.stringvar['nom_compte'].set('Veuillez saisir un compte')
            self.input['nom_compte'].temp_placeholder = "Veuillez saisir un compte"
        elif len(username) > 99:
            self.stringvar['username'].set('Nom trop long')
            self.input['username'].convert_placeholder()
            self.input['username'].temp_placeholder = "Nom trop long"
        elif len(link) > 999:
            self.stringvar['link'].set('Lien trop long')
            self.input['link'].convert_placeholder()
            self.input['link'].temp_placeholder = "Lien trop long"
        else:
            mdp_e = f"{mdp}{username}{len(username):02}{link}{len(link):03}"
            mdp_e_chiffre = encrypt(mdp_e, self.mdp_maitre)
            compte_e_chiffre = encrypt(compte, self.mdp_maitre)
            if compte not in self.donnees.keys():  # ecriture directe à la fin du fichier
                with open(self.f, "a") as fichier:
                    fichier.write(f"{compte_e_chiffre}\n")
                    fichier.write(f"{mdp_e_chiffre}\n")
                    self.donnees[compte] = mdp_e_chiffre
                    if self.server is not None:
                        self.server.update_donnees(self.donnees)
                    self.donnees_liste.append(f"{compte}\n")
                    self.donnees_liste.append(f'{mdp_e_chiffre}\n')
                    self.generer_f.destroy()
                    self.update(remonter=False)
                    threading.Thread(target=self.get_links).start()
            else:
                self.create_toplevel(350, 200, '', 'confirmer', 'confirmation', 30, 15, compte=compte,
                                     s=f"Un compte {compte}\nest déjà enregistré.\nVoulez-vous le modifier ?\n")

    def confirmation(self, compte, *args):
        """
        Fonction qui récupère les données après validation de modification,
        vérifie la validité de ces données et les enregistre
        """
        mdp = self.input['generer_mdp'].get_content()
        link = self.stringvar['link'].get()
        wait = self.stringvar['checklong'].get()
        prio = self.stringvar['checkprio'].get()
        doubleauth = self.stringvar['checkdoubleauth'].get()

        if lien_valide(link):
            link = doubleauth + wait + prio + link
        else:
            link = ''

        username = self.input["username"].get_content()
        new_compte = self.input["nom_compte"].get_content().strip()

        mdp_e = f"{mdp}{username}{len(username):02}{link}{len(link):03}"
        mdp_e_chiffre = encrypt(mdp_e, self.mdp_maitre)

        if new_compte != compte:
            # on supprime l'ancien compte
            self.confirmation_sup(compte, new_links=False)

            # on ajoute le nouveau compte
            mdp_e = f"{mdp}{username}{len(username):02}{link}{len(link):03}"
            mdp_e_chiffre = encrypt(mdp_e, self.mdp_maitre)
            compte_e_chiffre = encrypt(new_compte, self.mdp_maitre)
            with open(self.f, "a") as fichier:
                fichier.write(f"{compte_e_chiffre}\n")
                fichier.write(f"{mdp_e_chiffre}\n")
                self.donnees[new_compte] = mdp_e_chiffre
                if self.server is not None:
                    self.server.update_donnees(self.donnees)
                self.donnees_liste.append(f"{new_compte}\n")
                self.donnees_liste.append(f'{mdp_e_chiffre}\n')
                self.generer_f.destroy()
                self.update(delete=True, account=compte, remonter=False)
                threading.Thread(target=self.get_links).start()
        else:
            with open(self.f, "r") as fichier:
                donnees_s = fichier.readlines()
                index = index_liste(self.donnees_liste, f"{compte}\n")
                donnees_s = donnees_s[:index + 1] + [f"{mdp_e_chiffre}\n"] + donnees_s[index + 2:]
                self.donnees_liste = self.donnees_liste[:index + 1] + [f"{mdp_e_chiffre}\n"] + self.donnees_liste[index + 2:]
                donnees_s = ''.join(donnees_s)
            with open(self.f, "w") as fichier:
                fichier.write(donnees_s)
            self.donnees[compte] = mdp_e_chiffre
            if self.server is not None:
                self.server.update_donnees(self.donnees)
            self.generer_f.destroy()
            if self.visible[f"points{compte}"]:
                mdp_l = decrypt(self.donnees[compte], self.mdp_maitre)
                login = link_login(mdp_l)[1]
                password = user_mdp(login)[1]
                self.stringvar[f"points{compte}"].set(password)
            if username == '':
                username = '(non défini)'
            self.stringvar[f"user_label{compte}"].set(username)
            self.update(delete=True, account=compte, remonter=False)
            threading.Thread(target=self.get_links).start()

    def verif_confirmation(self, compte, *args):
        """
        Fonction qui vérifie la validité des données après validation de modification
        """
        link = self.stringvar['link'].get()
        wait = self.stringvar['checklong'].get()
        prio = self.stringvar['checkprio'].get()
        doubleauth = self.stringvar['checkdoubleauth'].get()

        if lien_valide(link):
            link = doubleauth + wait + prio + link
        else:
            link = ''

        username = self.input["username"].get_content()
        new_compte = self.input["nom_compte"].get_content().strip()

        if new_compte == '':
            self.stringvar['nom_compte'].set('Veuillez saisir un compte')
            self.input['nom_compte'].temp_placeholder = "Veuillez saisir un compte"
            return False
        elif new_compte in self.donnees.keys() and new_compte != compte:
            self.stringvar['nom_compte'].set('Ce compte existe déjà')
            self.input['nom_compte'].convert_placeholder()
            self.input['nom_compte'].temp_placeholder = "Ce compte existe déjà"
            return False
        elif len(username) > 99:
            self.stringvar['username'].set('Nom trop long')
            self.input['username'].convert_placeholder()
            self.input['username'].temp_placeholder = "Nom trop long"
            return False
        elif len(link) > 999:
            self.stringvar['link'].set('Lien trop long')
            self.input['link'].convert_placeholder()
            self.input['link'].temp_placeholder = "Lien trop long"
            return False
        else:
            return True

    def confirmation_sup(self, compte, new_links=True, *args):
        """
        Fonction qui supprime les données après validation de suppression
        """
        with open(self.f, "r") as fichier:
            donnees_s = fichier.readlines()
            index = index_liste(self.donnees_liste, f"{compte}\n")
            donnees_s = donnees_s[:index] + donnees_s[index + 2:]
            self.donnees_liste = self.donnees_liste[:index] + self.donnees_liste[index + 2:]
            donnees_s = ''.join(donnees_s)
        with open(self.f, "w") as fichier:
            fichier.write(donnees_s)
        self.donnees.pop(compte)
        if self.server is not None:
            self.server.update_donnees(self.donnees)
        self.frame[compte].destroy()
        self.confirmer_f.destroy()
        if new_links:
            self.update(remonter=False)
            threading.Thread(target=self.get_links).start()

    def build_modifier_mdp_user(self):
        """
        Construction de la fenêtre de modification du mdp utilisateur

        Déroulé :
            - Création des différents éléments :
                - 3 Labels, Ancien, nouveau et confirmation
                - 3 Inputs, Ancien, nouveau et confirmation
                - 3 Boutons voir
                - 1 Bouton de validation
                - 1 Bouton d'annulation
            - L'interaction se fait avec les fonctions appelées par les boutons
        """
        self.generer_f.grid_columnconfigure(0, weight=1)
        self.create_label(self.generer_f, 'ancien_mdp', 'Ancien mot de passe :', 0, 0, sticky='ew', anchor='w', padx=(50, 0), font=("arial", 20), pady=(25, 0))
        self.add_input(self.generer_f, 'ancien_mdp', 1, 0, sticky='news', focus=True, show=False, placeholder="Ancien mot de passe", padx=(50, 0))
        self.create_button(self.generer_f, 'voir_a', '', 1, 1, image=self.oeil,
                           width=25, commande=partial(self.voir, 'ancien_mdp'), bg="#DEDEDE", abg="#ECECEC", height=34, padx=(0, 50))

        self.create_label(self.generer_f, 'nouv_mdp', 'Nouveau mot de passe :', 2, 0,
                          sticky='ew', anchor='w', pady=(20, 0), padx=(50, 0), font=("arial", 20))
        self.add_input(self.generer_f, 'nouv_mdp', 3, 0, sticky='news', show=False, placeholder="Nouveau mot de passe", padx=(50, 0))
        self.create_button(self.generer_f, 'voir_n', '', 3, 1, image=self.oeil,
                           width=25, commande=partial(self.voir, 'nouv_mdp'), bg="#DEDEDE", abg="#ECECEC", height=34, padx=(0, 50))

        self.create_label(self.generer_f, 'nouv_mdp_c', 'Confirmation mot de passe :', 4, 0,
                          sticky='ew', anchor='w', pady=(20, 0), padx=(50, 0), font=("arial", 20))
        self.add_input(self.generer_f, 'nouv_mdp_c', 5, 0, sticky='news', show=False, placeholder="Confirmation nouveau mot de passe", padx=(50, 0))
        self.create_button(self.generer_f, 'voir_c', '', 5, 1, image=self.oeil,
                           width=25, commande=partial(self.voir, 'nouv_mdp_c'), bg="#DEDEDE", abg="#ECECEC", height=34, padx=(0, 50))

        self.create_button(self.generer_f, 'confirmer', 'Confirmer', 6, 0, columnspan=2,
                           commande=partial(self.changer_mdp_user), pady=(15, 10), bg="#DEDEDE", abg="#ECECEC", padx=(50, 50))
        self.create_button(self.generer_f, 'annuler', 'Annuler', 7, 0, columnspan=2,
                           commande=partial(self.generer_f.destroy), bg="#DEDEDE", abg="#ECECEC", padx=(50, 50))

    def build_modifier_mdp_maitre(self):
        """
        Construction de la fenêtre de modification du mdp maitre

        Déroulé :
            - Création des différents éléments :
                - 2 Labels, Expliquation et mot de passe
                - 1 Input, mot de passe
                - 1 Boutons voir
                - 1 Bouton de validation
                - 1 Bouton d'annulation
            - L'interaction se fait avec les fonctions appelées par les boutons
        """
        self.generer_f.grid_columnconfigure(0, weight=1)

        s = 'Cette opération changera\nla clé de chiffrement' \
            '\ndes données. Cela peut\nprendre quelques secondes.' \
            '\nEntrez votre mot de passe\npour confirmer.'

        self.create_label(self.generer_f, 'explication', s, 0, 0, columnspan=2, pady=(30, 20),
                          font=("arial", 20, "bold"))

        self.create_label(self.generer_f, 'mdp_user', 'Mot de passe :', 1, 0, sticky='ew', anchor='w', font=("arial", 20), padx=(50, 0))
        self.add_input(self.generer_f, 'mdp_user', 2, 0, sticky='news', focus=True, show=False, placeholder="Mot de passe", padx=(50, 0))
        self.create_button(self.generer_f, 'voir_a', '', 2, 1, image=self.oeil,
                           width=25, commande=partial(self.voir, 'mdp_user'), bg="#DEDEDE", abg="#ECECEC", height=34, padx=(0, 50))

        self.create_button(self.generer_f, 'confirmer', 'Confirmer', 3, 0, columnspan=2,
                           commande=partial(self.changer_mdp_maitre), pady=(15, 10), bg="#DEDEDE", abg="#ECECEC", padx=(50, 50))
        self.create_button(self.generer_f, 'annuler', 'Annuler', 4, 0, columnspan=2,
                           commande=partial(self.generer_f.destroy), bg="#DEDEDE", abg="#ECECEC", padx=(50, 50))

    def changer_mdp_user(self):
        """
        Fonction qui change le mot de passe de l'utilisateur
        """
        if self.stringvar['nouv_mdp'].get() != self.stringvar['nouv_mdp_c'].get():
            self.stringvar['nouv_mdp'].set('')
            self.input['nouv_mdp'].put_placeholder()
            self.stringvar['nouv_mdp_c'].set('Confirmation non identique')
            self.input['nouv_mdp_c'].convert_placeholder()
            self.input['nouv_mdp_c'].temp_placeholder = "Confirmation non identique"
            self.input['nouv_mdp_c'].configure(show='')
        elif len(self.stringvar['nouv_mdp'].get()) < 10 or self.input["nouv_mdp"].get_content() == "":
            self.stringvar['nouv_mdp'].set('10 caractères minimum')
            self.input['nouv_mdp'].convert_placeholder()
            self.input['nouv_mdp'].temp_placeholder = "10 caractères minimum"
            self.stringvar['nouv_mdp_c'].set('')
            self.input['nouv_mdp_c'].put_placeholder()
            self.input['nouv_mdp'].configure(show='')
        elif not get_master_password(self.stringvar['ancien_mdp'].get()) or self.input["ancien_mdp"].get_content() == "":
            self.stringvar['ancien_mdp'].set('Mot de passe incorrect')
            self.input['ancien_mdp'].convert_placeholder()
            self.input['ancien_mdp'].temp_placeholder = "Mot de passe incorrect"
            self.input['ancien_mdp'].configure(show='')
        else:
            new = self.stringvar['nouv_mdp'].get()
            old = self.stringvar['ancien_mdp'].get()
            change_user_password(old, new)
            self.mdp_user = new
            self.generer_f.destroy()

    def changer_mdp_maitre(self):
        """
        Fonction qui change le mot de passe maitre et réecrit les données
        dans le fichier et dans les listes, dictionnaires
        """
        if self.input["mdp_user"].get_content() == "" or not get_master_password(self.stringvar['mdp_user'].get()):
            self.stringvar['mdp_user'].set('Mot de passe incorrect')
            self.input['mdp_user'].convert_placeholder()
            self.input['mdp_user'].temp_placeholder = "Mot de passe incorrect"
            self.input['mdp_user'].configure(show='')
        else:
            donnees_mdp = self.donnees
            mdp_user = self.stringvar['mdp_user'].get()
            nouv_mdp_maitre = create_master_password(mdp_user)
            with open(".data/store.txt", "w") as f:
                for compte, password in donnees_mdp.items():
                    compte_e_chiffre = encrypt(compte, nouv_mdp_maitre)
                    f.write(f"{compte_e_chiffre}\n")
                    mdp_clear = decrypt(donnees_mdp[compte], self.mdp_maitre)
                    mdp_e_chiffre = encrypt(mdp_clear, nouv_mdp_maitre)
                    f.write(f"{mdp_e_chiffre}\n")
            self.mdp_maitre = nouv_mdp_maitre
            if self.server is not None:
                self.server.update_password(self.mdp_maitre)
            self.donnees_liste = donnees_liste(self.mdp_maitre)
            self.donnees = donnees_dico(self.donnees_liste)
            if self.server is not None:
                self.server.update_data(self.donnees)
            self.generer_f.destroy()
            threading.Thread(target=self.get_links).start()

    def creer_mdp_maitre(self, *args):
        """
        Fonction qui initialise un mot de passe maitre
        """
        if len(self.stringvar['mdp_accueil'].get()) < 10 or self.input["mdp_accueil"].get_content() == "":
            self.stringvar['mdp_accueil'].set('10 caractères minimum')
            self.input['mdp_accueil'].convert_placeholder()
            self.input['mdp_accueil'].temp_placeholder = "10 caractères minimum"
            self.stringvar['mdp_accueil_conf'].set('')
            self.input["mdp_accueil_conf"].put_placeholder()
            self.input['mdp_accueil'].configure(show='')
        elif self.stringvar['mdp_accueil'].get() != self.stringvar['mdp_accueil_conf'].get():
            self.stringvar['mdp_accueil_conf'].set('')
            self.input['mdp_accueil_conf'].put_placeholder()
            self.stringvar['mdp_accueil'].set('Confirmation non identique')
            self.input['mdp_accueil'].convert_placeholder()
            self.input['mdp_accueil'].temp_placeholder = "Confirmation non identique"
            self.input['mdp_accueil'].configure(show='')
        else:
            self.mdp_user = self.stringvar['mdp_accueil'].get()
            self.mdp_maitre = create_master_password(self.mdp_user)
            self.accueil.destroy()

    def build_tout_supprimer(self):
        """
        Fonction qui construit la fenêtre de suppression de toutes les données
        """

        self.generer_f.grid_columnconfigure(0, weight=1)

        self.create_label(self.generer_f, 'avertissement', 'Cette opération effacera\ntoutes vos données', 0, 0,
                          columnspan=2, pady=(30, 25), font=("arial", 25, "bold"))

        self.create_label(self.generer_f, 'mdp_l', "Mot de passe :", 1, 0, sticky='w', pady=(0, 10), padx=(50, 0), font=("arial", 20))
        self.add_input(self.generer_f, 'mdp', 2, 0, width=265, focus=True, show=False, sticky='news', placeholder="Mot de passe", padx=(50, 0))
        self.create_button(self.generer_f, 'voir_mdp', '', 2, 1, commande=partial(self.voir, 'mdp'), image=self.oeil, bg="#DEDEDE", abg="#ECECEC", height=34, padx=(0, 50))

        self.create_label(self.generer_f, 'confirmer_l', 'Tapez "CONFIRMER" :', 3, 0, sticky='w', pady=(30, 10), padx=(50, 0), font=("arial", 20))
        self.add_input(self.generer_f, 'confirmer', 4, 0, columnspan=2, sticky='news', placeholder="CONFIRMER", padx=(50, 50))
        self.input['confirmer'].configure(font=('arial', 20))

        self.create_button(self.generer_f, 'valider_supp', 'Confirmer', 5, 0, columnspan=2,
                           commande=partial(self.tout_supprimer_exe), bg='green', fg='white',
                           abg='#009020', afg='white', pady=(40, 0), padx=(50, 50), font=("arial", 20))


    def tout_supprimer_exe(self):
        """
        Fonction qui vérifie si le mot de passe et les validations sont corrects et supprime toutes les données
        """
        if not self.stringvar['confirmer'].get() == 'CONFIRMER':
            self.stringvar['mdp'].set('Confirmation incorrecte')
            self.input['mdp'].convert_placeholder()
            self.input['mdp'].temp_placeholder = "Confirmation incorrecte"
            self.input['mdp'].configure(show='')
        elif not get_master_password(self.stringvar['mdp'].get()) or self.input["mdp"].get_content() == "":
            self.stringvar['mdp'].set('Mot de passe incorrect')
            self.input['mdp'].convert_placeholder()
            self.input['mdp'].temp_placeholder = "Mot de passe incorrect"
            self.input['mdp'].configure(show='')
        else:
            with open(".data/salt.txt", "w"):
                pass
            with open(".data/master_password.txt", "w"):
                pass
            with open(".data/store.txt", "w"):
                pass
            with open(".data/preferences.txt", "w"):
                pass
            self.menu.destroy()


class Fenetre(CTk):
    def __init__(self, la=100, h=100, texte="", fg_color=("#F1F1F1", "#222325")):

        super().__init__(fg_color=fg_color)

        self.title(texte)

        self.style = ttkthemes.ThemedStyle()

        central_monitor = len(get_monitors()) // 2

        # largeur_ecran = self.winfo_screenwidth()
        largeur_ecran = get_monitors()[central_monitor].width
        # hauteur_ecran = self.winfo_screenheight()
        hauteur_ecran = get_monitors()[central_monitor].height

        cumulated_width = sum([get_monitors()[i].width for i in range(central_monitor)])

        pos_x = largeur_ecran // 2 - la // 2 + cumulated_width
        pos_y = hauteur_ecran // 2 - h // 2
        geometry = f"{la}x{h}+{pos_x}+{pos_y}"
        self.geometry(geometry)


class CTkEntryWithPlaceholder(CTkEntry):
    def __init__(self, master, textvariable, width=None, placeholder="PLACEHOLDER", color='gray', visible=None, index=None, recherche=False):

        if textvariable.get():
            text_color="gray10"
        else:
            text_color=color

        super().__init__(master, textvariable=textvariable, width=width, text_color=text_color)

        self.placeholder = placeholder
        self.temp_placeholder = None
        self.placeholder_color = color
        self.default_fg_color = "gray10"

        self.visible = visible
        self.index = index

        self.bind("<FocusIn>", self.refocus_launcher)
        self.bind("<Button-1>", self.refocus_launcher)

        self.bind('<Delete>', partial(self.shortcuts_manager))
        self.bind('<Control-a>', partial(self.shortcuts_manager))



        if not recherche:
            self.bind("<Key>", self.update)

        if not self.get():
            self.put_placeholder()

    def shortcuts_manager(self, event=None):
        if self._entry['fg'] == self.default_fg_color:
            return
        return "break"

    def convert_real_text(self):
        self._entry['fg'] = self.default_fg_color
        self._entry.icursor('end')

    def convert_placeholder(self):
        self._entry['fg'] = self.placeholder_color
        self._entry.icursor(0)

        if self.visible is not None:
            self.configure(show="")

    def put_placeholder(self):
        self._entry.insert(0, self.placeholder)
        self._entry.icursor(0)
        self._entry['fg'] = self.placeholder_color

        if self.visible is not None:
            self.configure(show="")

    def foc_in(self, *args):
        try:
            if self._entry['fg'] == self.placeholder_color and self.get() != self.placeholder and self.get() != self.temp_placeholder:
                if self.placeholder == self.get()[-len(self.placeholder):]:
                    placeholder = self.placeholder
                else:
                    placeholder = self.temp_placeholder
                difference = len(self.get()) - len(placeholder)
                self.delete(difference, 'end')
                self._entry['fg'] = self.default_fg_color

                if self.visible is not None:
                    if self.visible[self.index]:
                        self.configure(show="")
                    else:
                        self.configure(show="●")

        except TclError:
            pass

        except TypeError:
            self.delete('0', 'end')
            self.put_placeholder()

    def foc_out(self, *args):
        try:
            if not self.get():
                self.put_placeholder()
        except TclError:
            pass

    def refocus_launcher(self, *args):
        threading.Thread(target=self.refocus).start()

    def refocus(self, *args):
        time.sleep(0.01)
        if self._entry['fg'] == self.placeholder_color and (self.get() == self.placeholder or (self.temp_placeholder is not None and self.get() == self.temp_placeholder)):
            placeholder = self.get()

            self.delete('0', 'end')
            if placeholder == self.placeholder:
                self.insert(0, self.placeholder)
            else:
                self.insert(0, self.temp_placeholder)

            self._entry.icursor(0)

    def update(self, *args):
        threading.Thread(target=self.update_placeholder).start()

    def update_placeholder(self, *args):
        try:
            time.sleep(0.001)
            self.foc_in()
            self.foc_out()

            if self._entry['fg'] == self.placeholder_color:
                self._entry.icursor(0)
        except TclError:
            pass

    def get_content(self):
        if self._entry['fg'] == self.placeholder_color:
            return ""
        else:
            return self.get()
