import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_derived_password(user_password):
    """
    Fonction qui dérive le mot de passe de l'utilisateur
    """
    password = user_password.encode()

    with open('.data/salt.txt', 'rb') as fichier:
        salt = fichier.read()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000000,
    )
    derived_password = base64.urlsafe_b64encode(kdf.derive(password))
    return derived_password


def get_master_password(user_password):
    """
    Fonction qui récupère le mot de passe maître depuis le mot de passe de l'utilisateur
    Si le mot de passe de l'utilisateur est incorrect, la fonction renvoie False,
    Cette fonction peut donc servir à vérifier le mot de passe de l'utilisateur
    en plus de récupérer le mot de passe maître
    """
    if not user_password:
        return False

    derived_password = get_derived_password(user_password)
    fernet_derived_password = Fernet(derived_password)
    with open('.data/master_password.txt', 'rb') as fichier:
        encrypted_master_password = fichier.read()
    try:
        return str(fernet_derived_password.decrypt(encrypted_master_password).decode())
    except:
        return False


def create_master_password(user_password, master_password=None):
    """
    Fonction qui crée un mot de passe maître et une clé dérivée depuis le mot de passe de l'utilisateur
    servant à chiffrer le mot de passe maître. Si le mot de passe maître est fourni, il n'est pas recréé,
    et seulement la clé dérivée est créée.
    """
    if master_password is None:
        master_password = Fernet.generate_key()

    user_password = user_password.encode()
    salt = os.urandom(32)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000000,
    )
    derived_password = base64.urlsafe_b64encode(kdf.derive(user_password))
    fernet_derived_password = Fernet(derived_password)

    encrypted_master_password = fernet_derived_password.encrypt(master_password)

    with open('.data/salt.txt', 'wb') as fichier:
        fichier.write(salt)

    with open('.data/master_password.txt', 'wb') as fichier:
        fichier.write(encrypted_master_password)

    return str(master_password.decode())


def change_user_password(old_user_password, new_user_password):
    """
    Fonction qui change le mot de passe de l'utilisateur :
        - Récupère le mot de passe maître
        - Crée une nouvelle clé dérivée à partir du nouveau mot de passe de l'utilisateur
        - Chiffre le mot de passe maître avec la nouvelle clé dérivée
    """
    master_password = get_master_password(old_user_password)
    if master_password:
        create_master_password(new_user_password, master_password.encode())


def encrypt(message, master_password):
    """
    Fonction qui chiffre un message avec le mot de passe maître
    """
    fernet_master_password = Fernet(master_password.encode())
    return fernet_master_password.encrypt(message.encode()).decode()


def decrypt(message, master_password):
    """
    Fonction qui déchiffre un message avec le mot de passe maître
    """
    fernet_master_password = Fernet(master_password.encode())
    return fernet_master_password.decrypt(message.encode()).decode()


def current_password():
    """
    Fonction qui récupère le mot de pass maître chiffré
    """
    with open('.data/master_password.txt', 'r') as f:
        mdp = f.readline()
    return mdp

