import re


def is_valid_format(card_number):
    return bool(re.match(r"^[0-9]{13,19}$", card_number))


def luhn_check(card_number):
    total = 0
    reverse_digits = card_number[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def is_valid_card(card_number):
    return is_valid_format(card_number) and luhn_check(card_number)


def format_card_number(card: str):
    return " ".join([card[i:i + 4] for i in range(0, len(card), 4)])
