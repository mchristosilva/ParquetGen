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

- Editor SQL com highlight
- Placeholder automático quando o editor está vazio
- Botões de ação:
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
├── fonts/                      <= Pacote do motor de formatação SQL
│   ├── CONSOLA.TTF
│   ├── CONSOLAB.TTF
│   ├── CONSOLAI.TTF
│   └── CONSOLAZ.TTF
│
├── formatter/                  <= Pacote do motor de formatação SQL
│   ├── __init__.py
│   ├── indent.py
│   ├── main.py
│   ├── normalizer.py
│   ├── processor.py
|   ├── regex_formatter.py
│   ├── select_formatter.py
│   └── tokenizer.py
│
├── img/
│   └── icon.png                <= Favicon da aplicação, formato .png, 200px x 200px
│
├── .env
├── connection.py               <= Utilitário de conexão com o Banco e motor SQL
├── consulta.py                 <= Utilitário validador da consulta
├── listar_unidades.py          <= Utilitário para varredura de unidades do computador
├── log.py                      <= Utilitário gerador de logs
├── parquetgen.py
├── README.md                   <= Instruções
├── requirements.txt
└── sql_query_editor.py         <= Editor SQL simples
</pre>

## 5. 📦 Requisitos

- Python 3.10+
- Requerimentos do arquivo `requirements.txt`
- Oracle Instant Client

### Instalação:

- clone o repositório 
- crie um virtual environment `venv`
- ative o virtual environment
- instale os requerimentos a partir do arquivo `requirements.txt`  

``` python

pip install -r requirements.txt

```

- instale o Oracle Instant Client (se necessário)

## 6. ⚙️ Estrutura do Arquivo .env

Para conexão com Oracle e definição do caminho padrão de rede:

``` python

DB_USERNAME=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_SERVICE_NAME=
CAMINHO_PADRAO=

```

O arquivo .env deve estar na raiz do projeto.

## 7. ▶️ Como Executar

`python parquetgen.py`

ou crie um atalho para o Desktop para:  

`parquetgen.bat`

## 8. 📁 Importação de Query

1. Clique em **Importar Query**
2. Escolha a unidade (C:, D:, E:, etc...)
3. Navegue até o arquivo `.sql`
4. Clique em Carregar

A query será exibida já **formatada** no editor.

## 9. 🛠️ Atalhos  

- **Executar**: botão _Executar_                     <= Executa a query importada ou digitada no **Editor**
- **Importar Query**: botão _Importar Query_         <= Abre navegador de arquivos e pastas e importa arquivo `.sql` para alteração ou execução
- **Limpar**: botão _Limpar_                         <= Limpa caixas de texto, **pós-execução**
- **Copiar Query**: botão _Copiar Query_             <= Copia a query da caixa de edição para a área de transferência
- **Abrir Pasta**: botão _Abrir Pasta_               <= Abre a pasta dos arquivos gerados, **pós-execução**

## 10. 🧠 Lógica de Formatação SQL  

O formatter realiza:  

- tokenização da linha
- normalização de espaços
- ajuste de caixa (upper/lower)
- cálculo de indentação
- formatação de SELECTs com múltiplas colunas
- respeito a parênteses, funções e subqueries

Exemplo:  

``` sql

SELECT
    coluna1,
    SUM(coluna2),
    COUNT(*)
FROM tabela
WHERE coluna3 = 'ABC'

```

## 11. 📄 Licença  

Open-source
