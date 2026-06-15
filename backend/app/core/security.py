from hashlib import pbkdf2_hmac, sha256
from hmac import compare_digest
from secrets import token_bytes


PBKDF2_NAME = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 390000
PBKDF2_SALT_BYTES = 16


def legacy_hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = token_bytes(PBKDF2_SALT_BYTES)
    digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{PBKDF2_NAME}${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    if stored_hash.startswith(f"{PBKDF2_NAME}$"):
        _, iterations_text, salt_hex, digest_hex = stored_hash.split("$", 3)
        digest = pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations_text),
        )
        return compare_digest(digest.hex(), digest_hex)

    return compare_digest(legacy_hash_password(password), stored_hash)


def needs_password_rehash(stored_hash: str) -> bool:
    return not stored_hash.startswith(f"{PBKDF2_NAME}$")
