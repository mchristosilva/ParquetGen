def format_select(tokens):
    if tokens[0].upper() != "SELECT":
        return [" ".join(tokens)]

    result = ["SELECT"]
    col = []
    depth = 0

    for tok in tokens[1:]:
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1

        if tok == "," and depth == 0:
            result.append("    " + " ".join(col))
            col = []
        else:
            col.append(tok)

    if col:
        result.append("    " + " ".join(col))

    return result
