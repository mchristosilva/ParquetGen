import inspect
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

CAMINHO = os.getenv("CAMINHO_PADRAO", "")
if not CAMINHO:
    raise ValueError("Variável CAMINHO_PADRAO não definida no .env")


LOG_UTILS = True

# -------------------------
# CORES
# -------------------------
RESET = "\033[0m"
COLORS = {
    "INFO": "\033[92m",     # verde
    "WARNING": "\033[93m",  # amarelo
    "ERROR": "\033[91m",    # vermelho
    "DEBUG": "\033[94m",    # azul
}

# -------------------------
# PASTA DE LOGS
# -------------------------
os.makedirs("logs", exist_ok=True)

# -------------------------
# FORMATADOR COM CORES
# -------------------------


class ColorFormatter(logging.Formatter):
    def format(self, record):
        # salva mensagem original
        original_msg = record.msg

        # aplica cor APENAS para o console
        color = COLORS.get(record.levelname, "")
        record.msg = f"{color}{original_msg}{RESET}"

        # formata a mensagem colorida
        formatted = super().format(record)

        # restaura mensagem original para outros handlers
        record.msg = original_msg

        return formatted


# -------------------------
# LOGGER PRINCIPAL
# -------------------------
logger = logging.getLogger("HSJ")
logger.setLevel(logging.DEBUG)

# -------------------------
# FORMATADORES (console e arquivos)
# -------------------------
console_format = ColorFormatter(
    "[%(asctime)s] [%(levelname)s] [%(mod)s.%(caller)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_format = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(mod)s.%(caller)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

sql_format = logging.Formatter(
    "[%(asctime)s] [SQL] [%(mod)s.%(caller)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(console_format)

file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=2_000_000,
    backupCount=5,
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_format)

sql_handler = RotatingFileHandler(
    "logs/sql.log",
    maxBytes=5_000_000,
    backupCount=3,
    encoding="utf-8"
)
sql_handler.setLevel(logging.DEBUG)
sql_handler.setFormatter(sql_format)

logger.handlers.clear()
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(sql_handler)


def _log(msg, level="info", sql=False):
    if not LOG_UTILS:
        return

    caller_frame = inspect.stack()[1]
    caller_name = caller_frame.function
    module_name = caller_frame.frame.f_globals["__name__"]

    extra = {"caller": caller_name, "mod": module_name}

    level = level.lower()

    if sql:
        logger.debug(msg, extra=extra)
        return

    if level == "debug":
        logger.debug(msg, extra=extra)
    elif level == "warning":
        logger.warning(msg, extra=extra)
    elif level == "error":
        logger.error(msg, extra=extra)
    else:
        logger.info(msg, extra=extra)


def configurar_log_para_arquivo(caminho_parquet):
    """
    Configura os logs para usar o MESMO caminho e nome do arquivo parquet.
    Exemplo:
        parquet: beira_leito/2025/estoque.parquet
        log:     beira_leito/2025/estoque.log
    """
    base = CAMINHO

    # Remove extensão .parquet e troca por .log
    relativo = caminho_parquet.replace(".parquet", ".log")

    # Caminho final do log
    caminho_log = os.path.join(base, relativo)

    # Pasta do log
    pasta = os.path.dirname(caminho_log)
    os.makedirs(pasta, exist_ok=True)

    # Mantém SOMENTE o console
    logger.handlers = [
        h for h in logger.handlers
        if isinstance(h, logging.StreamHandler)
    ]

    # Cria APENAS o handler do arquivo principal
    file_handler = RotatingFileHandler(
        caminho_log,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_format)

    logger.addHandler(file_handler)

    return caminho_log
