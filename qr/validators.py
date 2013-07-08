import re

def coordvalidator(value):
    m = re.search(r'^\(\d+,\d+\)$', value)
    if m is None:
        raise ValueError
