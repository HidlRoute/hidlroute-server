from base64 import b64encode, b64decode

from nacl.public import PrivateKey

from hidlroute.contrib.wireguard.data import KeyPair


def generate_private_key() -> str:
    private = PrivateKey.generate()
    return b64encode(bytes(private)).decode("ascii")


def generate_public_key(private_key: str) -> str:
    private = PrivateKey(b64decode(private_key))
    return b64encode(bytes(private.public_key)).decode("ascii")


def generate_keypair() -> KeyPair:
    private = generate_private_key()
    public = generate_public_key(private)
    return KeyPair(private, public)
