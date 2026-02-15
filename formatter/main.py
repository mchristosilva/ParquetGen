import argparse
from .processor import process_file, process_string


def formatar_sql_de_arquivo(caminho, upper=True):
    with open(caminho, "r", encoding="utf-8") as f:
        texto = f.read()

    return process_string(texto, upper=upper)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Formatador SQL modular.")
    parser.add_argument("entrada")
    parser.add_argument("saida")
    parser.add_argument("--preserve-case", action="store_true")

    args = parser.parse_args()

    process_file(args.entrada, args.saida, upper=not args.preserve_case)
