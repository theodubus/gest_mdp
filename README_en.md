# gest_mdp
Password manager with automatic connection

<table align="right">
  <tr><td><a href="README.md"><img src="https://github.com/Th3o-D/Th3o-D/blob/main/images/fr-flag.png" height="13"> Français</a></td></tr>
  <tr><td><a href="README_en.md"><img src="https://github.com/Th3o-D/Th3o-D/blob/main/images/us-flag.png" height="13"> English</a></td></tr>
</table>

<details>
<summary><b> 🆕 - New features</b></summary><br>

### Last update 🔥

New technique for autocompletion: the software now uses an
extension for autocompletion. This extension communicates with a
local server managed by the application. The extension detects
login pages and automatically fills in the fields. The server,
in turn, communicates login information to the extension. This
new technique has the advantage of solving many problems that
were present before with Selenium, such as:
+ the need to launch the browser in a special mode from the software
+ autocompletion that only worked in the last opened tab
+ the inability to open multiple instances of the browser
+ issues with entering accented characters
+ certain sites refusing to work due to detection of a browser in robot mode
+ manual management of sites that take a long time to load with the "wait" option
+ infinite loop in case of incorrect password, causing the software to try to connect indefinitely.

With this improvement, all these problems are now a thing of the
past. The "wait" option has become unnecessary and has been removed
and replaced with the "submit" option. This option allows you
to decide on a per-site basis whether you want the extension to
automatically submit the login form or just fill in the fields.


