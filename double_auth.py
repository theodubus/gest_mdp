import pyautogui
import time
import pyperclip
import platform

if platform.system() == "Windows":
    from pywinauto.keyboard import send_keys


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
    time.sleep(4)

    # On essaye de taper le nom du compte, si on y arrive, l'application est ouverte
    # Pour ne pas tourner en boucle, on essaye pendant un peu plus de 20 secondes,
    # après quoi on renvoie None si l'application n'a pas été ouverte.
    attempts = 0
    test = ''
    while test != account and attempts < 20:
        pyperclip.copy('')
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.25)
        pyautogui.press('backspace')
        time.sleep(0.25)
        pyautogui.write(account)
        time.sleep(0.25)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.25)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.25)
        test = pyperclip.paste()
        if test != account:
            attempts += 1
            time.sleep(1)

    if attempts == 20:
        return None

    time.sleep(0.25)
    if platform.system() != "Windows":
        pyautogui.press('enter')
    else:
        # press enter ne fonctionne pas sur authy sous windows ¯\_(ツ)_/¯
        send_keys('{ENTER}')

    time.sleep(0.25)

    # On se déplace jusqu'au centre du code d'authentification
    size = pyautogui.size()

    # Cas particulier de deux moniteurs qui sont vu par le programme comme un seul
    if size[0] > 3000 and size[1] <= 1080:
        pyautogui.moveTo(size[0] / 4, size[1] / 2 - 30)
    else:
        pyautogui.moveTo(size[0] / 2, size[1] / 2 - 30)

    # triple click
    pyautogui.click(clicks=3, interval=0.25)

    # On vide le presse-papier
    pyperclip.copy('')

    # On copie le code d'authentification
    pyautogui.hotkey('ctrl', 'c')

    # On récupère le code d'authentification
    code = pyperclip.paste()

    # Si le presse-papier est vide, le compte n'existe pas (ou autre erreur)
    if code == '':
        code = None
    else:
        code = code.replace(' ', '')  # On enlève l'espace central
    time.sleep(0.25)

    # On ferme l'application
    pyautogui.hotkey('alt', 'f4')

    # On retourne le code d'authentification plutôt que de le laisser dans le presse-papier,
    # l'utilisateur pourrait copier autre chose et donc le code d'authentification serait perdu.
    # Ceci permet également de gérer correctement le cas où le compte n'a pas été trouvé.
    return code
