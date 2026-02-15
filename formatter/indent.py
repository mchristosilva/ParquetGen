BLOCK_KEYWORDS = {
    "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING",
    "VALUES", "SET", "JOIN", "LEFT JOIN", "RIGHT JOIN",
    "INNER JOIN", "OUTER JOIN", "ON"
}

CASE_OPEN = {"CASE"}
CASE_MID = {"WHEN", "THEN", "ELSE"}
CASE_CLOSE = {"END"}

UNION_KEYWORDS = {"UNION", "UNION ALL", "INTERSECT", "MINUS"}


def compute_indent(tokens, level, stack_case, stack_paren, stack_cte, stack_over):
    line = " ".join(tokens).upper()

    # -----------------------------
    # FECHAMENTO DE PARÊNTESES
    # -----------------------------
    if ")" in tokens:
        # Fecha OVER
        if stack_over:
            stack_over.pop()
            level -= 1
            return level

        # Fecha CTE
        if stack_cte:
            stack_cte.pop()
            level -= 1
            return level

        # Fecha parênteses normais
        if stack_paren:
            stack_paren.pop()
            level -= 1
            return level

    # -----------------------------
    # CTE: WITH
    # -----------------------------
    if tokens[0] == "WITH":
        stack_cte.append("WITH")
        return 0

    # Nome da CTE: X AS (
    if len(tokens) >= 3 and tokens[1] == "AS" and "(" in tokens:
        stack_cte.append(tokens[0])
        return level + 1

    # Vírgula entre CTEs
    if tokens[-1] == "," and stack_cte:
        return 1

    # SELECT principal após CTE
    if tokens[0] == "SELECT" and stack_cte and not stack_paren:
        return 0

    # -----------------------------
    # OVER (funções window)
    # -----------------------------
    if "OVER" in tokens:
        stack_over.append("OVER")
        return level + 1

    # PARTITION BY / ORDER BY dentro do OVER
    if stack_over and tokens[0] in {"PARTITION", "ORDER"}:
        return level + 1

    # -----------------------------
    # CASE
    # -----------------------------
    if tokens[0] in CASE_CLOSE:
        if stack_case:
            stack_case.pop()
            level -= 1
        return level

    if tokens[0] in CASE_OPEN:
        stack_case.append("CASE")
        return level + 1

    if stack_case and tokens[0] in CASE_MID:
        return level + 1

    # -----------------------------
    # SUBQUERY
    # -----------------------------
    if "(" in tokens and "SELECT" in line:
        stack_paren.append("(")
        return level + 1

    # SELECT
    if tokens[0] == "SELECT":
        return 0 if not stack_paren else level + 1

    # -----------------------------
    # UNION / INTERSECT / MINUS
    # -----------------------------
    if tokens[0] in UNION_KEYWORDS:
        return 0

    # -----------------------------
    # BLOCOS NORMAIS
    # -----------------------------
    if tokens[0] in BLOCK_KEYWORDS:
        return 1

    return level
