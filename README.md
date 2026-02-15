📘 README.md — RedeSC Gerador de Arquivos Parquet

# Gerador de Arquivos Parquet
Aplicação desktop desenvolvida em **Python + Kivy**, criada para facilitar a
geração de arquivos **Parquet** a partir de consultas SQL, com foco em
produtividade, organização e integração com ambientes corporativos.

A ferramenta inclui:
- Editor SQL com **highlight profissional (Pygments + SqlLexer)**
- Importação de arquivos `.sql`
- Formatação automática de queries (formatter modular)
- Execução de consultas
- Geração de arquivos Parquet
- Interface simples, leve e responsiva

---

## 🖥️ Interface
A aplicação possui uma interface clara e objetiva:
- Caixa de texto para edição da query SQL  
- Botões de ação (Executar, Limpar, Copiar, Abrir Pasta, Importar Query)  
- Log de execução  
- Popup de seleção de arquivos com **seletor de unidades**  
- Placeholder no editor quando vazio  

---

## ✨ Funcionalidades

### ✔ Editor SQL com Highlight Profissional
O editor utiliza:

- `CodeInput` (Kivy)
- `SqlLexer` (Pygments)

Isso garante coloração de:
- palavras‑chave (`SELECT`, `FROM`, `WHERE`, `JOIN`…)  
- funções (`COUNT`, `SUM`, `MAX`…)  
- strings  
- números  
- comentários  

---

### ✔ Placeholder no Editor
Quando o campo está vazio, aparece:
Digite ou importe uma query SQL...

Código
Implementado via `canvas.after` para não interferir no cursor ou highlight.

---

### ✔ Importação de Arquivos SQL
O usuário pode:

- abrir um popup  
- navegar entre unidades (C:, D:, E:, Z:)  
- selecionar um arquivo `.sql`  
- carregar e formatar automaticamente  

O popup inclui um **seletor de unidades** acima do FileChooser.

---

### ✔ Formatação Automática de SQL
O formatter é modular e composto por:

- `tokenizer.py`  
- `normalizer.py`  
- `indent.py`  
- `select_formatter.py`  
- `processor.py`  

O arquivo `main.py` expõe:
formatar_sql_de_arquivo(caminho)

E o editor usa:

Ctrl + Shift + F
para formatar o texto atual.

✔ Execução e Geração de Parquet
A aplicação permite:
executar a query
gerar arquivos Parquet
abrir a pasta de saída
copiar a query formatada

🧩 Arquitetura do Projeto
Código
ParquetGen/
│
├── formatter/
│   ├── __init__.py
│   ├── main.py
│   ├── processor.py
│   ├── tokenizer.py
│   ├── normalizer.py
│   ├── indent.py
│   └── select_formatter.py
│
├── sql_query_editor.py
├── tela.py
├── main.py
├── requirements.txt
└── README.md

📦 Requisitos
Python 3.10+
Kivy
Pygments
Pandas
PyArrow

Instalação:
pip install -r requirements.txt

# Estrutura padrão do arquivo .env
DB_USERNAME=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_SERVICE_NAME=
CAMINHO_PADRAO=


▶️ Como Executar
python parquetgen.py

📁 Importação de Query
Clique em Importar Query
Escolha a unidade (C:, D:, E:, Z:)
Navegue até o arquivo .sql
Clique em Carregar

A query aparece formatada no editor

🛠️ Atalhos
Formatar SQL:	Ctrl + Shift + F
Copiar Query:	Botão "Copiar Query"
Executar:	Botão "Executar"

🧠 Lógica de Formatação SQL
O formatter:
tokeniza a linha;
normaliza espaços;
ajusta caixa (upper/lower);
calcula indentação;
formata SELECTs com múltiplas colunas;
respeita parênteses, funções e subqueries;

Exemplo:

sql
SELECT
    coluna1,
    SUM(coluna2),
    COUNT(*)
FROM tabela
WHERE coluna3 = 'ABC'

📄 Licença
Open-source.
