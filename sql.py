# sql.py
import re
from executor import sqlalchemy_exec
from queries import QUERIES


SQL_PREFIXES = (
    "SELECT", "UPDATE", "INSERT", "DELETE",
    "WITH", "BEGIN", "CREATE", "ALTER", "DROP"
)


def is_sql(texto: str) -> bool:
    return isinstance(texto, str) and texto.strip().upper().startswith(SQL_PREFIXES)


def sql(query_or_name, params=None, fetchone=False, raw=False):
    """
    Executa SQL usando o executor centralizado (com retry, logs e sanitização).
    Aceita:
    - nome da query (QUERIES)
    - SQL bruto
    - params dict ou tuple
    """

    # 1. Resolve a query
    query = (
        query_or_name
        if raw or is_sql(query_or_name)
        else QUERIES.get(query_or_name)
    )

    if not query or not isinstance(query, str) or not query.strip():
        raise ValueError(
            f"Query inválida ou não encontrada: '{query_or_name}'")

    # 2. Converte tuple → dict
    if isinstance(params, tuple):
        keys = re.findall(r":(\w+)", query)
        if len(keys) != len(params):
            raise ValueError("Número de parâmetros não corresponde à query.")
        params = dict(zip(keys, params))

    params = params or {}

    # 3. Usa o executor centralizado
    return sqlalchemy_exec(
        query=query,
        params=params,
        fetchone=fetchone
    )
