# Este archivo se encarga de encriptar/desencriptar
# los archivos, llave, y la contraseña.

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Esta función convierta una contraseña normal
# o humanamente recordable a un conjunto de bytes
# encryptados.
def derive_key(password: str, salt: bytes) -> bytes:
    # PBKDF2 -> Password-Based Key Derivation Function 2
    # HMAC   -> Hash-Based Message Authentication Code
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        # salt en encriptacion son bits aleatorios que se mezclan
        # con la contraseña inicial para evitar duplicados si se
        # usan dos mismas contraseñas.
        iterations=480000,
        backend=default_backend()
    )
    # Se codifica la contraseña a bytes antes de derivar
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

def generate_vault_key(password: str) -> bytes:
    # Llave maestra, es la encargada de encriptar y decriptar los archivos
    key_fernet = Fernet.generate_key()
    salt = os.urandom(16)

    # Esta llave se encargara de desbloquear a la llave maestra
    key_to_encrypt = derive_key(password, salt)
    f = Fernet(key_to_encrypt)
    key_fernet_encrypted = f.encrypt(key_fernet)

    return salt + key_fernet_encrypted

# Esta función divide la key en dos (salt, contraseña cifrada)
# e intenta desifrarla.
def unlock_vault_key(password: str, vault_key_content: bytes) -> Fernet:
    try:
        # Extraer el salt y la llave cifrada
        salt = vault_key_content[:16]
        llave_fernet_cifrada = vault_key_content[16:]

        # Derivar la llave de descifrado
        llave_para_descifrar = derive_key(password, salt)

        # Intentar descifrar
        f = Fernet(llave_para_descifrar)
        llave_fernet = f.decrypt(llave_fernet_cifrada)

        return Fernet(llave_fernet)
    except InvalidToken:
        raise ValueError("Contraseña incorrecta")
    except Exception as e:
        raise ValueError(f"{e}")