# parse.py
from datetime import datetime, date
from decimal import Decimal, InvalidOperation


# ============================================================
#  PARSE DE DATAS
# ============================================================

DATE_FORMATS = [
    "%Y-%m-%d",              # ISO simples
    "%d/%m/%Y",              # Brasil
    "%Y-%m-%dT%H:%M:%S",     # ISO completo
    "%Y-%m-%d %H:%M:%S",     # SQLite / Oracle comum
    "%d-%b-%y"               # Oracle clássico (11-DEC-25)
]


def parse_sn_ativo(form):
    return "S" if form.get("SN_ATIVO") else "N"


def try_parse_date(valor):
    """Tenta converter string em datetime usando formatos conhecidos."""
    if not isinstance(valor, str):
        return None

    valor = valor.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(valor, fmt)
        except ValueError:
            pass
    return None


def parse_data_iso(valor):
    """Converte ISO completo para datetime."""
    return try_parse_date(valor)


def parse_data_oracle(valor, final=False):
    """Converte vários formatos para datetime, ajustando hora."""
    if not valor:
        return None

    dt = valor if isinstance(valor, datetime) else try_parse_date(valor)
    if not dt:
        return None

    return dt.replace(
        hour=23 if final else 0,
        minute=59 if final else 0,
        second=59 if final else 0
    )


def format_data_for_input(valor):
    """Converte datetime ou string para YYYY-MM-DD."""
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d")

    dt = try_parse_date(valor) if isinstance(valor, str) else None
    return dt.strftime("%Y-%m-%d") if dt else None


def parse_int(value):
    if value is None:
        return None
    value = str(value).strip()
    return int(value) if value.isdigit() else None


def parse_decimal(value):
    if value is None:
        return None

    value = str(value).strip()

    value = value.replace(".", "").replace(",", ".")
    if not value:
        return None

    try:
        return Decimal(value).quantize(Decimal("0.01"))
        # return round(float(value), 2)
    except InvalidOperation:
        return None


def parse_str(value):
    if value is None:
        return ""
    value = str(value).strip()
    return value or ""


TYPE_MAP = {
    "INTEGER": parse_int,
    "INT": parse_int,

    "NUMBER": parse_decimal,
    "NUMBER(10,2)": parse_decimal,
    "FLOAT": parse_decimal,
    "DECIMAL": parse_decimal,

    "VARCHAR": parse_str,
    "VARCHAR2": parse_str,
    "CHAR": parse_str,
    "TEXT": parse_str,

    "DATE": lambda v: parse_data_oracle(v, final=False),
    "TIMESTAMP": parse_data_iso,
    "DATETIME": parse_data_iso,
}


def serialize_value(valor):
    if valor is None:
        return ""

    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%dT%H:%M:%S")

    if isinstance(valor, date):
        return valor.strftime("%Y-%m-%d")

    if isinstance(valor, Decimal):
        return float(valor)

    if isinstance(valor, float) and valor.is_integer():
        return int(valor)

    if isinstance(valor, list):
        return [serialize_value(v) for v in valor]

    if isinstance(valor, dict):
        return {k: serialize_value(v) for k, v in valor.items()}

    return valor


def serialize_row(row: dict):
    return {k: serialize_value(v) for k, v in row.items()}
