from base64 import b64encode
from hashlib import scrypt, sha256
from os import urandom


def decode(b: bytes):
    return b64encode(b).decode()


def encode(s: str):
    return b64encode(s.encode())


def generate_salt():
    return decode(urandom(16))


def pcrypt(password: str, salt: str):
    drived = scrypt(password.encode(), salt=encode(salt), n=2**14, r=8, p=1, dklen=128)

    return decode(drived)


def verify(password: str, salt: str, digt: str):
    pwd = pcrypt(password, salt)
    return pwd == digt


def hash_sha256(data: str):
    sha256_hash = sha256()
    sha256_hash.update(data.encode("utf-8"))
    return sha256_hash.hexdigest()
