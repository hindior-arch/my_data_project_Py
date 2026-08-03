# transforms/privacy.py
import re
import hashlib


def mask_email(email):
    if not email:
        return None

    email = str(email).strip()
    if "@" not in email:
        return "MASKED"

    local, domain = email.split("@", 1)

    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

    return f"{masked_local}@{domain}"


def mask_phone(phone):
    if not phone:
        return None

    phone = str(phone).strip()
    digits = re.sub(r"\D", "", phone)

    if len(digits) <= 4:
        return "*" * len(digits)

    return "*" * (len(digits) - 3) + digits[-3:]


def mask_name(name):
    if not name:
        return None

    name = str(name).strip()

    if len(name) <= 1:
        return "*"

    return name[0] + "*" * (len(name) - 1)


def mask_address(address):
    if not address:
        return None

    return "MASKED_ADDRESS"


def mask_text_keep_length(value):
    if not value:
        return None

    value = str(value).strip()
    return "*" * len(value)


def hash_value(value):
    if not value:
        return None

    value = str(value).strip()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()