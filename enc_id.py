#!/usr/bin/python
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES

def encrypt_snap(media):
    key = bytes('1234567890123456')
    cipher = AES.new(key, AES.MODE_ECB)
    padded = media + ((16 - len(media) % 16) * chr(16 - len(media) % 16))
    encrypted = cipher.encrypt(padded)
    return encrypted

def decrypt_snap(media):
    key = bytes('1234567890123456')
    cipher = AES.new(key, AES.MODE_ECB)
    padded = media + ((16 - len(media) % 16) * chr(16 - len(media) % 16)).encode('utf8')
    decrypted = cipher.decrypt(padded)
    return decrypted

msg = 'vunerable_key_management'
encrypted = encrypt_snap(msg)
print encrypted.encode("hex")
