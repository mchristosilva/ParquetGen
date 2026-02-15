# utils.py

import datetime
from decimal import Decimal
from parse import TYPE_MAP, serialize_row


# ============================================================
#  DETECÇÃO DE TIPO SQL
# ============================================================

def detectar_tipo_sql(tipo: str) -> str:
    if not tipo:
        return ""

    tipo = tipo.upper().strip()

    if tipo.startswith("NUMBER("):
        return "NUMBER(10,2)"
    if tipo.startswith("NUMBER"):
        return "NUMBER"
    if tipo.startswith("VARCHAR2"):
        return "VARCHAR2"
    if tipo.startswith("VARCHAR"):
        return "VARCHAR"
    if tipo.startswith("CHAR"):
        return "CHAR"
    if tipo.startswith("DATE"):
        return "DATE"
    if tipo.startswith("TIMESTAMP"):
        return "TIMESTAMP"
    if tipo.startswith("DATETIME"):
        return "DATETIME"
    if tipo.startswith("INT"):
        return "INTEGER"

    return tipo


# ============================================================
#  CONVERSÃO AUTOMÁTICA
# ============================================================

def converter_automatico(dados: dict, colunas: dict) -> dict:
    convertidos = {}

    for campo, valor in dados.items():
        tipo_sql = detectar_tipo_sql(colunas.get(campo, ""))
        parser = TYPE_MAP.get(tipo_sql)
        convertidos[campo] = parser(valor) if parser else valor

    return convertidos


# ============================================================
#  VALIDAÇÃO AUTOMÁTICA
# ============================================================

def validar_automatico(dados: dict, colunas: dict):
    for campo, valor in dados.items():
        tipo_sql = detectar_tipo_sql(colunas.get(campo, ""))

        if valor is None:
            continue

        if tipo_sql in ("INTEGER", "NUMBER", "NUMBER(10,2)"):
            if not isinstance(valor, (int, float, Decimal)):
                raise TypeError(f"Campo '{campo}' deve ser numérico.")

        elif tipo_sql in ("VARCHAR", "VARCHAR2", "CHAR", "TEXT"):
            if not isinstance(valor, str):
                raise TypeError(f"Campo '{campo}' deve ser string.")

        elif tipo_sql == "DATE":
            if not isinstance(valor, datetime.date):
                raise TypeError(f"Campo '{campo}' deve ser datetime.date.")

        elif tipo_sql in ("TIMESTAMP", "DATETIME"):
            if not isinstance(valor, datetime.datetime):
                raise TypeError(f"Campo '{campo}' deve ser datetime.datetime.")


# ============================================================
#  MONTAGEM DE FILTROS
# ============================================================

