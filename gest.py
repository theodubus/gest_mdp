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
from web import *
import threading
import platform
import json
from copy import copy
import ttkthemes


# Gestionnaire (codé en objet)
class Application:
    def __init__(self):
        """
        Init : initialisation des variables
        """

        # web
        self.onglets = dict()
        self.login_urls = dict()
        self.login_links = []
        self.handles = []
        self.driver = None
        self.browser_opened = False
        self.decompte = 0
        self.temp = dict()

        # preferences
        keys = ['chiffres', 'lettresmin', 'lettresmaj', 'ponctuation', 'cara_spe', 'no_similar',
                'taille', 'profil_linux', 'profil_windows', 'autoconnexion']
        elements = ['1', '1', '1', '0', '0', '1', '25', '', '', '1']
        self.preferences = {k: v for k, v in zip(keys, elements)}

        # Tkinter
        self.label = dict()
        self.input = dict()
        self.button = dict()
        self.visible = dict()
        self.frame = dict()
        self.stringvar = dict()
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
        self.crayon = None
        self.copier = None
        self.poubelle = None
        self.web = None
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
        self.autoconnect_thread = None

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
        self.oeil_a = PhotoImage(file="images/oeil_a.png")
        self.logo = PhotoImage(file="images/logo.png")
        self.accueil.iconphoto(True, self.logo)

        # Pas de mot de passe maître = première connexion
        if current_password() == "":

            if platform.system() != "Windows":
                self.accueil.config(padx=105, pady=30)
            else:
                self.accueil.config(padx=145, pady=30)

            # Construction de la fenêtre
            self.build_accueil_premiere()

            # Ajout d'un raccourci clavier
            self.accueil.bind('<Return>', partial(self.creer_mdp_maitre))

        # Sinon, ouverture avec page de login
        else:
            if platform.system() != "Windows":
                self.accueil.config(padx=105, pady=80)
            else:
                self.accueil.config(padx=145, pady=80)

            # Construction de la fenêtre
            self.build_accueil()

            # Ajout d'un raccourci clavier
            self.accueil.bind('<Return>', partial(self.valider, 'mdp_accueil', self.accueil))

        # Taille non modifiable
        self.accueil.resizable(width=False, height=False)

        # Ajout d'un raccourci clavier
        self.accueil.bind('<Control-BackSpace>', partial(self.effacer, self.accueil))
        self.accueil.bind('<Control-Delete>', partial(self.effacer_fin, self.accueil))

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
        self.oeil = PhotoImage(file="images/oeil.png")
        self.crayon = PhotoImage(file="images/crayon.png")
        self.copier = PhotoImage(file="images/copier.png")
        self.poubelle = PhotoImage(file="images/poubelle.png")
        self.web = PhotoImage(file="images/web.png")
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

        self.menu.config(padx=60, pady=40)

        # Construction de la fenêtre
        self.build_menu()

        # Ajout de raccourcis clavier
        self.menu.bind('<Control-BackSpace>', partial(self.effacer_update))
        self.menu.bind('<Control-Delete>', partial(self.effacer_fin_update))
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
        self.menu_deroulant = dict()
        self.frames_comptes = dict()
        self.checkBouton = dict()
        self.radioBouton = dict()
        self.generer_f = None
        self.confirmer_f = None
        self.appui_valider = False
        self.onglets = dict()
        self.login_urls = dict()
        self.login_links = []
        self.handles = []
        self.driver = None
        self.browser_opened = False
        self.decompte = 0
        self.temp = dict()

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
                          0, 0, columnspan=2, pady=(0, 50))
        self.add_input(self.accueil, 'mdp_accueil', 1, 0, width=43, focus=True, show=False, sticky='news')
        self.create_button(self.accueil, 'valider_accueil', 'Valider', 2, 0, columnspan=2,
                           commande=partial(self.valider, 'mdp_accueil', self.accueil), bg='green',
                           fg='white', abg='#009020', afg='white', pady=(50, 0))
        self.create_button(self.accueil, 'voir_accueil', '', 1, 1,
                           commande=partial(self.voir, 'mdp_accueil'), image=self.oeil_a)

        self.stringvar['erreur'] = StringVar()
        self.label['mauvais_mdp'] = Label(self.accueil,
                                          textvariable=self.stringvar['erreur'], fg='red', font=("arial", 20, "bold"))
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
        self.add_input(self.accueil, 'mdp_accueil', 2, 0, width=43, focus=True, show=False, sticky='news')

        self.create_button(self.accueil, 'voir_accueil', '', 2, 1,
                           commande=partial(self.voir, 'mdp_accueil'), image=self.oeil_a)

        self.create_label(self.accueil, 'label_accueil_conf',
                          "Confirmation mot de passe :", 3, 0, sticky='w', pady=(30, 10))
        self.add_input(self.accueil, 'mdp_accueil_conf', 4, 0, width=43, focus=False, show=False, sticky='news')

        self.create_button(self.accueil, 'voir_accueil', '', 4, 1,
                           commande=partial(self.voir, 'mdp_accueil_conf'), image=self.oeil_a)

        self.create_button(self.accueil, 'valider_accueil', 'Valider', 5, 0, columnspan=2, fg='white', abg='#009020',
                           afg='white', commande=partial(self.creer_mdp_maitre), bg='green', pady=(30, 0), height=2)

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
        self.autoconnect_thread = threading.Thread(target=self.autoconnect)
        self.autoconnect_thread.start()

        if platform.system() != "Windows":
            self.menu.style.theme_use('ubuntu')
            padx = 105
        else:
            padx = 145

        self.add_input(self.menu, 'recherche', 0, 0, focus=True, sticky='news', pady=(0, 5))
        self.create_button(self.menu, '+', '+', 0, 1, pady=(0, 5),
                           commande=partial(self.create_toplevel, 450, 580, 'Créer', 'generer', 'creer', 60, 25,
                                            fc=partial(self.build_creer)))

        self.add_checkbutton(self.menu, 'auto', 'autoconnexion (temp)',
                             1, 0, '1', '0', self.preferences['autoconnexion'])

        self.create_frame(self.menu, 'liste_handler', 2, 0, columnspan=2, pady=(5, 25), sticky='news')
        self.create_scrollable_frame(self.frame['liste_handler'], 'liste')

        self.menu_deroulant['options'] = Menu(self.menu)
        self.menu_deroulant['1'] = Menu(self.menu_deroulant['options'], tearoff=0)
        self.menu_deroulant['donnees'] = Menu(self.menu_deroulant['1'], tearoff=0)
        self.menu_deroulant['profil'] = Menu(self.menu_deroulant['1'], tearoff=0)
        self.menu_deroulant['securite'] = Menu(self.menu_deroulant['profil'], tearoff=0)

        self.menu_deroulant['1'].add_command(label='Générer',
                                             command=partial(self.create_toplevel, 450, 380, 'Générer', 'generer',
                                                             'generer', 60, 40, fc=partial(self.build_generer)))
        self.menu_deroulant['donnees'].add_command(label='Nouveau compte',
                                                   command=partial(self.create_toplevel, 450, 580, 'Créer', 'generer',
                                                                   'creer', 60, 25, fc=partial(self.build_creer)))
        self.menu_deroulant['donnees'].add_command(label='Importer des données',
                                                   command=partial(self.importer))
        self.menu_deroulant['donnees'].add_command(label='Exporter les données',
                                                   command=partial(self.exporter))

        self.menu_deroulant['1'].add_cascade(label="Données", menu=self.menu_deroulant['donnees'])
        self.menu_deroulant['securite'].add_command(label='Modifier le mot de passe utilisateur',
                                                    command=partial(self.create_toplevel, 450, 370,
                                                                    'Modifier le mot de passe utilisateur',
                                                                    'generer', 'modifier_mdp_user', 60, 30,
                                                                    fc=partial(self.build_modifier_mdp_user)))
        self.menu_deroulant['securite'].add_command(label='Changer de clé de chiffrement',
                                                    command=partial(self.create_toplevel, 480, 430,
                                                                    'Changer de clé de chiffrement',
                                                                    'generer', 'modifier_mdp_maitre', 60, 30,
                                                                    fc=partial(self.build_modifier_mdp_maitre)))
        self.menu_deroulant['securite'].add_command(label='Supprimer toutes les données',
                                                    command=partial(self.create_toplevel, 600, 450,
                                                                    'Supprimer toutes les données', 'generer',
                                                                    'tout_supprimer', padx, 35,
                                                                    fc=partial(self.build_tout_supprimer)))
        self.menu_deroulant['profil'].add_cascade(label="Sécurité", menu=self.menu_deroulant['securite'])
        self.menu_deroulant['profil'].add_command(label='Modifier Préférences',
                                                  command=partial(self.create_toplevel, 410, 430,
                                                                  'Modifier Préférences', 'generer', 'preferences', 60,
                                                                  40, fc=partial(self.build_preferences)))
        self.menu_deroulant['1'].add_cascade(label="Profil", menu=self.menu_deroulant['profil'])

        if platform.system() != "Windows":
            self.menu_deroulant['1'].add_command(label='Se déconnecter', command=partial(self.deconnecter))

        self.menu_deroulant['options'].add_cascade(label="Options", menu=self.menu_deroulant['1'])
        self.menu.config(menu=self.menu_deroulant['options'])
        self.menu.grid_rowconfigure(1, weight=1)
        self.menu.grid_columnconfigure(0, weight=1)

        self.update()

    def deconnecter(self):
        """
        Méthode qui permet de se déconnecter et d'arrêter la connexion persistante
        """
        self.menu.destroy()
        self.deconnexion = True
        self.stop = True
        self.autoconnect_thread.join()
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
                          sticky='ew', anchor='center', columnspan=2)
        self.generer_f.grid_columnconfigure(0, weight=1)
        self.create_button(self.generer_f, 'voir', '', 0, 2, image=self.oeil,
                           width=25, height=25, commande=partial(self.voir_gen))
        self.create_button(self.generer_f, 'copier', '', 0, 3, image=self.copier,
                           width=25, height=25, commande=partial(self.copier_gen))

        self.add_checkbutton(self.generer_f, 'chiffres', '0-9', 1, 0,
                             digits, '', self.preferences['chiffres'])
        self.add_checkbutton(self.generer_f, 'lettresmin', 'a-z', 2, 0,
                             ascii_lowercase, '', self.preferences['lettresmin'])
        self.add_checkbutton(self.generer_f, 'lettresmaj', 'A-Z', 3, 0,
                             ascii_uppercase, '', self.preferences['lettresmaj'])
        self.add_checkbutton(self.generer_f, 'ponctuation', '!#/', 4, 0,
                             punctuation, '', self.preferences['ponctuation'])
        self.add_checkbutton(self.generer_f, 'cara_spe', '£çÉ', 5, 0,
                             "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨", '', self.preferences['cara_spe'])
        self.add_checkbutton(self.generer_f, 'double', 'no similar', 6, 0, "on", 'off', self.preferences['no_similar'])
        self.create_label(self.generer_f, 'taille', 'Taille (10-100) : ', 7, 0,
                          font=('arial', '12'), sticky='w', padx=0)
        self.add_input(self.generer_f, 'taille', 7, 1, sticky='w', width=3,
                       padx=(0, 100), default=self.preferences['taille'], focus=True)
        self.input['taille'].icursor('end')
        self.create_button(self.generer_f, 'generer', 'Générer', 8, 0, columnspan=4,
                           bg='#009020', fg='white', abg='#00A030', afg='white', commande=partial(self.generer_mdp))
        self.generer_mdp()
        self.voir_gen()

    def update_preferences(self):
        """
        Mise à jour des variables de préférences
        """
        with open(".data/preferences.txt", 'r') as f:
            elements = f.read().splitlines()
            if len(elements) != 10:
                elements = ['1', '1', '1', '0', '0', '1', '25', '', '', '1']
        keys = ['chiffres', 'lettresmin', 'lettresmaj', 'ponctuation', 'cara_spe',
                'no_similar', 'taille', 'profil_linux', 'profil_windows', 'autoconnexion']
        self.preferences = {k: v for k, v in zip(keys, elements)}

        if platform.system() != "Windows":
            self.preferences['profil'] = self.preferences['profil_linux']
        else:
            self.preferences['profil'] = self.preferences['profil_windows']

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

        self.create_label(self.generer_f, 'profil_label', 'Profil : ', 0, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 15, "bold"))
        self.add_input(self.generer_f, 'profil', 0, 1, sticky='news',
                       columnspan=3, pady=0, default=self.preferences['profil'])

        self.generer_f.grid_columnconfigure(0, weight=1)

        self.add_checkbutton(self.generer_f, 'autoconnexion', 'auto', 1, 0, "1", '0', self.preferences['autoconnexion'])
        self.add_checkbutton(self.generer_f, 'chiffres', '0-9', 2, 0, digits, '', self.preferences['chiffres'])
        self.add_checkbutton(self.generer_f, 'lettresmin', 'a-z', 3, 0,
                             ascii_lowercase, '', self.preferences['lettresmin'])
        self.add_checkbutton(self.generer_f, 'lettresmaj', 'A-Z', 4, 0,
                             ascii_uppercase, '', self.preferences['lettresmaj'])
        self.add_checkbutton(self.generer_f, 'ponctuation', '!#/', 5, 0,
                             punctuation, '', self.preferences['ponctuation'])
        self.add_checkbutton(self.generer_f, 'cara_spe', '£çÉ', 6, 0,
                             "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨", '', self.preferences['cara_spe'])
        self.add_checkbutton(self.generer_f, 'double', 'no similar', 7, 0, "on", 'off', self.preferences['no_similar'])
        self.create_label(self.generer_f, 'taille', 'Taille (10-100) : ', 8, 0,
                          font=('arial', '12'), sticky='w', padx=0)
        self.add_input(self.generer_f, 'taille', 8, 1, sticky='w', width=3,
                       padx=(0, 100), default=self.preferences['taille'], focus=True)
        self.input['taille'].icursor('end')
        self.create_button(self.generer_f, 'modifier', 'Modifier', 9, 0, columnspan=4,
                           bg='#009020', fg='white', abg='#00A030', afg='white',
                           commande=partial(self.modifier_preferences))

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

        self.create_label(self.generer_f, 'compte_mdp', compte, 0, 0, sticky='ew',
                          anchor='center', columnspan=4, pady=(0, 15), font=("arial", 18, "bold", 'underline'))

        self.create_label(self.generer_f, 'user_label', 'Utilisateur : ', 1, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 15, "bold"))
        self.add_input(self.generer_f, 'username', 1, 1, sticky='news', columnspan=3, pady=(0, 15), default=user)

        self.create_label(self.generer_f, 'link_label', 'Lien : ', 2, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 15, "bold"))
        self.add_input(self.generer_f, 'link', 2, 1, sticky='news', columnspan=3, pady=0, default=link)
        self.add_checkbutton(self.generer_f, 'prio', 'prio', 3, 0, '1', '0', prio)
        self.add_checkbutton(self.generer_f, 'long', 'long', 3, 1, '1', '0', wait)
        self.add_checkbutton(self.generer_f, 'doubleauth', '2FA', 3, 2, '1', '0', doubleauth, columnspan=2)

        self.add_input(self.generer_f, 'generer_mdp', 4, 0, sticky='news', columnspan=2, show=False, default=password)
        self.generer_f.grid_columnconfigure(0, weight=1)
        self.create_button(self.generer_f, 'voir', '', 4, 2, image=self.oeil,
                           width=25, height=25, commande=partial(self.voir))
        self.create_button(self.generer_f, 'copier', '', 4, 3, image=self.copier,
                           width=25, height=25, commande=partial(self.copier_gen_modif))

        self.add_checkbutton(self.generer_f, 'chiffres', '0-9', 5, 0,
                             digits, '', self.preferences['chiffres'])
        self.add_checkbutton(self.generer_f, 'lettresmin', 'a-z', 6, 0,
                             ascii_lowercase, '', self.preferences['lettresmin'])
        self.add_checkbutton(self.generer_f, 'lettresmaj', 'A-Z', 7, 0,
                             ascii_uppercase, '', self.preferences['lettresmaj'])
        self.add_checkbutton(self.generer_f, 'ponctuation', '!#/', 8, 0,
                             punctuation, '', self.preferences['ponctuation'])
        self.add_checkbutton(self.generer_f, 'cara_spe', '£çÉ', 9, 0,
                             "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨", '', self.preferences['cara_spe'])
        self.add_checkbutton(self.generer_f, 'double', 'no similar', 10, 0, "on", 'off', self.preferences['no_similar'])
        self.create_label(self.generer_f, 'taille', 'Taille (10-100) : ', 11, 0,
                          font=('arial', '12'), sticky='w', padx=0)
        self.add_input(self.generer_f, 'taille', 11, 1, sticky='w', width=3,
                       padx=(0, 100), default=self.preferences['taille'], focus=True)
        self.input['taille'].icursor('end')
        self.create_button(self.generer_f, 'generer', 'Générer', 12, 0, columnspan=4,
                           bg='#1030EE', fg='white', abg='#2050FF', afg='white',
                           commande=partial(self.generer_mdp_modif), pady=(15, 0))
        self.create_button(self.generer_f, 'modifier', 'Modifier', 13, 0, columnspan=4,
                           bg='#009020', fg='white', abg='#00A030', afg='white',
                           commande=partial(self.create_toplevel, 350, 200, '', 'confirmer',
                                            'confirmation', 30, 15, compte=compte))

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
                          anchor='w', pady=(0, 15), font=("arial", 15, "bold"))
        self.add_input(self.generer_f, 'nom_compte', 0, 1, sticky='news', columnspan=3, focus=True, pady=(0, 15))

        self.create_label(self.generer_f, 'user_label', 'Utilisateur : ', 1, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 15, "bold"))
        self.add_input(self.generer_f, 'username', 1, 1, sticky='news', columnspan=3, pady=(0, 15))

        self.create_label(self.generer_f, 'link_label', 'Lien : ', 2, 0, sticky='ew',
                          anchor='w', pady=(0, 15), font=("arial", 15, "bold"))
        self.add_input(self.generer_f, 'link', 2, 1, sticky='news', columnspan=3, pady=0)

        self.add_checkbutton(self.generer_f, 'prio', 'prio', 3, 0, '1', '0', '0')
        self.add_checkbutton(self.generer_f, 'long', 'long', 3, 1, '1', '0', '0')
        self.add_checkbutton(self.generer_f, 'doubleauth', '2FA', 3, 2, '1', '0', '0', columnspan=2)

        self.add_input(self.generer_f, 'generer_mdp', 4, 0, sticky='news', columnspan=2, show=False)
        self.generer_f.grid_columnconfigure(0, weight=1)
        self.create_button(self.generer_f, 'voir', '', 4, 2, image=self.oeil, width=25,
                           height=25, commande=partial(self.voir))
        self.create_button(self.generer_f, 'copier', '', 4, 3, image=self.copier, width=25,
                           height=25, commande=partial(self.copier_gen_modif))

        self.add_checkbutton(self.generer_f, 'chiffres', '0-9', 5, 0, digits, '', self.preferences['chiffres'])
        self.add_checkbutton(self.generer_f, 'lettresmin', 'a-z', 6, 0,
                             ascii_lowercase, '', self.preferences['lettresmin'])
        self.add_checkbutton(self.generer_f, 'lettresmaj', 'A-Z', 7, 0,
                             ascii_uppercase, '', self.preferences['lettresmaj'])
        self.add_checkbutton(self.generer_f, 'ponctuation', '!#/', 8, 0,
                             punctuation, '', self.preferences['ponctuation'])
        self.add_checkbutton(self.generer_f, 'cara_spe', '£çÉ', 9, 0,
                             "àâäçéèêëîïôöùûüÿÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ¤£µ§°²¨", '', self.preferences['cara_spe'])
        self.add_checkbutton(self.generer_f, 'double', 'no similar', 10, 0, "on", "off", self.preferences['no_similar'])
        self.create_label(self.generer_f, 'taille', 'Taille (10-100) : ', 11, 0,
                          font=('arial', '10'), sticky='w', padx=0)
        self.add_input(self.generer_f, 'taille', 11, 1, sticky='w',
                       width=3, padx=(0, 100), default=self.preferences['taille'])
        self.input['taille'].icursor('end')
        self.create_button(self.generer_f, 'generer', 'Générer', 12, 0, columnspan=4,
                           bg='#1030EE', fg='white', abg='#2050FF', afg='white',
                           commande=partial(self.generer_mdp_modif), pady=(15, 0))
        self.create_button(self.generer_f, 'creer', 'Créer', 13, 0, columnspan=4, bg='#009020',
                           fg='white', abg='#00A030', afg='white', commande=partial(self.creer_mdp))
        self.generer_mdp_modif()

    def add_checkbutton(self, fenetre, index, texte, row, column, on, off, default, padx=None, pady=(3, 3),
                        columnspan=1):
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
        self.checkBouton[index] = Checkbutton(fenetre, text=texte, variable=self.stringvar[f'check{index}'],
                                              offvalue=off, onvalue=on, font=("arial", 15))
        self.checkBouton[index].grid(row=row, column=column, padx=padx, pady=pady, sticky='w', columnspan=columnspan)

    def add_radiobutton(self, fenetre, index, texte, row, column, value, default=False, padx=None, commande=None,
                        columnspan=1):
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
            self.radioBouton[value] = Radiobutton(fenetre, text=texte, variable=self.stringvar[f'radio{index}'],
                                                  value=value, font=("arial", 15))
        else:
            self.radioBouton[value] = Radiobutton(fenetre, text=texte, variable=self.stringvar[f'radio{index}'],
                                                  value=value, font=("arial", 15), command=commande)

        self.radioBouton[value].grid(row=row, column=column, padx=padx, pady=3, sticky='w', columnspan=columnspan)

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
        self.frame[index] = Frame(fenetre, bg=bg)
        self.frame[index].pack(fill='both', padx=padx, pady=pady)
        self.create_label(self.frame[index], f"compte{index}", f"{index[:15]}", 0, 0, bg='white', padx=(25, 15),
                          pady=20, width=12, anchor='w', font=("arial", 15, "underline"), rowspan=2)

        mdp_l = decrypt(self.donnees[index], self.mdp_maitre)
        link, login = link_login(mdp_l)
        user = user_mdp(login)[0]
        if user == '':
            user = '(non défini)'
        self.create_label(self.frame[index], f"user_label{index}", user, 0, 2, bg='white', pady=(20, 0),
                          width=18, sticky='w', padx=(0, 20), anchor='w', user=True)
        self.create_label(self.frame[index], f"points{index}", "", 1, 2, bg='white', pady=(0, 20),
                          width=18, sticky='w', padx=(0, 20), textvar=True, anchor='w')

        self.create_button(self.frame[index], f"copier_user{index}", '', 0, 1, sticky='se', image=self.copier,
                           width=25, height=25, commande=partial(self.copy_user, index), padx=(0, 10), pady=5)
        self.create_button(self.frame[index], f"copier{index}", '', 1, 1, sticky='en', image=self.copier,
                           width=25, height=25, commande=partial(self.copier_pp, f"points{index}"), padx=(0, 10))

        if link != '':
            self.create_button(self.frame[index], f"voir{index}", '', 0, 3, sticky='se', image=self.oeil, width=25,
                               height=25, commande=partial(self.voir_mdp, f"points{index}"), rowspan=1, padx=5, pady=5)
            self.create_button(self.frame[index], f"modif{index}", '', 0, 4, sticky='se', image=self.crayon, width=25,
                               height=25, rowspan=1, padx=0, pady=5,
                               commande=partial(self.create_toplevel, 450, 580, 'Modifier', 'generer', 'modifier',
                                                60, 25, fc=partial(self.build_modifier, compte=index)))
            self.create_button(self.frame[index], f"supprimer{index}", '', 1, 3, sticky='en', image=self.poubelle,
                               width=25, height=25, rowspan=1, padx=5,
                               commande=partial(self.create_toplevel, 350, 200, '', 'confirmer',
                                                'confirmation_sup', 30, 15,
                                                s='Cette opération\n est définitive.\n\nConfirmer la suppression ?\n',
                                                compte=index))

            self.create_button(self.frame[index], f"web{index}", '', 1, 4, sticky='en', image=self.web, width=25,
                               height=25, commande=partial(self.ouvrir_fenetre, link, login, index),
                               rowspan=1, padx=0, bg='white')
        else:
            self.create_button(self.frame[index], f"voir{index}", '', 0, 3, sticky='e', image=self.oeil, width=25,
                               height=25, commande=partial(self.voir_mdp, f"points{index}"), rowspan=2, padx=0, pady=0)
            self.create_button(self.frame[index], f"modif{index}", '', 0, 4, sticky='e', image=self.crayon, width=25,
                               height=25, rowspan=2, padx=0, pady=0,
                               commande=partial(self.create_toplevel, 450, 580, 'Modifier', 'generer', 'modifier', 60,
                                                25, fc=partial(self.build_modifier, compte=index)))
            self.create_button(self.frame[index], f"supprimer{index}", '', 0, 5, sticky='e', image=self.poubelle,
                               width=25, height=25, rowspan=2, padx=0, pady=0,
                               commande=partial(self.create_toplevel, 350, 200, '', 'confirmer',
                                                'confirmation_sup', 30, 15,
                                                s='Cette opération\n est définitive.\n\nConfirmer la suppression ?\n',
                                                compte=index))

    def create_frame(self, fenetre, index, row, column, bg='#BBBBBB', columnspan=1, pady=None, padx=None, sticky=None):
        """
        Création d'une frame

        Déroulé :
            - Création de la frame
            - Ajout de la frame
        """
        self.frame[index] = Frame(fenetre, width=200, height=200, bg=bg)
        self.frame[index].grid(row=row, column=column, sticky=sticky, columnspan=columnspan, pady=pady, padx=padx)
        self.frame[index].grid_columnconfigure(0, weight=1)

    def create_label(self, fenetre, index, texte, ligne, colonne, columnspan=1, rowspan=1, font=("arial", 15), bg=None,
                     padx=None, pady=None, width=None, sticky=None, textvar=False, anchor=None, user=False, fg=None):
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

        if textvar:
            self.stringvar[index] = StringVar()
            self.stringvar[index].set('●●●●●●●●●●●●●●')
            self.visible[index] = False
            self.label[index] = Label(fenetre, textvariable=self.stringvar[index],
                                      font=font, bg=bg, width=width, anchor=anchor, fg=fg)
        elif user:
            self.stringvar[index] = StringVar()
            self.stringvar[index].set(texte)
            self.label[index] = Label(fenetre, textvariable=self.stringvar[index],
                                      font=font, bg=bg, width=width, anchor=anchor, fg=fg)
        else:
            self.label[index] = Label(fenetre, text=texte, font=font, bg=bg, width=width, anchor=anchor, fg=fg)
        self.label[index].grid(row=ligne, column=colonne, columnspan=columnspan,
                               rowspan=rowspan, padx=padx, pady=pady, sticky=sticky)

    def create_button(self, fenetre, index, texte, ligne, colonne, columnspan=1, rowspan=1,
                      commande=None, bg=None, fg=None, abg=None, afg=None,
                      sticky='ew', height=None, width=None, image=None, pady=None, padx=None):
        """
        Ajout d'un bouton à la fenêtre

        Permet l'ajout facile, car gère tout :
            - Création du bouton
            - Sauvegarde du bouton dans un dictionnaire (permettant de garder la trace des éléments)
            - Ajout du bouton dans la fenêtre
        """
        self.button[index] = Button(fenetre, text=texte, command=commande, bg=bg, fg=fg, activebackground=abg,
                                    activeforeground=afg, width=width, height=height, image=image)
        self.button[index].grid(row=ligne, column=colonne, columnspan=columnspan,
                                rowspan=rowspan, sticky=sticky, pady=pady, padx=padx)

    def add_input(self, fenetre, index, ligne, colonne, pady=None, padx=None, width=None,
                  focus=False, show=True, sticky=None, columnspan=1, default=None, placeholder=''):
        """
        Ajout d'un champ de saisie à la fenêtre

        Permet l'ajout facile, car gère tout :
            - Création de la variable de contenu du champ de saisie
            - Création du champ de saisie
            - Sauvegarde du champ de saisie dans un dictionnaire (permettant de garder la trace des éléments)
            - Ajout du champ de saisie dans la fenêtre

        Certains champs de saisies sont cachés ou non par défaut
        """
        self.stringvar[index] = StringVar()
        if default is not None:
            self.stringvar[index].set(default)
        if placeholder == '':
            self.input[index] = Entry(fenetre, textvariable=self.stringvar[index], width=width)
        else:
            self.input[index] = EntryWithPlaceholder(fenetre, textvariable=self.stringvar[index], width=width,
                                                     placeholder=placeholder)
        if focus:
            self.input[index].focus_set()
        self.input[index].grid(row=ligne, column=colonne, pady=pady, sticky=sticky, columnspan=columnspan, padx=padx)
        if not show:
            self.visible[index] = False
            self.input[index].config(show="●")

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
            self.input[index].config(show="●")
        else:
            self.visible[index] = True
            self.input[index].config(show="")

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
        """
        pyperclip.copy(self.stringvar[f"user_label{index}"].get())

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

        compte = self.stringvar['recherche'].get().lower()
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
        if type_fenetre != 'generer' and fonction != 'confirmation_sup':
            username = self.stringvar['username'].get()
            link = self.stringvar['link'].get()
            if len(username) > 99:
                self.stringvar['username'].set('Nom trop long')
                return
            elif len(link) > 999:
                self.stringvar['username'].set('Lien trop long')
                return

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
            if type_fenetre != 'generer' and fonction != 'confirmation_sup':
                sur_fenetre = Toplevel(self.generer_f, width=w, height=h)
            else:
                sur_fenetre = Toplevel(self.menu, width=w, height=h)

            sur_fenetre.title(title)
            largeur_ecran = self.menu.winfo_screenwidth()
            hauteur_ecran = self.menu.winfo_screenheight()
            pos_x = largeur_ecran // 2 - w // 2
            pos_y = hauteur_ecran // 2 - h // 2
            geometry = f"{w}x{h}+{pos_x}+{pos_y}"
            sur_fenetre.geometry(geometry)
            sur_fenetre.resizable(height=False, width=False)
            sur_fenetre.config(padx=padx, pady=pady)

            if type_fenetre == 'generer':
                sur_fenetre.bind('<Control-BackSpace>', partial(self.effacer, sur_fenetre))
                sur_fenetre.bind('<Control-Delete>', partial(self.effacer_fin, sur_fenetre))

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
                self.create_label(self.confirmer_f, 'choix', s, 0, 0, columnspan=2, anchor='center')

                if fonction == 'confirmation':
                    self.create_button(self.confirmer_f, 'oui', 'Oui', 1, 0,
                                       commande=partial(self.confirmation, compte))
                    self.create_button(self.confirmer_f, 'non', 'Non', 1, 1, commande=self.generer_f.destroy)
                    self.confirmer_f.bind('<Return>', partial(self.confirmation, compte))
                else:  # fonction == 'confirmation_sup'
                    self.create_button(self.confirmer_f, 'oui', 'Oui', 1, 0,
                                       commande=partial(self.confirmation_sup, compte))
                    self.create_button(self.confirmer_f, 'non', 'Non', 1, 1, commande=self.confirmer_f.destroy)
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

    def autoconnect(self):
        """
        Connexion automatique :
        - Bascule sur le nouvel onglet que vient de créer l'utilisateur s'il le fait
        - Regarde s'il est sur une page de connexion et si oui, essaye de se connecter
        """
        self.stop = False
        while threading.main_thread().is_alive() and not self.stop:
            try:
                if self.stringvar['checkauto'].get() == '1':
                    if self.browser_opened is True:

                        try:
                            if self.driver is not None:

                                tab = [t for t in self.driver.window_handles if t not in self.handles]
                                if len(tab) != 0:
                                    if len(tab) == 1:
                                        cur_handles = self.driver.window_handles
                                        time.sleep(3)
                                        if cur_handles == self.driver.window_handles:
                                            # print("new")
                                            self.driver.switch_to.window(tab[0])
                                            self.decompte = 20
                                    self.handles = self.driver.window_handles

                        except Exception as e:
                            # print(e)
                            self.browser_opened = False
                            self.driver.quit()
                            self.driver = None

                        try:
                            if self.driver is not None:
                                url_l = self.driver.current_url
                                url = domaine(url_l)
                                if url in self.login_urls.keys():
                                    # print("conn page")
                                    link = url
                                    compte = self.login_urls[link]
                                    chaine_clair = decrypt(self.donnees[compte], self.mdp_maitre)

                                    l, login = link_login(chaine_clair)

                                    wait = False
                                    if l != '':
                                        wait = doubleauth_wait_prio_link(l)[1]
                                        if wait == '1':
                                            wait = True
                                        else:
                                            wait = False

                                    user, password = user_mdp(login)

                                    doubleauth = doubleauth_wait_prio_link(l)[0]
                                    code = False
                                    if doubleauth == '1':
                                        code = compte

                                    login_connect(self.driver, link, user, password, wait=wait, deja_charge=True,
                                                  doubleauth=code)

                        except closed_tab:
                            pass

                        except IndexError:
                            pass

                        except Exception as e:
                            # print(e)
                            self.browser_opened = False
                            self.driver.quit()
                            self.driver = None
            except: #KeyError
                pass

            if self.decompte > 0:
                time.sleep(1.5)
                self.decompte -= 1
            else:
                time.sleep(4)

    def ouvrir_fenetre(self, link, login, compte):
        """
        Ouvre une fenêtre pour se connecter à un compte
        Si la fênetre est déjà ouverte, bascule sur celle-ci
        """
        doubleauth, wait, prio, link = doubleauth_wait_prio_link(link)
        code = False
        if doubleauth == '1':
            code = compte

        if wait == "1":
            wait = True
        else:
            wait = False
        user, password = user_mdp(login)
        try:
            if not self.browser_opened:
                self.browser_opened = True
                # self.driver = connexion_chrome_1(self.preferences['profil'])
                # self.driver = connexion_chrome_2(self.preferences['profil'])
                self.driver = connexion_firefox(self.preferences['profil'])
                login_connect(self.driver, link, user, password, wait=wait, deja_charge=False, doubleauth=code)
                self.onglets[compte] = self.driver.window_handles[0]
            else:
                if compte not in self.onglets.keys():
                    self.onglets[compte] = False
                previous_handles = self.driver.window_handles
                nouv = new_page(self.driver, compte, self.onglets[compte])
                new_handles = self.driver.window_handles
                if nouv:
                    login_connect(self.driver, link, user, password, wait=wait, deja_charge=False, doubleauth=code)
                    tab = [t for t in new_handles if t not in previous_handles]
                    if len(tab) != 0:
                        tab = tab[0]
                        self.onglets[compte] = tab
        except:
            try:
                self.browser_opened = False
                self.onglets = dict()
                self.driver.quit()
                # self.driver = connexion_chrome_1(self.preferences['profil'])
                # self.driver = connexion_chrome_2(self.preferences['profil'])
                self.driver = connexion_firefox(self.preferences['profil'])
                login_connect(self.driver, link, user, password, wait=wait, deja_charge=False, doubleauth=code)
                self.onglets[compte] = self.driver.window_handles[0]
                self.browser_opened = True
            except:
                pass

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

    def generer_mdp_modif(self):
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
            self.visible['generer_mdp'] = True
            self.input['generer_mdp'].config(show='')
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
            self.stringvar['generer_mdp'].set(self.mdp_gen)

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
        profil = self.stringvar['profil'].get()
        autoconnexion = self.stringvar['checkautoconnexion'].get()

        self.preferences['chiffres'] = chiffres
        self.preferences['lettresmin'] = mini
        self.preferences['lettresmaj'] = maj
        self.preferences['ponctuation'] = ponct
        self.preferences['cara_spe'] = cara
        self.preferences['no_similar'] = no_similar
        self.preferences['profil'] = profil

        if platform.system() != "Windows":
            self.preferences['profil_linux'] = profil
        else:
            self.preferences['profil_windows'] = profil

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
                    self.preferences['profil_linux'] + '\n' +
                    self.preferences['profil_windows'] + '\n' +
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
                    self.create_toplevel(500, 340, '', 'generer', 'conflit_donnees', 80, 15, compte=new_compte,
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
        self.create_label(self.generer_f, 'conflit', s, 0, 0, anchor='center', pady=(10, 10), columnspan=2)

        if 'radiochoix' not in self.stringvar.keys():
            self.add_radiobutton(self.generer_f, 'choix', 'Ignorer', 1, 0, 'ignorer', default=True,
                                 commande=partial(self.hide_entry), columnspan=2)
        else:
            self.add_radiobutton(self.generer_f, 'choix', 'Ignorer', 1, 0, 'ignorer',
                                 commande=partial(self.hide_entry), columnspan=2)
        self.add_radiobutton(self.generer_f, 'choix', 'Écraser', 2, 0, 'ecraser',
                             commande=partial(self.hide_entry), columnspan=2)
        self.add_radiobutton(self.generer_f, 'choix', 'Renommer', 3, 0, 'renommer',
                             commande=partial(self.show_entry, compte), columnspan=2)

        self.create_button(self.generer_f, 'conflit', 'Valider', 5, 0, padx=(0, 10), pady=(10, 0),
                           commande=partial(self.verif_conflit, self.generer_f))
        self.create_button(self.generer_f, 'annnuler_conflit', 'Annuler', 5, 1, pady=(10, 0),
                           commande=partial(self.generer_f.destroy))

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
                    self.input['nouveau_nom']['fg'] == self.input['nouveau_nom'].placeholder_color):

                if self.input['nouveau_nom']['fg'] == self.input['nouveau_nom'].placeholder_color:
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
                                          fg='red', user=True, pady=(10, 0), columnspan=2)
                except:
                    self.create_label(fenetre, 'conflit_error', s, 6, 0, anchor='center',
                                      fg='red', user=True, pady=(10, 0), columnspan=2)

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
                                     4, 0, '1', '0', '0', pady=(5, 10), columnspan=2)
        except:
            try:
                self.add_checkbutton(self.generer_f, 'idem', 'Faire pour tous',
                                     4, 0, '1', '0', '0', pady=(5, 10), columnspan=2)
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
                self.add_input(self.generer_f, 'nouveau_nom', 4, 0, sticky='news', focus=True, pady=(10, 10), padx=10,
                               placeholder='Nouveau nom', columnspan=2)
                self.stringvar['nouveau_nom'].set(f"{compte} ({i})")
                self.input['nouveau_nom'].convert_real_text()
        except:
            try:
                self.add_input(self.generer_f, 'nouveau_nom', 4, 0, sticky='news', focus=True, pady=(10, 10), padx=10,
                               placeholder='Nouveau nom', columnspan=2)
                self.stringvar['nouveau_nom'].set(f"{compte} ({i})")
                self.input['nouveau_nom'].convert_real_text()
            except:
                pass

    def creer_mdp(self, *args):
        """
        Fonction qui récupère les données après validation de création,
        vérifie la validité de ces données et les enregistre
        """
        mdp = self.stringvar['generer_mdp'].get()
        username = self.stringvar['username'].get()
        link = self.stringvar['link'].get()
        wait = self.stringvar['checklong'].get()
        prio = self.stringvar['checkprio'].get()
        doubleauth = self.stringvar['checkdoubleauth'].get()

        if lien_valide(link):
            link = doubleauth + wait + prio + link
        else:
            link = ''

        mdp_e = f"{mdp}{username}{len(username):02}{link}{len(link):03}"
        compte = self.stringvar['nom_compte'].get().strip()
        if compte == '':
            self.stringvar['nom_compte'].set('Veuillez saisir un compte')
        elif len(username) > 99:
            self.stringvar['username'].set('Nom trop long')
        else:
            mdp_e_chiffre = encrypt(mdp_e, self.mdp_maitre)
            compte_e_chiffre = encrypt(compte, self.mdp_maitre)
            if compte not in self.donnees.keys():  # ecriture directe à la fin du fichier
                with open(self.f, "a") as fichier:
                    fichier.write(f"{compte_e_chiffre}\n")
                    fichier.write(f"{mdp_e_chiffre}\n")
                    self.donnees[compte] = mdp_e_chiffre
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
        mdp = self.stringvar['generer_mdp'].get()
        username = self.stringvar['username'].get()
        link = self.stringvar['link'].get()
        wait = self.stringvar['checklong'].get()
        prio = self.stringvar['checkprio'].get()
        doubleauth = self.stringvar['checkdoubleauth'].get()

        if lien_valide(link):
            link = doubleauth + wait + prio + link
        else:
            link = ''

        if len(username) > 99:
            self.stringvar['username'].set('Nom trop long')
        else:
            mdp_e = f"{mdp}{username}{len(username):02}{link}{len(link):03}"
            mdp_e_chiffre = encrypt(mdp_e, self.mdp_maitre)

            with open(self.f, "r") as fichier:
                donnees_s = fichier.readlines()
                index = index_liste(self.donnees_liste, f"{compte}\n")
                donnees_s = donnees_s[:index + 1] + [f"{mdp_e_chiffre}\n"] + donnees_s[index + 2:]
                self.donnees_liste = self.donnees_liste[:index + 1] + [f"{mdp_e_chiffre}\n"] + self.donnees_liste[index + 2:]
                donnees_s = ''.join(donnees_s)
            with open(self.f, "w") as fichier:
                fichier.write(donnees_s)
            self.donnees[compte] = mdp_e_chiffre
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

    def confirmation_sup(self, compte, *args):
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
        self.frame[compte].destroy()
        self.confirmer_f.destroy()
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
        self.create_label(self.generer_f, 'ancien_mdp', 'Ancien mot de passe :', 0, 0, sticky='ew', anchor='w')
        self.add_input(self.generer_f, 'ancien_mdp', 1, 0, sticky='news', focus=True, show=False)
        self.create_button(self.generer_f, 'voir_a', '', 1, 1, image=self.oeil,
                           width=25, height=25, commande=partial(self.voir, 'ancien_mdp'))

        self.create_label(self.generer_f, 'nouv_mdp', 'Nouveau mot de passe :', 2, 0,
                          sticky='ew', anchor='w', pady=(20, 0))
        self.add_input(self.generer_f, 'nouv_mdp', 3, 0, sticky='news', show=False)
        self.create_button(self.generer_f, 'voir_n', '', 3, 1, image=self.oeil,
                           width=25, height=25, commande=partial(self.voir, 'nouv_mdp'))

        self.create_label(self.generer_f, 'nouv_mdp_c', 'Confirmation mot de passe :', 4, 0,
                          sticky='ew', anchor='w', pady=(20, 0))
        self.add_input(self.generer_f, 'nouv_mdp_c', 5, 0, sticky='news', show=False)
        self.create_button(self.generer_f, 'voir_c', '', 5, 1, image=self.oeil,
                           width=25, height=25, commande=partial(self.voir, 'nouv_mdp_c'))

        self.create_button(self.generer_f, 'confirmer', 'Confirmer', 6, 0, columnspan=2,
                           commande=partial(self.changer_mdp_user), pady=(15, 10))
        self.create_button(self.generer_f, 'annuler', 'Annuler', 7, 0, columnspan=2,
                           commande=partial(self.generer_f.destroy))

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

        self.create_label(self.generer_f, 'explication', s, 0, 0, columnspan=2, pady=(0, 25),
                          font=("arial", 20, "bold"))

        self.create_label(self.generer_f, 'mdp_user', 'Mot de passe :', 1, 0, sticky='ew', anchor='w')
        self.add_input(self.generer_f, 'mdp_user', 2, 0, sticky='news', focus=True, show=False)
        self.create_button(self.generer_f, 'voir_a', '', 2, 1, image=self.oeil,
                           width=25, height=25, commande=partial(self.voir, 'mdp_user'))

        self.create_button(self.generer_f, 'confirmer', 'Confirmer', 3, 0, columnspan=2,
                           commande=partial(self.changer_mdp_maitre), pady=(15, 10))
        self.create_button(self.generer_f, 'annuler', 'Annuler', 4, 0, columnspan=2,
                           commande=partial(self.generer_f.destroy))

    def changer_mdp_user(self):
        """
        Fonction qui change le mot de passe de l'utilisateur
        """
        if self.stringvar['nouv_mdp'].get() != self.stringvar['nouv_mdp_c'].get():
            self.visible['nouv_mdp_c'] = True
            self.stringvar['nouv_mdp'].set('')
            self.stringvar['nouv_mdp_c'].set('Confirmation non identique')
            self.input['nouv_mdp_c'].config(show='')
        elif len(self.stringvar['nouv_mdp'].get()) < 10:
            self.visible['nouv_mdp'] = True
            self.stringvar['nouv_mdp'].set('10 caractères minimum')
            self.stringvar['nouv_mdp_c'].set('')
            self.input['nouv_mdp'].config(show='')
        elif not get_master_password(self.stringvar['ancien_mdp'].get()):
            self.visible['ancien_mdp'] = True
            self.stringvar['ancien_mdp'].set('Mot de passe incorrect')
            self.input['ancien_mdp'].config(show='')
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
        if not get_master_password(self.stringvar['mdp_user'].get()):
            self.visible['mdp_user'] = True
            self.stringvar['mdp_user'].set('Mot de passe incorrect')
            self.input['mdp_user'].config(show='')
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
            self.donnees_liste = donnees_liste(self.mdp_maitre)
            self.donnees = donnees_dico(self.donnees_liste)
            self.generer_f.destroy()
            threading.Thread(target=self.get_links).start()

    def creer_mdp_maitre(self, *args):
        """
        Fonction qui initialise un mot de passe maitre
        """
        if self.stringvar['mdp_accueil'].get() != self.stringvar['mdp_accueil_conf'].get():
            self.visible['mdp_accueil'] = True
            self.stringvar['mdp_accueil_conf'].set('')
            self.stringvar['mdp_accueil'].set('Confirmation non identique')
            self.input['mdp_accueil'].config(show='')
        elif len(self.stringvar['mdp_accueil'].get()) < 10:
            self.visible['mdp_accueil'] = True
            self.stringvar['mdp_accueil'].set('10 caractères minimum')
            self.stringvar['mdp_accueil_conf'].set('')
            self.input['mdp_accueil'].config(show='')
        else:
            self.mdp_user = self.stringvar['mdp_accueil'].get()
            self.mdp_maitre = create_master_password(self.mdp_user)
            self.accueil.destroy()

    def build_tout_supprimer(self):
        """
        Fonction qui construit la fenêtre de suppression de toutes les données
        """
        self.create_label(self.generer_f, 'avertissement', 'Cette opération effacera\ntoutes vos données', 0, 0,
                          columnspan=2, pady=(0, 25), font=("arial", 20, "bold"))

        self.create_label(self.generer_f, 'mdp_l', "Mot de passe :", 1, 0, sticky='w', pady=(0, 10))
        self.add_input(self.generer_f, 'mdp', 2, 0, width=43, focus=True, show=False, sticky='news')
        self.create_button(self.generer_f, 'voir_mdp', '', 2, 1, commande=partial(self.voir, 'mdp'), image=self.oeil)

        self.create_label(self.generer_f, 'confirmer_l', 'Tapez "CONFIRMER" :', 3, 0, sticky='w', pady=(30, 10))
        self.add_input(self.generer_f, 'confirmer', 4, 0, columnspan=2, sticky='news')
        self.input['confirmer'].config(font=('arial', 20))
        self.create_label(self.generer_f, 'eq', '', 4, 2, width=0)
        self.label['eq'].config(height=2)

        self.create_button(self.generer_f, 'valider_supp', 'Confirmer', 5, 0, columnspan=2,
                           commande=partial(self.tout_supprimer_exe), bg='green', fg='white',
                           abg='#009020', afg='white', pady=(30, 0), height=2)

    def tout_supprimer_exe(self):
        """
        Fonction qui vérifie si le mot de passe et les validations sont corrects et supprime toutes les données
        """
        if not self.stringvar['confirmer'].get() == 'CONFIRMER':
            self.visible['mdp'] = True
            self.stringvar['mdp'].set('Confirmation incorrecte')
            self.input['mdp'].config(show='')
        elif not get_master_password(self.stringvar['mdp'].get()):
            self.visible['mdp'] = True
            self.stringvar['mdp'].set('Mot de passe incorrect')
            self.input['mdp'].config(show='')
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


class Fenetre(Tk):
    def __init__(self, la=100, h=100, texte=""):

        Tk.__init__(self)

        self.title(texte)

        self.style = ttkthemes.ThemedStyle()

        largeur_ecran = self.winfo_screenwidth()
        hauteur_ecran = self.winfo_screenheight()
        pos_x = largeur_ecran // 2 - la // 2
        pos_y = hauteur_ecran // 2 - h // 2
        geometry = f"{la}x{h}+{pos_x}+{pos_y}"
        self.geometry(geometry)


class EntryWithPlaceholder(Entry):
    def __init__(self, master, textvariable, width=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master, textvariable=textvariable, width=width)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.refocus_launcher)
        self.bind("<Button-1>", self.refocus_launcher)
        self.bind("<Key>", self.update)

        self.put_placeholder()

    def convert_real_text(self):
        self['fg'] = self.default_fg_color
        self.icursor('end')

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self.icursor(0)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        try:
            if self['fg'] == self.placeholder_color and self.get() != self.placeholder:
                self.delete('1', 'end')
                self['fg'] = self.default_fg_color
        except TclError:
            pass

    def foc_out(self, *args):
        try:
            if not self.get():
                self.put_placeholder()
        except TclError:
            pass

    def refocus_launcher(self, *args):
        threading.Thread(target=self.refocus).start()

    def refocus(self, *args):
        time.sleep(0.001)
        if self['fg'] == self.placeholder_color and self.get() == self.placeholder:
            self.delete('0', 'end')
            self.insert(0, self.placeholder)
            self.icursor(0)

    def update(self, *args):
        threading.Thread(target=self.update_placeholder).start()

    def update_placeholder(self, *args):
        try:
            time.sleep(0.001)
            self.foc_in()
            self.foc_out()

            if self['fg'] == self.placeholder_color:
                self.icursor(0)
        except TclError:
            pass
