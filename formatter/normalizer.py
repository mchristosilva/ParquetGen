import re


def normalize_spaces(line):
    return re.sub(r"\s+", " ", line).strip()


def normalize_case(tokens, upper=True):
    if upper:
        return [t.upper() if not t.startswith("'") else t for t in tokens]
    return tokens
