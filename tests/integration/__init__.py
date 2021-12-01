import random


def generate_random_string(n: int) -> str:
    result = ''
    for _ in range(n):
        result += (chr(random.randint(97, 122)))
    return result
