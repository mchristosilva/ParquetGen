def tokenize(sql):
    tokens = []
    buffer = ""
    i = 0
    length = len(sql)

    def flush():
        nonlocal buffer
        if buffer.strip():
            tokens.append(buffer)
        buffer = ""

    while i < length:
        ch = sql[i]

        # ---------------------------
        # Comentário de linha --
        # ---------------------------
        if ch == "-" and i + 1 < length and sql[i+1] == "-":
            flush()
            break  # ignora o resto da linha

        # ---------------------------
        # Comentário de bloco /* */
        # ---------------------------
        if ch == "/" and i + 1 < length and sql[i+1] == "*":
            flush()
            i += 2
            while i < length and not (sql[i] == "*" and i + 1 < length and sql[i+1] == "/"):
                i += 1
            i += 2
            continue

        # ---------------------------
        # Strings '...'
        # ---------------------------
        if ch == "'":
            flush()
            buffer = ch
            i += 1
            while i < length:
                buffer += sql[i]
                if sql[i] == "'" and (i + 1 >= length or sql[i+1] != "'"):
                    break
                if sql[i] == "'" and sql[i+1] == "'":
                    buffer += "'"
                    i += 1
                i += 1
            tokens.append(buffer)
            buffer = ""
            i += 1
            continue

        # ---------------------------
        # Parênteses e vírgulas
        # ---------------------------
        if ch in "(),":
            flush()
            tokens.append(ch)
            i += 1
            continue

        # ---------------------------
        # Espaço → separa token
        # ---------------------------
        if ch.isspace():
            flush()
            i += 1
            continue

        # ---------------------------
        # Operadores compostos
        # ---------------------------
        if i + 1 < length:
            two = sql[i:i+2]
            if two in {">=", "<=", "<>", "!=", "||"}:
                flush()
                tokens.append(two)
                i += 2
                continue

        # ---------------------------
        # Acumula caractere normal
        # ---------------------------
        buffer += ch
        i += 1

    flush()
    return tokens
