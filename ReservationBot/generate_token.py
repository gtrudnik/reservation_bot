import pgpy


def generate_token():
    cipher = pgpy.constants.SymmetricKeyAlgorithm.AES256
    token = str(cipher.gen_key().hex())
    return token


