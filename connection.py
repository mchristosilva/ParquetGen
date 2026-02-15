from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from functools import wraps
from log import _log
import oracledb

load_dotenv(dotenv_path='.env')

# Ativa o modo THICK usando o Instant Client
oracledb.init_oracle_client(
    lib_dir=os.getenv("ORACLE_LIB_DIR")
)

# -------------------------
# ORACLE (seguro)
# -------------------------
usuario = os.getenv("DB_USERNAME")
senha = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
porta = os.getenv("DB_PORT")
servico = os.getenv("DB_SERVICE_NAME")

# Cria a engine SQLAlchemy
oracle_engine = create_engine(
    f"oracle+oracledb://{usuario}:{senha}@{host}:{porta}/?service_name={servico}",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)


class DBManager:
    engines = {
        "oracle": oracle_engine,
    }

    current = "oracle"

    @classmethod
    def use(cls, name: str):
        name = name.lower()
        if name not in cls.engines:
            _log(f"[DB] Banco desconhecido solicitado: {name}", "error")
            raise ValueError(f"Banco desconhecido: {name}")

        if cls.current != name:
            _log(f"[DB] Mudando banco para: {name}")

        cls.current = name

    @classmethod
    def get(cls):
        return cls.engines[cls.current]

    @classmethod
    def get_specific(cls, name: str):
        name = name.lower()
        if name not in cls.engines:
            _log(f"[DB] Banco desconhecido solicitado: {name}", "error")
            raise ValueError(f"Banco desconhecido: {name}")
        return cls.engines[name]


def use_db(name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            old = DBManager.current

            if old != name:
                _log(f"[DB] Temporariamente usando: {name}")

            DBManager.use(name)

            try:
                return func(*args, **kwargs)
            finally:
                if old != name:
                    _log(f"[DB] Restaurando banco: {old}")
                DBManager.use(old)

        return wrapper
    return decorator
