import re

EMAIL_REGEXP = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"


def send_email_token(receiver_address: str):
    pass


def is_valid_email(email: str):
    res = re.search(EMAIL_REGEXP, email)
    if res is not None:
        return True
    return False
