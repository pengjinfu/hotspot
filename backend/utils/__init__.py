import re


def hump_2_underline(hump):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub = re.sub(p, r'\1_\2', hump).lower()
    return sub
