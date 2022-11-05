import pyautogui
import time
import pyperclip
import platform


def open_app(app_name):
    """
    Fonction qui ouvre une application
    """
    time.sleep(0.5)
    pyautogui.press('win')
    time.sleep(0.5)
    pyautogui.write(app_name)
    time.sleep(0.5)
    pyautogui.press('enter')


def get_authy_code(account):
    """
    Fonction qui récupère le code d'authentification d'un compte
    """

    # On ouvre l'application Authy
    open_app('authy')
    time.sleep(0.5)
    verif = None
    attempts = 0

    # On vérifie que l'app est bien ouverte grâce à la présence d'un bouton distinctif
    # L'application peut mettre du temps à s'ouvrir,
    # après un certain nombre d'essais, on demande à l'utilisateur s'il veut continuer.
    while verif is None:
        if attempts > 10:
            reponse = pyautogui.confirm(text="L'application semble ne pas charger, continuer d'essayer ?",
                                        title='Erreur', buttons=['Oui', 'Annuler'])
            if reponse == 'Annuler':
                pyautogui.hotkey('alt', 'f4')
                return None
            else:
                attempts = 0
        if platform.system() != "Windows":
            verif = pyautogui.locateCenterOnScreen('images/verif_linux.png')
        else:
            verif = pyautogui.locateCenterOnScreen('images/verif_win.png')
        if verif is None:
            time.sleep(1)
            attempts += 1

    time.sleep(0.25)

    # On efface le texte de la barre de recherche (si l'app déjà était ouverte, il y a peut-être du texte)
    pyautogui.hotkey('ctrl', 'backspace')
    time.sleep(0.25)

    # On écrit le nom du compte dans la barre de recherche
    pyautogui.write(account)
    time.sleep(0.25)

    # On ne sait pas où se trouve la souris, ni la position absolue sur l'écran du compte, on se déplace donc
    # au point de repère vu précédemment.
    pyautogui.moveTo(verif)
    time.sleep(0.25)

    # On se déplace jusqu'au compte et on clique dessus
    pyautogui.move(0, 75)
    time.sleep(0.25)
    pyautogui.click()
    time.sleep(0.25)

    # On se déplace jusqu'au bouton "copier"
    if platform.system() != "Windows":
        pyautogui.move(25, 455)
    else:
        pyautogui.move(20, 530)
    time.sleep(0.25)

    # On vide le presse-papier
    pyperclip.copy('')

    # On clique sur le bouton "copier"
    pyautogui.click()

    # On récupère le code d'authentification
    code = pyperclip.paste()

    # Si le presse-papier est vide, le compte n'existe pas (ou autre erreur)
    if code == '':
        code = None
    time.sleep(0.25)

    # On ferme l'application
    pyautogui.hotkey('alt', 'f4')

    # On retourne le code d'authentification plutôt que de le laisser dans le presse-papier,
    # l'utilisateur pourrait copier autre chose et donc le code d'authentification serait perdu.
    # Ceci permet également de gérer correctement le cas où le compte n'a pas été trouvé.
    return code
