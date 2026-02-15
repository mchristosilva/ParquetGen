from sqlalchemy import text
from connection import DBManager
from decimal import Decimal
from log import _log
import time

SENSITIVE_KEYS = {"password", "password_hash",
                  "senha", "pwd", "pass", "secret"}

# Erros típicos de conexão Oracle/SQLAlchemy
RETRY_ERRORS = (
    "DPI-1010",
    "DPI-1080",
    "ORA-03113",
    "ORA-03114",
    "ORA-12541",
    "ORA-00028",
    "connection was closed",
    "not connected",
)


def sanitize_params(params):
    if not params:
        return params

    safe = {}
    for k, v in params.items():
        safe[k] = "***" if k.lower() in SENSITIVE_KEYS else v
    return safe


def sqlalchemy_exec(query, params=None, fetchone=False, retries=3, backoff=0.5):
    engine = DBManager.get()

    safe_params = sanitize_params(params)

    _log(f"SQL: {query}", sql=True)
    _log(f"PARAMS: {safe_params}", sql=True)

    if DBManager.current == "sqlite" and params:
        params = {
            k: float(v) if isinstance(v, Decimal) else v
            for k, v in params.items()
        }

    attempt = 0

    while True:
        try:
            with engine.begin() as conn:
                result = conn.execute(text(query), params or {})

                if query.lstrip().upper().startswith("SELECT"):
                    keys = [k.upper() for k in result.keys()]
                    if fetchone:
                        row = result.fetchone()
                        return dict(zip(keys, row)) if row else None
                    return [dict(zip(keys, r)) for r in result.fetchall()]

                return result.rowcount

        except Exception as e:
            msg = str(e).upper()

            # Verifica se é erro de conexão
            if any(err in msg for err in RETRY_ERRORS) and attempt < retries:
                attempt += 1
                wait = backoff * attempt
                _log(
                    f"[SQL RETRY] Tentativa {attempt}/{retries} após erro: {e}", "warning")
                time.sleep(wait)
                continue

            # Se não for erro de conexão ou esgotou tentativas
            _log(f"[SQL ERROR] {e}", "error")
            raise
