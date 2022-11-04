import pyautogui
import time
import pyperclip


def open_app(app_name):
    time.sleep(0.5)
    pyautogui.press('win')
    time.sleep(0.5)
    pyautogui.write(app_name)
    time.sleep(0.5)
    pyautogui.press('enter')


def get_authy_code(account):
    open_app('authy')
    time.sleep(0.5)
    verif = None
    attempts = 0

    while verif is None:
        if attempts > 10:
            reponse = pyautogui.confirm(text="L'application semble ne pas charger, continuer d'essayer ?",
                                        title='Erreur', buttons=['Oui', 'Annuler'])
            if reponse == 'Annuler':
                break
            else:
                attempts = 0
        verif = pyautogui.locateCenterOnScreen('images/verif.png')
        if verif is None:
            time.sleep(0.25)
            attempts += 1

    time.sleep(0.25)
    pyautogui.hotkey('ctrl', 'backspace')
    time.sleep(0.25)
    pyautogui.write(account)
    time.sleep(0.25)
    pyautogui.moveTo(verif)
    time.sleep(0.25)
    pyautogui.move(0, -500)
    time.sleep(0.25)
    pyautogui.click()
    time.sleep(0.25)
    pyautogui.move(25, 435)
    time.sleep(0.25)
    pyperclip.copy('')
    pyautogui.click()
    code = pyperclip.paste()
    if code == '':
        code = None
    time.sleep(0.25)
    pyautogui.hotkey('alt', 'f4')
    return code









