import os
import json

from utils import (
    montar_filtros,
    converter_automatico,
    validar_automatico,
    serialize_row
)

# ---------------------------------------------------------
# CONFIGURAÇÃO DE CACHE EM DISCO
# ---------------------------------------------------------

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache_tabelas")
os.makedirs(CACHE_DIR, exist_ok=True)

# ---------------------------------------------------------
# CACHE EM MEMÓRIA
# ---------------------------------------------------------
# Estrutura:
# COLUMN_CACHE[(nome_tabela, cache_key)] = colunas
#
# cache_key pode ser:
#   - None (default)
#   - nome da conexão
#   - nome do blueprint
#   - qualquer string que você quiser usar para segmentar cache
# ---------------------------------------------------------

COLUMN_CACHE = {}


def _make_cache_key(nome_tabela, cache_key=None):
    return (nome_tabela.upper(), cache_key or None)


def _disk_cache_path(nome_tabela, cache_key=None):
    key = f"{nome_tabela.upper()}"
    if cache_key:
        key += f"__{cache_key}"
    return os.path.join(CACHE_DIR, f"{key}.json")


def load_columns_from_disk(nome_tabela, cache_key=None):
    path = _disk_cache_path(nome_tabela, cache_key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Falha ao ler cache de disco para {nome_tabela}: {e}")
        return None


def save_columns_to_disk(nome_tabela, colunas, cache_key=None):
    path = _disk_cache_path(nome_tabela, cache_key)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(colunas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Falha ao salvar cache de disco para {nome_tabela}: {e}")


class Table:
    def __init__(
        self,
        nome,
        pk=None,
        dialeto=None,
        executor=None,
        auto_load=False,
        cache_key=None,
        use_disk_cache=True,
    ):
        """
        nome: nome da tabela/view no banco
        pk: None, string ou lista/tupla
        dialeto: objeto com métodos SQL específicos (get_columns, placeholder, etc.)
        executor: função que executa SQL (query, params, fetchone=False)
        auto_load: se True, carrega colunas imediatamente (não recomendado em dev)
        cache_key: chave opcional para segmentar cache (por conexão, blueprint, etc.)
        use_disk_cache: se True, usa cache em disco para colunas
        """
        self.nome = nome
        self.dialeto = dialeto
        self.exec = executor
        self.colunas = {}
        self.cache_key = cache_key
        self.use_disk_cache = use_disk_cache

        # PK pode ser:
        # - None → view
        # - string → PK simples
        # - lista/tupla → PK composta
        if pk is None:
            self.pk = None
        elif isinstance(pk, str):
            self.pk = (pk,)
        else:
            self.pk = tuple(pk)

        # Auto-load opcional (mantido por compatibilidade)
        if auto_load:
            self.load_columns()

    # ---------------------------------------------------------
    # LAZY LOADING + CACHE (MEMÓRIA + DISCO)
    # ---------------------------------------------------------

    def ensure_columns(self):
        """Carrega colunas apenas quando necessário."""
        if self.colunas:
            return
        self.load_columns()

    def load_columns(self):
        """Carrega colunas do banco apenas uma vez por tabela/cache_key."""
        if not self.dialeto:
            return

        cache_id = _make_cache_key(self.nome, self.cache_key)

        # 1) Tenta cache em memória
        if cache_id in COLUMN_CACHE:
            self.colunas = COLUMN_CACHE[cache_id]
            return

        # 2) Tenta cache em disco (se habilitado)
        if self.use_disk_cache:
            cols = load_columns_from_disk(self.nome, self.cache_key)
            if cols:
                self.colunas = cols
                COLUMN_CACHE[cache_id] = cols
                return

        # 3) Busca no banco
        try:
            cols = self.dialeto.get_columns(self.nome, self.exec)
            self.colunas = cols
            COLUMN_CACHE[cache_id] = cols

            if self.use_disk_cache:
                save_columns_to_disk(self.nome, cols, self.cache_key)

        except Exception as e:
            print(
                f"[WARN] Não foi possível carregar colunas de {self.nome}: {e}")
            self.colunas = {}

    # -------------------------
    # JSON helpers
    # -------------------------

    def to_json(self, data):
        if isinstance(data, list):
            return [serialize_row(r) for r in data]
        if isinstance(data, dict):
            return serialize_row(data)
        return data

    def from_json(self, data_json):
        self.ensure_columns()
        return converter_automatico(data_json, self.colunas)

    # -------------------------
    # CREATE TABLE
    # -------------------------

    def create(self, colunas):
        if self.pk is None:
            raise ValueError("Views não podem ser criadas via create().")

        self.colunas = colunas
        self.exec(self.dialeto.create_table(self.nome, colunas, self.pk), {})

        # Autoincrement só para PK simples
        if len(self.pk) == 1:
            for q in self.dialeto.create_autoincrement(self.nome, self.pk[0]):
                self.exec(q, {})

    # -------------------------
    # SELECT (com paginação)
    # -------------------------

    def select(self, colunas="*", filtros=None, order_by=None,
               order_dir="ASC", page=None, page_size=None, **kwargs):

        filtros = filtros.copy() if filtros else {}
        if kwargs:
            filtros.update(kwargs)

        where_sql, params = montar_filtros(filtros, self.dialeto)

        colunas_sql = ", ".join(colunas) if isinstance(
            colunas, (list, tuple)) else colunas

        query = f"SELECT {colunas_sql} FROM {self.nome}"

        if where_sql:
            query += f" WHERE {where_sql}"

        if order_by:
            query += f" ORDER BY {', '.join(order_by)} {order_dir}"

        if page and page_size:
            query = self.dialeto.paginar(query, page, page_size)

        return [serialize_row(r) for r in self.exec(query, params)]

    # -------------------------
    # GET
    # -------------------------

    def get(self, *args, colunas="*", **kwargs):

        colunas_sql = ", ".join(colunas) if isinstance(
            colunas, (list, tuple)) else colunas

        # VIEW (sem PK)
        if self.pk is None:
            if kwargs:
                filtros = kwargs
            elif args and isinstance(args[0], dict):
                filtros = args[0]
            else:
                raise ValueError("Views não possuem PK. Use filtros nomeados.")

        else:
            if args and not kwargs:
                if len(args) != len(self.pk):
                    raise ValueError(
                        "Número de argumentos não corresponde ao número de PKs.")
                filtros = dict(zip(self.pk, args))

            elif kwargs:
                filtros = kwargs

            elif args and isinstance(args[0], dict):
                filtros = args[0]

            else:
                raise ValueError("Parâmetros inválidos para get().")

        condicoes = []
        params = {}

        for chave, valor in filtros.items():
            placeholder = self.dialeto.placeholder(chave)
            condicoes.append(f"{chave} = {placeholder}")
            params[chave] = valor

        where_sql = " AND ".join(condicoes)

        query = f"""SELECT {colunas_sql} FROM {self.nome} WHERE {where_sql}"""

        row = self.exec(query, params, fetchone=True)
        return serialize_row(row) if row else None

    # -------------------------
    # SELECT2
    # -------------------------

    def select2(self, value_col="ID", text_col="NOME",
                search_term=None, page=1, page_size=20):

        self.ensure_columns()

        filtros = {}

        if search_term:
            filtros[f"{text_col}__contains"] = search_term

        dados = self.select(
            colunas=[value_col, text_col],
            filtros=filtros,
            order_by=[text_col],
            page=page,
            page_size=page_size
        )

        more = len(dados) == page_size

        return {
            "results": [{"id": r[value_col], "text": r[text_col]} for r in dados],
            "pagination": {"more": more}
        }

    # -------------------------
    # INSERT
    # -------------------------

    def insert(self, dados):
        if self.pk is None:
            raise ValueError("Views não suportam INSERT.")

        self.ensure_columns()

        dados = converter_automatico(dados, self.colunas)
        validar_automatico(dados, self.colunas)

        colunas = ", ".join(dados.keys())
        placeholders = ", ".join(self.dialeto.placeholder(k)
                                 for k in dados.keys())

        query = f"INSERT INTO {self.nome} ({colunas}) VALUES ({placeholders})"
        self.exec(query, dados)

        if len(self.pk) > 1:
            return {k: dados.get(k) for k in self.pk}

        pk_col = self.pk[0]

        if pk_col in dados:
            return dados[pk_col]

        return self.dialeto.last_insert_id(self.nome, pk_col, self.exec)

    # -------------------------
    # UPDATE
    # -------------------------

    def update(self, *args, dados=None, **kwargs):
        if self.pk is None:
            raise ValueError("Views não suportam UPDATE.")

        if dados is None:
            raise ValueError("É necessário fornecer 'dados' para update().")

        self.ensure_columns()

        dados = converter_automatico(dados, self.colunas)
        validar_automatico(dados, self.colunas)

        if args and not kwargs:
            if len(args) != len(self.pk):
                raise ValueError(
                    "Número de argumentos não corresponde ao número de PKs.")
            filtros = dict(zip(self.pk, args))

        elif kwargs:
            filtros = {k: v for k, v in kwargs.items() if k != "dados"}

        elif args and isinstance(args[0], dict):
            filtros = args[0]

        else:
            raise ValueError("Parâmetros inválidos para update().")

        set_clause = ", ".join(
            f"{k} = {self.dialeto.placeholder(k)}" for k in dados.keys()
        )

        params = dados.copy()
        condicoes = []

        for chave, valor in filtros.items():
            condicoes.append(f"{chave} = {self.dialeto.placeholder(chave)}")
            params[chave] = valor

        where_sql = " AND ".join(condicoes)

        query = f"""
            UPDATE {self.nome}
            SET {set_clause}
            WHERE {where_sql}
        """

        return self.exec(query, params)

    # -------------------------
    # DELETE
    # -------------------------

    def delete(self, *args, **kwargs):
        if self.pk is None:
            raise ValueError("Views não suportam DELETE.")

        self.ensure_columns()

        if args and not kwargs:
            if len(args) != len(self.pk):
                raise ValueError(
                    "Número de argumentos não corresponde ao número de PKs.")
            filtros = dict(zip(self.pk, args))

        elif kwargs:
            filtros = kwargs

        elif args and isinstance(args[0], dict):
            filtros = args[0]

        else:
            raise ValueError("Parâmetros inválidos para delete().")

        condicoes = []
        params = {}

        for chave, valor in filtros.items():
            condicoes.append(f"{chave} = {self.dialeto.placeholder(chave)}")
            params[chave] = valor

        where_sql = " AND ".join(condicoes)

        query = f"""
            DELETE FROM {self.nome}
            WHERE {where_sql}
        """

        return self.exec(query, params)

    # -------------------------
    # COUNT / EXISTS
    # -------------------------

    def count(self, filtros=None, **kwargs):
        filtros = filtros.copy() if filtros else {}
        if kwargs:
            filtros.update(kwargs)

        where_sql, params = montar_filtros(filtros, self.dialeto)

        query = f"SELECT COUNT(*) AS TOTAL FROM {self.nome}"
        if where_sql:
            query += f" WHERE {where_sql}"

        row = self.exec(query, params, fetchone=True)
        return row["TOTAL"] if row else 0

    def exists(self, filtros=None, **kwargs):
        return self.count(filtros, **kwargs) > 0
