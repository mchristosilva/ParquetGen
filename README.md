# 📘 Gerador de Arquivos Parquet  
Aplicação desktop desenvolvida em Python + Kivy para facilitar a criação de arquivos Parquet a partir de consultas SQL.
O objetivo é oferecer produtividade, organização e integração com ambientes corporativos, mantendo uma interface leve e direta.

---

## 📑 Sumário
1. Visão Geral
2. Interface
3. Funcionalidades
4. Arquitetura do Projeto
5. Requisitos
6. Configuração do .env
7. Como Executar
8. Importação de Query
9. Atalhos
10. Lógica de Formatação SQL
11. Licença

---

1. 🔍 Visão Geral  

O Gerador de Arquivos Parquet permite:

- editar e formatar consultas SQL com highlight profissional;
- importar arquivos .sql;
- executar consultas em banco Oracle;
- gerar arquivos Parquet de forma rápida;
- organizar o fluxo de trabalho com logs, atalhos e interface responsiva.

Ideal para analistas, engenheiros de dados e equipes que precisam transformar consultas SQL em datasets padronizados.

---

2. 🖥️ Interface  

A interface foi projetada para ser simples e objetiva:

- Editor SQL com highlight (Pygments + SqlLexer)
- Placeholder automático quando o editor está vazio
= Botões de ação:
  - **Executar**
  - **Limpar**
  - **Copiar**
  - **Abrir Pasta**
  - **Importar Query**
- Popup de seleção de arquivos com **seletor de unidades locais ou mapeadas**
- Log de execução integrado

---

## 3. ✨ Funcionalidades

### ✔ Editor SQL com Highlight Profissional

Baseado em:

- `CodeInput` (Kivy)
- `SqlLexer` (Pygments)

Com coloração para:

- palavras‑chave (`SELECT`, `FROM`, `WHERE`, `JOIN`…)
- funções (`COUNT`, `SUM`, `MAX`…)
- strings
- números
- comentários

### ✔ Placeholder Inteligente

Quando o editor está vazio, exibe:  

`Digite ou importe uma query SQL...`

Implementado via `canvas.after`, sem interferir no cursor ou no highlight.

### ✔ Importação de Arquivos SQL

O usuário pode:

- abrir o popup de seleção
- navegar entre unidades locais e de rede
- escolher um arquivo .sql
- carregar e formatar automaticamente o conteúdo

O popup inclui um seletor de unidades acima do `FileChooser`.

### ✔ Formatação Automática de SQL

O formatter é modular e composto por:

- `indent.py`
- `normalizer.py`
- `processor.py`
- `select_formatter.py`
- `tokenizer.py`

O módulo principal expõe:  

`formatar_sql_de_arquivo(caminho)`  

No editor, o atalho:  

`Ctrl + Shift + F`  

formata o texto atual.

### ✔ Execução e Geração de Arquivos Parquet  

A aplicação permite:  

- copiar a query formatada
- executar a consulta
- gerar arquivos Parquet
- abrir a pasta de saída automaticamente

## 4. 🧩 Arquitetura do Projeto  

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
├── img/
│   └── icon.png
│
├── .env
├── connection.py
├── consulta.py
├── converte.py
├── format_query.py
├── listar_unidades.py
├── log.py
├── parquetgen.py
├── README.md
├── requirements.txt
└── sql_query_editor.py
</pre>

## 5. 📦 Requisitos

- Python 3.10+
- Kivy
- Pygments
- Pandas
- PyArrow

Instalação:

`pip install -r requirements.txt`

## 6. ⚙️ Estrutura do Arquivo .env

Para conexão com Oracle e definição do caminho padrão de rede:

<pre>
DB_USERNAME=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_SERVICE_NAME=
CAMINHO_PADRAO=
</pre>

O arquivo .env deve estar na raiz do projeto.

## 7. ▶️ Como Executar

`python parquetgen.py`

## 8. 📁 Importação de Query

1. Clique em **Importar Query**
2. Escolha a unidade (C:, D:, E:, Z:)
3. Navegue até o arquivo `.sql`
4. Clique em Carregar

A query será exibida já **formatada** no editor.

## 9. 🛠️ Atalhos  

- **Formatar SQL**: `Ctrl + Shift + F`
- **Copiar Query**: botão _Copiar Query_
- **Executar**: botão _Executar_

## 10. 🧠 Lógica de Formatação SQL  

O formatter realiza:

- tokenização da linha
- normalização de espaços
- ajuste de caixa (upper/lower)
- cálculo de indentação
- formatação de SELECTs com múltiplas colunas
- respeito a parênteses, funções e subqueries

Exemplo:

<pre>
SELECT
    coluna1,
    SUM(coluna2),
    COUNT(*)
FROM tabela
WHERE coluna3 = 'ABC'
</pre>

## 11. 📄 Licença
Open-source