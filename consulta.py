from sqlalchemy import text
import pandas as pd
import gc
import traceback
from connection import DBManager
import os
from log import _log, configurar_log_para_arquivo, CAMINHO
from formatter.regex_formatter import limpar_comentarios, formatar_sql


def roda_consulta(query, caminho_relativo):
    try:
        caminho_log = configurar_log_para_arquivo(caminho_relativo)
        _log("Iniciando execução da consulta")

        engine = DBManager.get()

        # 1. Bloqueio de comandos
        proibidos = ["delete", "update", "insert",
                     "drop", "alter", "truncate", "merge"]
        q_lower = query.lower()

        for palavra in proibidos:
            if palavra in q_lower:
                msg = f"Comando proibido detectado: '{palavra.upper()}'. Apenas SELECT é permitido."
                _log(msg, level="error")
                return {"erro": msg}

        # 2. Remoção de comentários
        query_limpa = limpar_comentarios(query)

        # 3. Formatação automática
        query_formatada = formatar_sql(query_limpa)

        _log("Query formatada:")
        _log(f'\n{query_formatada}')

        # 4. Validação de sintaxe
        try:
            _log("Validando sintaxe da query...")

            with engine.connect() as conn:
                conn.execute(text(f"EXPLAIN PLAN FOR {query_formatada}"))

            _log("Sintaxe válida.")
        except Exception as e:
            erro = str(e)

            sugestao = ""
            if "ORA-00923" in erro:
                sugestao = "Sugestão: verifique se o FROM está presente e na posição correta."
            elif "ORA-00936" in erro:
                sugestao = "Sugestão: falta algum elemento obrigatório (ex: SELECT, FROM)."
            elif "ORA-00933" in erro:
                sugestao = "Sugestão: verifique vírgulas, parênteses ou palavras-chave fora do lugar."
            elif "ORA-00904" in erro:
                sugestao = "Sugestão: coluna ou alias inválido."

            msg = f"Consulta inválida: {erro}"
            _log(msg, level="error")
            if sugestao:
                _log(sugestao, level="error")

            return {"erro": msg + ("\n" + sugestao if sugestao else "")}

        # 5. Execução real
        _log("Executando consulta no banco...")
        df = pd.read_sql(query, con=engine)
        _log(f"Consulta realizada. {len(df)} registros carregados.")

        caminho_parquet = os.path.join(CAMINHO, caminho_relativo)
        os.makedirs(os.path.dirname(caminho_parquet), exist_ok=True)

        df.to_parquet(caminho_parquet, engine="pyarrow", compression="snappy")
        _log(f"Arquivo salvo em: {caminho_parquet}")

        del df
        gc.collect()
        _log(f"Limpeza de memória concluida")

        return {
            "parquet": caminho_parquet,
            "log": caminho_log
        }

    except Exception as e:
        _log("Erro durante execução", level="error")
        _log(traceback.format_exc(), level="error")
        return {"erro": str(e)}
