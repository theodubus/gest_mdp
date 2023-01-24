import pyautogui
import time
import pyperclip
import platform
import psutil
from shutil import which
import subprocess

def get_window_titles():
    wmctrl = subprocess.Popen(['wmctrl', '-lx'], stdout=subprocess.PIPE)
    awk = subprocess.Popen(['awk', "{print $3}"], stdin=wmctrl.stdout, stdout=subprocess.PIPE)
    stdout, _ = awk.communicate()
    windows = stdout.decode().strip().split('\n')
    return windows


if platform.system() == "Windows":
    from pywinauto.keyboard import send_keys, Application

def app_installed(name):
    """Vérifie si une application est installée"""
    return which(name) is not None

def is_open(app_name):
    """
    Fonction qui vérifie si une application est ouverte
    """
    if not app_name in (i.name() for i in psutil.process_iter()):
        return False

    try:
        if platform.system() != "Windows":
            if "authy" in get_window_titles():
                return True
        else:
            Application(backend="uia").connect(title_re=".*Authy.*")
        return True
    except Exception as e:
        return False

def open_app(app_name):
    """
    Fonction qui ouvre une application
    """
    time.sleep(0.5)
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write(app_name)
    time.sleep(0.5)
    pyautogui.press('enter')


def get_authy_code(account):
    """
    Fonction qui récupère le code d'authentification d'un compte
    """
    if not app_installed("authy"):
        return None

    # On ouvre l'application Authy
    open_app('authy')

    attempts = 0
    while not is_open('authy') and attempts < 15:
        time.sleep(2)
        attempts += 1

    if attempts == 15:
        return None

    attempts = 0
    test = ''
    while test != account and attempts < 20:
        if not is_open('authy'):
            return None
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