def montar_filtros(filtros, dialeto, _prefix_counter=[0]):
    if not filtros:
        return "", {}

    clausulas = []
    params = {}

    filtros = filtros.copy()

    # RAW SQL
    raw = filtros.pop("__raw__", None)
    if raw:
        clausulas.extend(raw if isinstance(raw, list) else [raw])

    operadores = {
        "igual": "=", "maior": ">", "menor": "<",
        "maiorouigual": ">=", "menorouigual": "<=",
        "diferente": "!=", "entre": "BETWEEN", "em": "IN",
        "eq": "=", "gt": ">", "lt": "<",
        "gte": ">=", "lte": "<=", "neq": "!=",
        "between": "BETWEEN", "in": "IN",
    }

    # ---------------------------------------------------------
    # Subquery helper
    # ---------------------------------------------------------
    def montar_where_subquery(where_dict, prefix="sub_"):
        sub_sql, sub_params = montar_filtros(where_dict, dialeto)

        if not sub_sql:
            sub_sql = "1=1"

        if prefix is None:
            params.update(sub_params)
            return sub_sql

        # prefixo incremental
        _prefix_counter[0] += 1
        prefix = f"{prefix}{_prefix_counter[0]}_"

        prefixed = {}
        for k, v in sub_params.items():
            new_key = f"{prefix}{k}"
            prefixed[new_key] = v
            sub_sql = sub_sql.replace(
                dialeto.placeholder(k),
                dialeto.placeholder(new_key)
            )

        params.update(prefixed)
        return sub_sql

    # ---------------------------------------------------------
    # Loop principal
    # ---------------------------------------------------------
    for campo, valor in filtros.items():

        if valor is None or valor == "":
            continue

        # OR lógico
        if campo == "__or__":
            sub_clauses = []
            for cond in valor:
                sub_sql, sub_params = montar_filtros(cond, dialeto)
                sub_clauses.append(f"({sub_sql})")
                params.update(sub_params)
            clausulas.append("(" + " OR ".join(sub_clauses) + ")")
            continue

        # NOT lógico
        if campo == "__not__":
            sub_sql, sub_params = montar_filtros(valor, dialeto)
            clausulas.append(f"NOT ({sub_sql})")
            params.update(sub_params)
            continue

        # AND lógico
        if campo == "__and__":
            sub_clauses = []
            for cond in valor:
                sub_sql, sub_params = montar_filtros(cond, dialeto)
                sub_clauses.append(f"({sub_sql})")
                params.update(sub_params)
            clausulas.append("(" + " AND ".join(sub_clauses) + ")")
            continue

        # ---------------------------------------------------------
        # Operadores com "__"
        # ---------------------------------------------------------
        if "__" in campo:
            campo_base, op = campo.split("__", 1)
            op = op.lower()

            # NOT IN SUBQUERY
            if op == "not_in_subquery":
                table = valor["table"]
                column = valor["column"]
                where = valor.get("where", {})
                where_sql = montar_where_subquery(where)
                clausulas.append(
                    f"{campo_base} NOT IN (SELECT {column} FROM {table} WHERE {where_sql})"
                )
                continue

            # IN SUBQUERY
            if op == "in_subquery":
                table = valor["table"]
                column = valor["column"]
                where = valor.get("where", {})
                where_sql = montar_where_subquery(where)
                clausulas.append(
                    f"{campo_base} IN (SELECT {column} FROM {table} WHERE {where_sql})"
                )
                continue

            # EXISTS
            if op == "exists":
                table = valor["table"]
                where = valor.get("where", {})
                where_sql = montar_where_subquery(where)
                clausulas.append(
                    f"EXISTS (SELECT 1 FROM {table} WHERE {where_sql})"
                )
                continue

            # NOT EXISTS
            if op == "not_exists":
                table = valor["table"]
                where = valor.get("where", {})
                where_sql = montar_where_subquery(where)
                clausulas.append(
                    f"NOT EXISTS (SELECT 1 FROM {table} WHERE {where_sql})"
                )
                continue

            # LIKE
            if op in ("startswith", "comeca_com"):
                pname = f"{campo_base}_startswith"
                clausulas.append(dialeto.like(campo_base))
                params[pname] = f"{valor}%"
                continue

            if op in ("endswith", "termina_com"):
                pname = f"{campo_base}_endswith"
                clausulas.append(dialeto.like(campo_base))
                params[pname] = f"%{valor}"
                continue

            if op in ("contains", "contem"):
                pname = f"{campo_base}_contains"
                clausulas.append(dialeto.like(campo_base))
                params[pname] = f"%{valor}%"
                continue

            # BETWEEN
            if op in ("between", "entre"):
                p1, p2 = f"{campo_base}_from", f"{campo_base}_to"
                clausulas.append(
                    f"{campo_base} BETWEEN {dialeto.placeholder(p1)} AND {dialeto.placeholder(p2)}"
                )
                params[p1], params[p2] = valor
                continue

            # IN
            if op in ("in", "em"):
                placeholders = []
                for i, v in enumerate(valor):
                    pname = f"{campo_base}_{op}_{i}"
                    placeholders.append(dialeto.placeholder(pname))
                    params[pname] = v
                clausulas.append(
                    f"{campo_base} IN ({', '.join(placeholders)})"
                )
                continue

            # Operadores simples
            if op in operadores:
                pname = f"{campo_base}_{op}"
                operador_sql = operadores[op]
                clausulas.append(
                    f"{campo_base} {operador_sql} {dialeto.placeholder(pname)}"
                )
                params[pname] = valor
                continue

        # Tupla → operador direto
        if isinstance(valor, tuple) and len(valor) == 2:
            operador, v = valor
            pname = f"{campo}_{operador}"
            clausulas.append(
                f"{campo} {operador} {dialeto.placeholder(pname)}"
            )
            params[pname] = v
            continue

        # Lista → IN
        if isinstance(valor, list):
            placeholders = []
            for i, v in enumerate(valor):
                pname = f"{campo}_list_{i}"
                placeholders.append(dialeto.placeholder(pname))
                params[pname] = v
            clausulas.append(f"{campo} IN ({', '.join(placeholders)})")
            continue

        # Caso simples
        pname = f"{campo}_eq"
        clausulas.append(f"{campo} = {dialeto.placeholder(pname)}")
        params[pname] = valor

    return " AND ".join(clausulas), params
