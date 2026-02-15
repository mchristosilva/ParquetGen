import argparse
import re

# Palavras-chave principais
TOP_LEVEL = {
    "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "WITH"
}

BLOCK_KEYWORDS = {
    "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING",
    "VALUES", "SET", "JOIN", "LEFT JOIN", "RIGHT JOIN",
    "INNER JOIN", "OUTER JOIN"
}

CASE_OPEN = {"CASE"}
CASE_MID = {"WHEN", "THEN", "ELSE"}
CASE_CLOSE = {"END"}

FUNCTION_NAMES = {
    "TO_CHAR", "NVL", "DECODE", "SUM", "COUNT", "AVG", "MIN", "MAX",
    "FN_IDADE", "TRUNC", "ADD_MONTHS"
}


def separar_tokens(linha):
    tokens = []
    buffer = ""
    in_string = False

    for char in linha:
        if char == "'" and not in_string:
            in_string = True
            if buffer:
                tokens.append(buffer)
                buffer = ""
            buffer += char
        elif char == "'" and in_string:
            buffer += char
            tokens.append(buffer)
            buffer = ""
            in_string = False
        elif in_string:
            buffer += char
        else:
            if char in "(),":
                if buffer:
                    tokens.append(buffer)
                    buffer = ""
                tokens.append(char)
            elif char.isspace():
                if buffer:
                    tokens.append(buffer)
                    buffer = ""
            else:
                buffer += char

    if buffer:
        tokens.append(buffer)

    return tokens


def normalizar_sql(linha):
    return re.sub(r"\s+", " ", linha).strip()


def eh_funcao(tokens):
    if len(tokens) >= 2:
        return tokens[0].upper() in FUNCTION_NAMES and tokens[1] == "("
    return False


def indentacao(tokens, nivel, stack):
    linha = " ".join(tokens).upper()

    # Fecha parênteses estruturais
    if ")" in tokens:
        while stack and stack[-1] == "(":
            stack.pop()
            nivel = max(0, nivel - 1)

    # Fecha CASE
    if linha.startswith("END"):
        if stack and stack[-1] == "CASE":
            stack.pop()
            nivel -= 1
        return nivel

    # Abre CASE
    if linha.startswith("CASE"):
        stack.append("CASE")
        return nivel + 1

    # WHEN / THEN / ELSE dentro de CASE
    if stack and stack[-1] == "CASE" and any(linha.startswith(k) for k in CASE_MID):
        return nivel + 1

    # Detecta subquery
    if "(" in tokens and "SELECT" in linha:
        stack.append("(")
        return nivel + 1

    # SELECT principal ou subquery
    if linha.startswith("SELECT"):
        return 0 if not stack else nivel + 1

    # FROM / WHERE / GROUP BY / ORDER BY
    if any(linha.startswith(k) for k in BLOCK_KEYWORDS):
        return 1

    # JOIN + ON na mesma linha
    if "JOIN" in linha:
        return 1

    # vírgula → volta ao nível de coluna
    if tokens[-1] == ",":
        return 1 if nivel > 1 else nivel

    return nivel


def formatar_select(tokens):
    """
    Quebra SELECT automaticamente em colunas.
    """
    if tokens[0].upper() != "SELECT":
        return [" ".join(tokens).upper()]

    resultado = ["SELECT"]
    coluna = []

    for tok in tokens[1:]:
        if tok == ",":
            resultado.append("    " + " ".join(coluna).upper() + ",")
            coluna = []
        else:
            coluna.append(tok)

    if coluna:
        resultado.append("    " + " ".join(coluna).upper())

    return resultado


def processar_arquivo(entrada, saida):
    with open(entrada, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    linhas_processadas = []
    nivel = 0
    stack = []

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        linha = normalizar_sql(linha)
        tokens = separar_tokens(linha)

        # SELECT especial
        if tokens and tokens[0].upper() == "SELECT":
            linhas_select = formatar_select(tokens)
            for ls in linhas_select:
                linhas_processadas.append("    " * nivel + ls)
            continue

        nivel = indentacao(tokens, nivel, stack)
        linhas_processadas.append("    " * nivel + " ".join(tokens).upper())

    with open(saida, "w", encoding="utf-8") as f:
        for linha in linhas_processadas:
            f.write(linha + "\n")

    print(f"Arquivo processado: {entrada} → {saida}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Formatador SQL estilo Oracle.")
    parser.add_argument("entrada", help="Arquivo SQL de entrada")
    parser.add_argument("saida", help="Arquivo SQL de saída")

    args = parser.parse_args()

    processar_arquivo(args.entrada, args.saida)