The extension is available on the [Firefox store](https://addons.mozilla.org/en-US/firefox/addon/gest_mdp/).

### Other updates 🎉

+ Many bug fixes and stability improvements.
+ Many GUI improvements.
+ Added keyboard shortcuts.
+ Automatic generation of passwords when changing generation parameters.
+ Changed GUI from Tkinter to [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter):
#### Tkinter (before) :<br>
<img src="readme_documents/old.png" width="240" height="160"><br>
#### CustomTkinter (after) :<br>
<img src="readme_documents/new.png" width="240" height="160">

</details>


<details>
<summary><b> ‍⚙️ - Installation</b></summary><br>

```bash
git clone https://github.com/Th3o-D/gest_mdp.git
cd gest_mdp
pip install -r requirements.txt
```
If you also want to take advantage of the autocompletion feature,
you need to install an extension for your browser.
To do this, go to the [Firefox store](https://addons.mozilla.org/en-US/firefox/addon/gest_mdp/).

This extension is currently only available for Firefox, please
let me know if you would like me to make it available for
Chrome or any other browser.

#### Additional Operations for Linux
```bash
sudo apt install python3-tk
sudo apt install xclip
sudo apt install wmctrl
```

These operations may be necessary on Linux. The first line is to
install `Tkinter` in case the installation with pip fails.
The second line is to install `xclip`, which is used to copy
passwords to the clipboard. The last line is to install `wmctrl`,
which is used to view the names of open windows.
This feature is used for the retrieval of two-factor authentication
codes, it checks if Authy is open. If you do not plan to use this
feature, you can ignore this operation. Please note that I
only tested `wmctrl` on Gnome, it may not work on other desktop
environments.

</details>

<details>
<summary><b> 💻 - Software use</b></summary><br>

### Linux
+ <ins>Option 1 :</ins> Directly launch the program from a terminal :
`python3 /path/to/gest_mdp/main.py`


+ <ins>Option 2 :</ins> Add the execution rights to `main.py`, then create a keyboard shortcut containing the
command `/path/to/gest_mdp/main.py`


+ <ins>Option 3 :</ins> Use the `gest.desktop` file provided in the `additional_resources/` folder.
You must give execution rights to the files `gest.desktop` and `main.py`. Then you have to modify the
paths in the `gest.desktop` file so that they correspond to your installation. Finally, you have to copy the file
in the `~/.local/share/applications/` folder. This solution will make the application available in the list of your
applications.

### Windows
+ <ins>Option 1 :</ins> Directly launch the program from a terminal :
`python C:\path\to\gest_mdp\main.py`


+ <ins>Option 2 :</ins> Use the `gest.bat` file provided in the `additional_resources/` folder.
You have to modify the paths in the `gest.bat` file so that they correspond
to your installation. You can then either use this file directly,
either create a shortcut to this file, which will allow you to define a
icon. An image in the right format, `logo.ico` is also available in the folder
`additional_resources/`.

</details>

<details>
<summary><b> 🛠 - Features</b></summary><br>

### Add a password

You can store new passwords by clicking on the `Nouveau` button
or in `Options > Données > Nouveau compte`. Only the name of the account
and the password are compulsory.

+ The checkbox `Lien` correspond to the connection page for which you wish to
set up the automatic connection for this account (include the whole link with https://).

+ The checkbox `prio` allows you to define a priority for automatic connection
(e.g. if you have several Amazon accounts).

+ The checkbox `submit` allows you to decide whether you want the extension to
automatically submit the login form or just fill in the fields.

+ The checkbox `2FA` indicates that this account has a two factor authentification.

+ The checkboxes below the password field correspond to the characters
to include or not in the password.

+ The checkbox `no 0OIl` avoids similar characters (eg 0 and O).

If you don't want a random password,
it is possible to seize it manually.

If the generated password is not satisfactory, you can click on the `Générer` button
to generate a new one.

### Modify a password
To modify a password, click the pencil-shaped button next to the account you
want to modify. The modification follows the same rules as adding.

### Delete a password
To delete a password, click the bin button next to the account you want to delete.

### Generate a password without saving it
If you want to generate a password without saving it, go to
`Options > Générer`. Password generation parameters are
the same as for the addition of a password.

### Automatic connection
Don't forget to install the [extension](https://addons.mozilla.org/en-US/firefox/addon/gest_mdp/)
if you want to use autocompletion.

You can open a website by clicking on the globe
shaped button next to the account you want to open. Automatic
login will only work for websites for which you have specified a
login link.

You can temporarily disable automatic login by
unchecking the `autoconnexion` box. This will turn off the local
server managed by the application.

N'oubliez pas d'installer [l'extension](https://addons.mozilla.org/en-US/firefox/addon/gest_mdp/)
si vous souhaitez utiliser la connexion automatique.

Vous pouvez ouvrir un site internet en cliquant sur le bouton en forme de globe
à côté du compte que vous souhaitez ouvrir. La connexion automatique fonctionnera
uniquement pour les sites pour lesquels vous avez spécifié un lien de connexion.

Vous pouvez désactiver temporairement la connexion automatique en décochant la case 
`autoconnexion`. Cela aura pour effet d'éteindre le serveur local géré par l'application.

### Two factor authentification
If you have activated the double authentication for an account, the application
will try to open Authy, type the account name and recover the code, to enter it
in your browser thereafter. You must therefore have Authy installed and configured
on your computer. In addition, the name of the desired account must be the same
name in Authy. You can modify the function `get_authy_code` in `double_auth.py`
to use another double authentication application (very little code is to be modified).

### Preferences
You can change preferences from `Options > Profil > Modifier Préférences`.
In addition to specifying your browser's profile folder, you can decide whether to enable automatic login by default, whether to include certain character
types in generated passwords by default, and more.

### Change user password
You can change your password from `Options > Profil > Sécurité > Modifier le mot de passe utilisateur`.

### Change encryption key
You can encrypt your data with a new encryption key from `Options > Profil > Sécurité > Changer de clé de chiffrement`.
This operation can be time consuming as it requires all data to be rewritten
(decryption with old encryption key, encryption with new key).
Expect a wait of a few seconds for a hundred accounts.

### Delete all data
You can delete all data from `Options > Profil > Sécurité > Supprimer toutes les données`.

### Copy password or username
You can copy a password or username to the clipboard by clicking the
clipboard-shaped button next to the account.

### See a password
You can see a password by clicking the eye button next to the password.

### Find an account
To search for an account, type the name of the account you are looking for
in the search bar.

### Export data
All your data is stored in the `.data/` folder in the application's directory.
You can export it by copying this folder.
In this folder, the `master_password.txt`, `salt.txt`, `store.txt` and `preferences.txt`
files contain your encrypted encryption key, salt, encrypted data and preferences respectively.

You can even synchronize your data on several devices, for this you must have installed
the application on all the devices you want to synchronize.
As for data, you can synchronize the `.data/` folder on a storage service between your different devices.

You can also retrieve your plain data in JSON format from
`Options > Données > Exporter les données`. Please note that the file produced will
contain all your <b>unencrypted</b> data.

### Import data
You can import data from `Options > Données > Importer des données`.
The file must be in JSON format and must have been produced by the application,
if the data is not in the correct format, the application ignores the file.

If an account with the same name already exists, the application lets you choose
to overwrite the existing version, ignore the version being imported, or rename
the version being imported. If you choose one of the first two options, you have
the option of applying the same choice for all the other accounts that follow.
If during the import you open another window of the application, press `Annuler`
or close the dialog box, the import in its entirety will be cancelled.

### Persistent connection
Under Linux, the connection to the software will be persistent, you will not need
to reconnect each time you launch the application, but only at the first launch
after a restart of the computer. You can still choose to lock the application by
logging out from `Options > Se déconnecter`.

</details>

<details><summary><b> 🔒 - Security</b></summary><br>

Data security follows the same principles as many other similar software. We derive
the user's password (with a salt) with a time-consuming function
(PBKDF2-HMAC-SHA256 with 1M iterations) to obtain an encryption key, a "derived" key.
(See [official recommendation](https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet)
of the `cryptography` module).

This key could be directly used to encrypt the data, but this would have the
consequence of having to decrypt and re-encrypt all the data each time the user
changes his password. To avoid this, we use as encryption key a random key
generated by the `cryptography` module and we encrypt it with the "derived" key.

Security related functions are implemented in the [security.py](./security.py) file.

The power of computers is bound to increase in the coming years, so the password
derivation function might need to be changed. Here are different approaches that
could be used in the future if it becomes necessary:
+ PBKDF2-HMAC with SHA512 instead of SHA256
+ Increasing the number of iterations
+ Using a different derivation function (scrypt, argon2, bcrypt, etc.) depending
on which will be deemed most secure at the time
</details>

<details>
<summary><b> 🗄️ - Code structure</b></summary><br>

. \
├── 📄 [LICENSE](./LICENSE) \
├── 📄 [README.md](./README.md) \
├── 📄 [README_en.md](./README_en.md) \
├── 📄 [main.py](./main.py) \
├── 📄 [gest.py](./gest.py) \
├── 📄 [control.py](./control.py) \
├── 📄 [double_auth.py](./double_auth.py) \
├── 📄 [fonctions.py](./fonctions.py) \
├── 📄 [requirements.txt](./requirements.txt) \
├── 📄 [scroll.py](./scroll.py) \
├── 📄 [security.py](./security.py) \
├── 📄 [server.py](./server.py) \
├── 📁 [.data](./.data) \
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [master_password.txt](./.data/master_password.txt) \
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [preferences.txt](./.data/preferences.txt) \
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [salt.txt](./.data/salt.txt) \
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 📄 [store.txt](./.data/store.txt) \
├── 📁 [additional_resources](./additional_resources) \
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [gest.bat](./additional_resources/gest.bat) \
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 📄 [gest.desktop](./additional_resources/gest.desktop) \
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 📄 [logo.ico](./additional_resources/logo.ico) \
└── 📁 [images](./images) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [arial.ttf](./images/arial.ttf) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [copier.png](./images/copier.png) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [copier_disabled.png](./images/copier_disabled.png) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [crayon.png](./images/crayon.png) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [oeil.png](./images/oeil.png) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [oeil_a.png](./images/oeil_a.png) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [oeil_disabled.png](./images/oeil_disabled.png) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [poubelle.png](./images/poubelle.png) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── 📄 [web.png](./images/web.png) \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 📄 [web_disabled.png](./images/web_disabled.png)

</details>


https://user-images.githubusercontent.com/80580619/205418244-770941eb-55e1-4142-aa34-a60320952aa0.mp4

https://user-images.githubusercontent.com/80580619/205418250-b0da6ad6-a7ba-40d7-b791-51390fdfc477.mp4


<div align="right" style="display: flex">
    <img src="https://visitor-badge.glitch.me/badge?page_id=Th3o-D/gest_mdp&left_color=gray&right_color=blue" height="20"/>
    <a href="https://github.com/Th3o-D" alt="https://github.com/Th3o-D"><img height="20" style="border-radius: 5px" src="https://img.shields.io/static/v1?style=for-the-badge&label=CREATED%20BY&message=Th3o-D&color=1182c2"></a>
    <a href="LICENSE" alt="license"><img style="border-radius: 5px" height="20" src="https://img.shields.io/static/v1?style=for-the-badge&label=LICENSE&message=GNU+GPL+V3&color=1182c2"></a>
</div>
