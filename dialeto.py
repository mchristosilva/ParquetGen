class DialetoSQLite:
    def placeholder(self, nome):
        return f":{nome}"

    def like(self, campo):
        # Compatível com o novo montar_filtros
        return f"{campo} LIKE {self.placeholder(campo)}"

    def last_insert_id(self, table, pk_col, exec_fn):
        row = exec_fn("SELECT last_insert_rowid() AS ID", {}, fetchone=True)
        return row["ID"]

    def paginar(self, query, page, page_size):
        offset = (page - 1) * page_size
        return f"{query} LIMIT {page_size} OFFSET {offset}"

    def create_table(self, nome, colunas, pk):
        cols = []

        # PK composta → PRIMARY KEY (a, b)
        if isinstance(pk, (list, tuple)) and len(pk) > 1:
            for c, t in colunas.items():
                cols.append(f"{c} {t}")
            pk_sql = ", ".join(pk)
            cols.append(f"PRIMARY KEY ({pk_sql})")

        # PK simples → INTEGER PRIMARY KEY AUTOINCREMENT
        else:
            pk_col = pk[0] if isinstance(pk, (list, tuple)) else pk
            for c, t in colunas.items():
                if c == pk_col:
                    cols.append(f"{c} INTEGER PRIMARY KEY AUTOINCREMENT")
                else:
                    cols.append(f"{c} {t}")

        return f"CREATE TABLE IF NOT EXISTS {nome} ({', '.join(cols)})"

    def create_autoincrement(self, nome, pk):
        return []

    # ---------------------------------------------------------
    # 🔥 NOVO: Carregar colunas automaticamente no SQLite
    # ---------------------------------------------------------
    def get_columns(self, table_name, executor):
        sql = f"PRAGMA table_info({table_name})"
        rows = executor(sql, {})
        return {r["name"]: None for r in rows}


class DialetoOracle:
    def placeholder(self, nome):
        return f":{nome}"

    def like(self, campo):
        return f"UPPER({campo}) LIKE UPPER({self.placeholder(campo)})"

    def last_insert_id(self, table, pk_col, exec_fn):
        seq = f"{table}_SEQ"
        try:
            row = exec_fn(
                f"SELECT {seq}.CURRVAL AS ID FROM dual", {}, fetchone=True)
            return row["ID"]
        except Exception:
            return None

    def paginar(self, query, page, page_size):
        offset = (page - 1) * page_size
        limite = offset + page_size

        return f"""
        SELECT * FROM (
            SELECT t.*, ROWNUM AS rn
            FROM ({query}) t
            WHERE ROWNUM <= {limite}
        )
        WHERE rn > {offset}
        """

    def create_table(self, nome, colunas, pk):
        cols = []

        if isinstance(pk, (list, tuple)) and len(pk) > 1:
            for c, t in colunas.items():
                cols.append(f"{c} {t}")
            pk_sql = ", ".join(pk)
            cols.append(f"PRIMARY KEY ({pk_sql})")
        else:
            pk_col = pk[0] if isinstance(pk, (list, tuple)) else pk
            for c, t in colunas.items():
                if c == pk_col:
                    cols.append(f"{c} NUMBER PRIMARY KEY")
                else:
                    cols.append(f"{c} {t}")

        return f"CREATE TABLE {nome} ({', '.join(cols)})"

    def create_autoincrement(self, nome, pk):
        if isinstance(pk, (list, tuple)) and len(pk) > 1:
            return []

        pk_col = pk[0] if isinstance(pk, (list, tuple)) else pk

        seq = f"{nome}_SEQ"
        trg = f"{nome}_TRG"

        return [
            f"CREATE SEQUENCE {seq} START WITH 1 INCREMENT BY 1",
            f"""
            CREATE OR REPLACE TRIGGER {trg}
            BEFORE INSERT ON {nome}
            FOR EACH ROW
            WHEN (new.{pk_col} IS NULL)
            BEGIN
                SELECT {seq}.NEXTVAL INTO :new.{pk_col} FROM dual;
            END;
            """
        ]

    # ---------------------------------------------------------
    # 🔥 NOVO: Carregar colunas automaticamente no Oracle
    # ---------------------------------------------------------
    def get_columns(self, table_name, executor):
        sql = """
            SELECT COLUMN_NAME
            FROM USER_TAB_COLUMNS
            WHERE TABLE_NAME = :t
        """
        rows = executor(sql, {"t": table_name.upper()})
        return {r["COLUMN_NAME"]: None for r in rows}
