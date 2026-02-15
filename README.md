📘 README.md — Gerador de Arquivos Parquet

# Gerador de Arquivos Parquet
Aplicação desktop desenvolvida em **Python + Kivy**, criada para facilitar a
geração de arquivos **Parquet** a partir de consultas SQL, com foco em
produtividade, organização e integração com ambientes corporativos.

A ferramenta inclui:
- Editor SQL com **highlight profissional (Pygments + SqlLexer)**
- Importação de arquivos `.sql`
- Formatação automática de queries **(formatter modular)**
- Execução de consultas
- Geração de arquivos Parquet
- Interface simples, leve e responsiva

---

## 🖥️ Interface
A aplicação possui uma interface clara e objetiva:
- Caixa de texto para edição da query SQL
- Botões de ação (`Executar`, `Limpar`, `Copiar`, `Abrir Pasta`, `Importar Query`)  
- Popup de seleção de arquivos com **seletor de unidades**  
- Log de execução
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
Quando o campo está vazio, aparece: `Digite ou importe uma query SQL...`  
Implementado via `canvas.after` para não interferir no cursor ou highlight.

---

### ✔ Importação de Arquivos SQL
O usuário pode:
- abrir um popup  
- navegar entre unidades locais e unidades de rede mapeadas  
- selecionar um arquivo `.sql`
- carregar e formatar automaticamente

O popup inclui um **seletor de unidades** acima do FileChooser.

---

### ✔ Formatação Automática de SQL
O formatter é modular e composto por:

- `indent.py`  
- `normalizer.py`  
- `processor.py`  
- `select_formatter.py`  
- `tokenizer.py`  

O arquivo `main.py` expõe: `formatar_sql_de_arquivo(caminho)`

E o editor usa: `Ctrl + Shift + F` para formatar o texto atual.

### Execução e Geração de Parquet
A aplicação permite:
- copiar a query formatada
- executar a query
- gerar arquivos Parquet
- abrir a pasta de saída

🧩 Arquitetura do Projeto

<pre>
ParquetGen/
│
├── fonts/
│   ├── CONSOLA.TTF
│   ├── CONSOLAB.TTF
│   ├── CONSOLAI.TTF
│   └── CONSOLAZ.TTF
│
├── formatter/
│   ├── __init__.py
│   ├── indent.py
│   ├── main.py
│   ├── normalizer.py
│   ├── processor.py
│   ├── select_formatter.py
│   └── tokenizer.py
│
├── img
│   └── icon.png
│
├── .env
├── connection.py
├── consulta.py
├── converte.py
├── format_query.py
├── listar_unidades.py
├── log.py.py
├── parquetgen.py
├── README.md
├── requirements.txt
└── sql_query_editor.py
</pre>

📦 Requisitos
- Python 3.10+
- Kivy
- Pygments
- Pandas
- PyArrow

# requirements.txt

`pip install -r requirements.txt`  

# Estrutura padrão do arquivo .env
Para garantir a conexão com o banco de dados Oracle
 e o caminho de rede padrão, deve configurar as variáveis
 de ambiente em um arquivo .env a ser colocado na raiz do projeto

<pre>
DB_USERNAME=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_SERVICE_NAME=
CAMINHO_PADRAO=
</pre>  

▶️ Como Executar

`python parquetgen.py`  

📁 Importação de Query
- Clique em Importar Query
- Escolha a unidade (C:, D:, E:, Z:)
- Navegue até o arquivo `.sql`
- Clique em Carregar
A query aparece formatada no editor

🛠️ Atalhos
- Formatar SQL: `Ctrl + Shift + F`
- Copiar Query: Botão `Copiar Query`
- Executar: Botão `Executar`

🧠 Lógica de Formatação SQL
O formatter:
- tokeniza a linha;
- normaliza espaços;
- ajusta caixa (upper/lower);
- calcula indentação;
- formata SELECTs com múltiplas colunas;
- respeita parênteses, funções e subqueries;

Exemplo:  
<pre>
SELECT`
    coluna1,
    SUM(coluna2),
    COUNT(*)
FROM tabela
WHERE coluna3 = 'ABC'
</pre>  

📄 Licença
- Open-source
