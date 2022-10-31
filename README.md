# gest_mdp
Gestionnaire de mots de passe avec connexion automatique

## Installation
```bash
git clone https://github.com/4igle/gest_mdp.git
cd gest_mdp
pip install -r requirements.txt
```
Si vous voulez également profiter de la fonctionnalité
de connexion automatique, il faut installer un driver
pour votre navigateur. Pour cela, rendez-vous sur
[la page de selenium](https://selenium-python.readthedocs.io/installation.html#drivers)
et téléchargez le driver correspondant à votre navigateur.

Notez que seuls les navigateurs Chrome et Firefox sont supportés.
Vous pouvez cependant ajouter vos propres fonctions de connexion
en les ajoutant dans le fichier `gest_mdp/web.py`.

### Utilisation de Chrome
Par défaut, le navigateur utilisé est Firefox, mais vous pouvez
utiliser Chrome en commentant les deux lignes appelant `connexion_firefox()`
et en décommentant les deux lignes appelant `connexion_chrome_1()` ou
`connexion_chrome_2()` (Si une des deux fonctions de connexion ne fonctionne
pas, essayez l'autre). Vous devez également renseigner le chemin vers
le driver dans la fonction `connexion_chrome_1()` ou `connexion_chrome_2()`
dans le fichier `gest_mdp/web.py`.


## Utilisation

```bash
python gest.py
```
Lors de la première utilisation, vous devez saisir votre mot de passe
maître qui servira à chiffrer vos mots de passe.

### Ajouter un mot de passe

Vous pouvez ensuite stocker des nouveaux mots de passe en cliquant
sur le bouton `+` ou dans `Options > Données > Nouveau compte`. Seul le nom du compte
et le mot de passe sont obligatoires. La case `Lien` correspond au
lien vers la page de connexion si vous souhaitez mettre en place la
connexion automatique pour ce compte (incluez le lien entier avec https://).
La case `prio` permet de définir une priorité pour la connexion automatique
(ex : si vous avez plusieurs comptes Amazon ou autre).

La case `long` permet de mettre un délai si un site est particulièrement
long à charger, la connexion automatique peut échouer dans ce cas si
on ne rajoute pas de délai (ex: openclassrooms).

Les cases en dessous le champ de mot de passe correspondent aux
caractères à inclure ou non dans le mot de passe.

La case `no similar` permet d'éviter les caractères similaires (ex : 0 et O)

Si vous ne souhaitez pas un mot de passe aléatoire,
il est possible de le saisir manuellement.

Si vous modifiez les paramètres de génération de mot de passe
(changement de taille, changement des caractères inclus), n'oubliez
pas de cliquer sur le bouton `Générer` pour générer un nouveau mot de
passe correspondant à vos critères.

### Modifier un mot de passe
Pour modifier un mot de passe, cliquez sur le bouton en forme de crayon
à côté du compte que vous souhaitez modifier. La modification suit les
mêmes règles que l'ajout.

### Supprimer un mot de passe
Pour supprimer un mot de passe, cliquez sur le bouton en forme de poubelle
à côté du compte que vous souhaitez supprimer.

### Générer un mot de passe sans l'enregistrer
Si vous souhaitez générer un mot de passe sans l'enregistrer, allez dans
`Options > Générer`. Les paramètres de génération de mot de passe sont
les mêmes que pour l'ajout d'un mot de passe.

### Connexion automatique
N'oubliez pas de spécifier le dossier du profil de votre navigateur
depuis `Options > Profil > Modifier Préférences` si vous souhaitez utiliser
votre profil habituel pour la connexion automatique.

Trouver le dossier du profil de votre navigateur (dans la barre d'adresse) :
- Firefox : `about:support`
- Chrome : `chrome://version/`

Pour utiliser la connexion automatique, lancer un navigateur contrôlé
par selenium, cliquez sur le bouton en forme de globe d'un compte
pour lequel vous avez spécifié un lien de connexion. Si vous avez
spécifié votre profil, veillez à ce que le navigateur soit fermé avant
de lancer la connexion automatique, la connexion automatique ne supporte
pas plusieurs navigateurs avec le même profil.

Pour ouvrir un autre site internet, vous pouvez cliquer soit sur le bouton
en forme de globe d'un autre compte, soit ouvrir un nouvel onglet et
arriver sur la page de connexion, le programme détectera automatiquement
que vous êtes sur une page de connexion et vous connectera automatiquement.

Notez que cette détéction automatique ne fonctionne que dans le
dernier onglet ouvert.

Si vous souhaitez désactiver temporairment la connexion automatique,
vous pouvez décocher la case `autoconnection (temp)`.

### Préférences
Vous pouvez modifier les préférences depuis `Options > Profil > Modifier Préférences`.
En plus de spécifier le dossier du profil de votre navigateur, vous pouvez
décider d'activer ou non par défaut la connexion automatique, d'inclure
par défaut certains types de caractères dans les mots de passe générés, etc.

### Modifier le mot de passe utilisateur
Vous pouvez modifier votre mot de passe depuis `Options > Profil > Sécurité > Modifier le mot de passe utilisateur`.

### Modifier la clé de chiffrement
Vous pouvez chiffrer vos données avec une nouvelle clé de chiffrement depuis `Options > Profil > Sécurité > Changer de clé de chiffrement`.
Cette opération peut prendre du temps étant donné qu'elle nécessite la réécriture de toutes les
données (déchiffrement avec l'anncienne clé de chiffrement, chiffrement avec la nouvelle clé).
Attendez-vous à une attente de quelques secondes pour une centaine de comptes.

### Supprimer toutes les données
Vous pouvez supprimer toutes les données depuis `Options > Profil > Sécurité > Supprimer toutes les données`.

### Copier un mot de passe ou un nom d'utilisateur
Vous pouvez copier un mot de passe ou un nom d'utilisateur dans le presse-papier
en cliquant sur le bouton en forme de presse-papier à côté du compte.

### Voir un mot de passe
Vous pouvez voir un mot de passe en cliquant sur le bouton en forme d'œil
à côté du mot de passe.

### Chercher un compte
Pour chercher un compte, tapez le nom du compte recherché dans la barre de
recherche.

### Exporter les données
Toutes vos données sont stockées dans le dossier `.data/` du répertoire
de l'application. Vous pouvez donc les exporter en copiant ce dossier.
Dans ce dossier, les fichiers `master_password.txt`, `salt.txt`, `store.txt` et
`preferences.txt` contiennent respectivement votre clé de chiffrement chifrée, votre salt,
vos données chiffées et vos préférences.

Vous pouvez même synchroniser vos données sur plusieurs appareils,
pour cela, il faut que vous ayez installé l'application sur tous les
appareils que vous souhaitez synchroniser. Pour ce qui est des données, vous
pouvez synchroniser le dossier `.data/` sur un service de stockage entre
vos différents appareils.

Vous pouvez également récupérer vos données en clair au format JSON depuis
`Options > Données > Exporter les données`. Attention, le fichier profuit contiendra
toutes vos données non chiffrées.

### Importer les données
Vous pouvez importer des données depuis `Options > Données > Importer des données`.
Le fichier doit être au format JSON et avoir été produit par l'application,
si les données ne sont pas au bon format, l'application ignore le fichier.

Si un compte avec le même nom existe déjà, l'application vous laisse le choix
d'écraser la version déjà existante, d'ignorer la version en cours d'importation,
ou de renommer la version en cours d'importation. Si vous choisissez une des
deux premières options, vous avez la possibilité d'appliquer le même choix
pour tous les autres comptes qui suivent. Si durant l'import vous ouvrez une
autre fenêtre de l'application, appuyer sur `Annuler` ou alors fermez la
boîte de dialogue, l'importation dans son entièreté sera annulée.

### Connexion persistante
Sous Linux, la connexion au logiciel sera persistante, vous n'aurez pas besoin
de vous reconnecter à chaque fois que vous lancerez l'application, mais uniquement
au premier lancement après un redémarrage de l'ordinateur. Vous tout de même
choisir de vérouiller l'application en vous déconnectant depuis `Options > Se déconnecter`.

## Sécurité
La sécurité des données suit les mêmes principes que beaucoup d'autres logiciels similaires.
On dérive le mot de passe de l'utilisateur (avec un salt) avec une fonction
coûtant beaucoup de temps (PBKDF2 avec 1M d'itérations) pour obtenir une clé de chiffrement, une clé "dérivée".
(Voir [recommandation officielle](https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet)
du module `cryptography`).

Cette clé pourrait être directement utilisée pour chiffrer les données,
mais cela aurait pour conséquence de devoir déchiffrer et rechiffrer toutes les données
à chaque fois que l'utilisateur change son mot de passe. Pour éviter cela, on utilise comme clé
de chiffrement une clé aléatoire générée par le module `cryptograpy` et on la chiffre avec la clé "dérivée".

Les fonctions liées à la sécurité sont implémentées dans le fichier `security.py`.

## Accès au logiciel
### Linux
+ Lancer directement le programme depuis un terminal :
`python3 /path/to/gest_mdp/main.py`


+ Ajouter les droits d'exécution à `main.py`, puis créer un raccourci clavier contenant la commande `/path/to/gest_mdp/main.py`


+ Utiliser le fichier `gest.desktop` fourni dans le dossier `additional_resources/`.
Il faut donner les droits d'exécution aux fichiers `gest.desktop` et `main.py`. Ensuite, il faut modifier les
chemins dans le fichier `gest.desktop` pour qu'ils correspondent à votre installation. Enfin, il faut copier le fichier
dans le dossier `~/.local/share/applications/`. Cette solution rendra l'application disponible dans la liste de vos
applications.

### Windows
+ Lancer directement le programme depuis un terminal :
`python C:\path\to\gest_mdp\main.py`

+ Utiliser le fichier `gest.bat` fourni dans le dossier `additional_resources/`.
Il faut modifier les chemins dans le fichier `gest.bat` pour qu'ils correspondent
à votre installation. Vous pouvez ensuite soit utiliser directement ce fichier,
soit créer un raccourci vers ce fichier, ce qui vous permettra de définir une
icône. Une image au bon format, `logo.ico` est également fournie dans le dossier
`additional_resources/`.
