import re


def formatar_sql(sql):
    # Mantém comentários, mas normaliza espaços
    original = sql

    # Remove espaços duplicados
    sql = re.sub(r"[ \t]+", " ", sql)

    # Normaliza quebras de linha
    sql = re.sub(r"\n\s*\n", "\n", sql)

    # Palavras-chave principais
    keywords = [
        "select", "from", "where", "group by", "order by", "having",
        "union", "union all", "intersect", "minus",
        "inner join", "left join", "right join", "full join", "cross join",
        "join", "on"
    ]

    # Quebra de linha antes das keywords
    for kw in keywords:
        sql = re.sub(
            rf"\b{kw}\b",
            f"\n{kw.upper()}",
            sql,
            flags=re.IGNORECASE
        )

    # Indentação de subqueries
    def indent_subquery(match):
        conteudo = match.group(1)
        linhas = conteudo.split("\n")
        linhas = ["    " + linha for linha in linhas]
        return "(\n" + "\n".join(linhas) + "\n)"

    sql = re.sub(r"\(([^()]+)\)", indent_subquery, sql)

    # Coloca cada coluna em uma linha no SELECT
    sql = re.sub(
        r"SELECT\s+(.*)\s+FROM",
        lambda m: "SELECT\n    " + ",\n    ".join(
            [c.strip() for c in m.group(1).split(",")]
        ) + "\nFROM",
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Alinhamento de operadores
    operadores = ["=", ">", "<", ">=", "<=", "<>", "!="]

    for op in operadores:
        sql = re.sub(rf"\s*{re.escape(op)}\s*", f" {op} ", sql)

    # Alinhamento de AND / OR
    sql = re.sub(r"\bAND\b", "\n    AND", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bOR\b", "\n    OR", sql, flags=re.IGNORECASE)

    # Remove múltiplas quebras de linha
    sql = re.sub(r"\n\s*\n", "\n", sql)

    return sql.strip()


def limpar_comentarios(sql):
    # Remove comentários de bloco /* ... */
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)

    # Remove comentários de linha --
    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)

    return sql.strip()
