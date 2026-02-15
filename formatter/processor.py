from .tokenizer import tokenize
from .normalizer import normalize_spaces, normalize_case
from .indent import compute_indent
from .select_formatter import format_select


def process_file(input_path, output_path, upper=True):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result = []
    level = 0
    stack_case = []
    stack_paren = []
    stack_cte = []
    stack_over = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = normalize_spaces(line)
        tokens = tokenize(line)
        tokens = normalize_case(tokens, upper)

        # IGNORAR LINHAS SEM TOKENS
        if not tokens:
            continue

        if tokens[0] == "SELECT":
            formatted = format_select(tokens)
            for fline in formatted:
                result.append("    " * level + fline)
            continue

        level = compute_indent(tokens, level, stack_case,
                               stack_paren, stack_cte, stack_over)

        result.append("    " * level + " ".join(tokens))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(result))


def process_string(texto, upper=True):
    lines = texto.splitlines()

    result = []
    level = 0
    stack_case = []
    stack_paren = []
    stack_cte = []
    stack_over = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = normalize_spaces(line)
        tokens = tokenize(line)
        tokens = normalize_case(tokens, upper)

        if not tokens:
            continue

        if tokens[0] == "SELECT":
            formatted = format_select(tokens)
            for fline in formatted:
                result.append("    " * level + fline)
            continue

        level = compute_indent(tokens, level, stack_case,
                               stack_paren, stack_cte, stack_over)

        result.append("    " * level + " ".join(tokens))

    return "\n".join(result)
