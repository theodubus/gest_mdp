from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchWindowException as closed_tab


def connexion_firefox(profil):
    """
    Connexion à firefox, renvoie le driver
    """
    options = FirefoxOptions()
    if profil != '':
        options.add_argument('-profile')
        options.add_argument(profil)
    options.set_preference('dom.webdriver.enabled', False)
    options.set_preference('useAutomationExtension', False)
    driver = webdriver.Firefox(options=options)
    return driver


def connexion_chrome_1(profil):
    """
    Connexion à chrome, renvoie le driver
    """
    driver_location = '/snap/bin/chromium.chromedriver'  # changer chemins sous Windows
    binary_location = '/usr/bin/chromium-browser'
    options = webdriver.ChromeOptions()
    options.binary_location = binary_location
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    if profil != '':
        options.add_argument(fr"--user-data-dir={profil}")
    options.add_argument(r'--profile-directory=Default')
    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=options)
    return driver


def connexion_chrome_2(profil):
    """
    Connexion à chrome (alternative), renvoie le driver
    """
    driver_location = '/snap/bin/chromium.chromedriver'  # changer chemins sous Windows
    options = ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if profil != '':
        options.add_argument(fr"--user-data-dir={profil}")
    options.add_argument(r'--profile-directory=Default')
    driver = webdriver.Chrome(service=Service(driver_location), options=options)
    return driver


def user_login(driver, username):
    """
    Fonction qui cherche le champ de login et le remplit
    """
    logins = ['//input[@type="text"]', '//input[@type="email"]']
    success = False
    for login in logins:
        try:
            driver.find_element(By.XPATH, login).send_keys(username)
            success = True
            break
        except:
            pass
    return success


def password_login(driver, password):
    """
    Fonction qui cherche le champ de mot de passe et le remplit
    """
    success = False
    try:
        driver.find_element(By.XPATH, '//input[@type="password"]').send_keys(password)
        success = True
    except:
        pass
    return success


def is_login_page(driver):
    """
    Fonction qui vérifie si la page est une page de login
    """
    success = False
    try:
        driver.find_element(By.XPATH, '//input[@type="password"]')
        success = True
    except:
        pass
    return success


def button_click(driver):
    """
    Fonction qui cherche le bouton de connexion et le clique
    """
    buttons = ['//button[@type="submit"]', '//button[@type="button"]', 'input[type="submit"]']
    success = False

    try:
        element = driver.switch_to.active_element
        element.send_keys(Keys.ENTER)
        success = True
    except:
        pass

    if not success:
        for button in buttons:
            try:
                element = driver.find_element(By.XPATH, button)
                try:
                    element.submit()
                    success = True
                    break
                except:
                    try:
                        element.click()
                        success = True
                        break
                    except:
                        try:
                            element.send_keys(Keys.ENTER)
                            success = True
                            break
                        except:
                            pass

                break
            except:
                pass
    return success


def login_connect(driver, link, username, password, wait=False, deja_charge=False):
    """
    Fonction qui se connecte à un site
    """
    if not deja_charge:
        driver.get(link)
        if driver.current_url != link:
            return False

    if not is_login_page(driver):
        return False

    if wait:
        sleep(5)

    if not user_login(driver, username):
        if not password_login(driver, password):
            return False
        return button_click(driver)

    if not password_login(driver, password):
        if not button_click(driver):
            return False
        sleep(2)
        if not password_login(driver, password):
            return False

    return button_click(driver)


def new_page(driver, compte, fenetre):
    """
    Fonction qui ouvre un nouvel onglet
    """
    if fenetre is False:
        driver.switch_to.window(driver.window_handles[0])
        driver.execute_script(f"window.open('about:blank','{compte}');")
        driver.switch_to.window(compte)
        return True

    try:
        driver.switch_to.window(fenetre)
        return False
    except:
        driver.switch_to.window(driver.window_handles[0])
        driver.execute_script(f"window.open('about:blank','{compte}');")
        driver.switch_to.window(compte)
        return True
