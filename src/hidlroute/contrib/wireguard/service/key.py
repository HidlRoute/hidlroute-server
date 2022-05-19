#    Hidl Route - opensource vpn management system
#    Copyright (C) 2023 Dmitry Berezovsky, Alexander Cherednichenko
#
#    Hidl Route is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Hidl Route is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
