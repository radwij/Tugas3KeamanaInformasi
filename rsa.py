import random
import hashlib

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def mod_inverse(e, phi):
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        g, x, y = egcd(b % a, a)
        return g, y - (b // a) * x, x

    g, x, _ = egcd(e, phi)
    if g != 1:
        raise Exception("Modular inverse does not exist")
    return x % phi

def generate_prime(bits):
    while True:
        num = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(num):
            return num

def is_prime(n, k=5):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _ in range(k):
        a = random.randint(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_rsa_keys(bits=2048):
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        raise Exception("e and phi are not coprime")

    d = mod_inverse(e, phi)

    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key

def rsa_encrypt(public_key, plaintext):
    e, n = public_key
    plaintext_int = int.from_bytes(plaintext.encode(), 'big')
    ciphertext = pow(plaintext_int, e, n)
    return str(ciphertext)

def rsa_decrypt(private_key, ciphertext):
    d, n = private_key
    if isinstance(ciphertext, str):
        ciphertext = int(ciphertext)
    plaintext_int = pow(ciphertext, d, n)
    plaintext = plaintext_int.to_bytes((plaintext_int.bit_length() + 7) // 8, 'big').decode()
    return plaintext

def hash_function(message):
    return hashlib.sha256(message.encode()).digest()


def rsa_sign(private_key, message):
    d, n = private_key
    hashed_message = int.from_bytes(hash_function(message), 'big')
    signature = pow(hashed_message, d, n)
    return str(signature)


def rsa_verify(public_key, message, signature):
    e, n = public_key
    if isinstance(signature, str):
        signature = int(signature)
    decrypted_hash = pow(signature, e, n)
    original_hash = int.from_bytes(hash_function(message), 'big')

    return decrypted_hash == original_hash
