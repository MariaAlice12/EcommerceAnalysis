# Dashboard de E-commerce — Apache Superset

![Python](https://img.shields.io/badge/Python-3.x-blue) ![MySQL](https://img.shields.io/badge/MySQL-8.0-orange) ![Redis](https://img.shields.io/badge/Redis-7-red) ![Apache Superset](https://img.shields.io/badge/Apache%20Superset-latest-green) ![Docker](https://img.shields.io/badge/Docker-Compose-blue)

Dashboard analítico de e-commerce construído com Apache Superset, rodando completamente via Docker. Inclui banco MySQL com dados fictícios gerados automaticamente, configuração do dashboard via scripts Python que consomem a API REST do Superset, e um painel com 5 abas temáticas e filtros nativos interativos.

---

## Stack

| Container | Imagem | Função |
|---|---|---|
| `superset_mysql` | MySQL 8.0 | Banco de dados com os dados do negócio |
| `superset_redis` | Redis 7 | Cache de queries e sessões |
| `superset_app` | Apache Superset (customizado) | Ferramenta de BI |

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/)
- Python 3 com a biblioteca `requests`:
  ```bash
  pip install requests
  ```

---

## Início rápido

### 1. Clone o repositório

```bash
git clone https://github.com/MariaAlice12/dash-apache-superset.git
cd dash-apache-superset
```

### 2. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (o `.gitignore` já o exclui do versionamento):

```env
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=ecommerce
MYSQL_USER=superset
MYSQL_PASSWORD=supersetpass
SUPERSET_SECRET_KEY=supersecretkey123changeme
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
ADMIN_EMAIL=admin@example.com
```

> Em produção, troque `SUPERSET_SECRET_KEY` por uma string longa e aleatória.

### 3. Suba os containers

```bash
make up
# ou: docker compose up -d
```

### 4. Aguarde a inicialização

O Superset leva aproximadamente **90 segundos** para inicializar. Acompanhe os logs:

```bash
make logs
```

Quando estiver pronto, acesse **http://localhost:8088** e faça login com `admin` / `admin` (ou os valores definidos no `.env`).

### 5. Adicione a conexão com o banco

No Superset: **Settings → Database Connections → + Database → MySQL**

| Campo | Valor |
|---|---|
| Host | `mysql` |
| Porta | `3306` |
| Database | `ecommerce` |
| User | `superset` |
| Password | `supersetpass` |

> Use o nome `mysql` como host — é o nome do serviço dentro da rede Docker.

### 6. Crie os datasets, gráficos e dashboard

```bash
python setup.py
```

O script cria automaticamente 11 datasets virtuais, os gráficos e o dashboard via API REST. Ao final, exibe a URL direta para o dashboard.

> O script é **idempotente**: rodar mais de uma vez atualiza o que existe, sem criar duplicatas.

---

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `MYSQL_ROOT_PASSWORD` | Senha do root do MySQL | `rootpassword` |
| `MYSQL_DATABASE` | Nome do banco de dados | `ecommerce` |
| `MYSQL_USER` | Usuário do MySQL usado pelo Superset | `superset` |
| `MYSQL_PASSWORD` | Senha do usuário MySQL | `supersetpass` |
| `SUPERSET_SECRET_KEY` | Chave de criptografia interna do Superset | `supersecretkey123changeme` |
| `ADMIN_USERNAME` | Usuário administrador do Superset | `admin` |
| `ADMIN_PASSWORD` | Senha do administrador | `admin` |
| `ADMIN_EMAIL` | E-mail do administrador | `admin@example.com` |

---

## Comandos disponíveis

```bash
make up          # sobe os containers em background
make down        # para os containers
make rebuild     # reconstrói tudo sem cache
make logs        # acompanha logs do Superset
make logs-all    # acompanha logs de todos os containers
make shell       # abre terminal dentro do container do Superset
make mysql       # abre o MySQL interativo
make reset       # destrói tudo (volumes incluídos) e recria do zero
```

---

## Estrutura do projeto

```
dash-apache-superset/
├── docker-compose.yml         # orquestra os 3 containers
├── Makefile                   # atalhos de comandos
├── .env                       # variáveis de ambiente (não versionado)
├── .gitignore
├── setup.py                   # entry point: executa o fluxo completo via API
├── config.py                  # definições declarativas de datasets, charts e dashboard
├── superset_client.py         # cliente idempotente da API REST do Superset
├── mysql/
│   └── init/
│       ├── 01_schema.sql      # criação das tabelas
│       └── 02_data.sql        # dados de exemplo + procedure geradora de pedidos
└── superset/
    ├── Dockerfile             # imagem customizada com driver MySQL
    ├── docker-init.sh         # inicialização do Superset (db upgrade, admin, gunicorn)
    └── superset_config.py     # configurações: cache Redis, banco de metadados, flags
```

---

## Como os scripts funcionam

### `config.py` — Definições declarativas

Centraliza todas as definições do dashboard:

- **11 datasets virtuais** — queries SQL que transformam os dados antes de visualizar (ex.: `receita_mensal`, `comparacao_mensal`, `kpis_visao_geral`)
- **5 charts** — especificações de tipo de visualização, métricas, agrupamentos e formatação
- **Layout** — posicionamento dos gráficos em abas via `build_layout()`
- **Native filters** — 3 filtros interativos via `build_metadata()`: Mês, Mês Base e Mês de Comparação

### `superset_client.py` — Cliente da API REST

Wrapper em torno da API do Superset com lógica de upsert (cria se não existe, atualiza se já existe):

| Método | O que faz |
|---|---|
| `upsert_dataset(name, sql, schema, db_id)` | Cria ou atualiza dataset virtual |
| `mark_dttm_column(ds_id, column_name)` | Marca coluna como timestamp |
| `upsert_chart(name, viz_type, ds_id, params)` | Cria ou atualiza gráfico |
| `upsert_dashboard(title, slug, chart_ids, ...)` | Cria ou atualiza dashboard com layout e filtros |

Autenticação JWT e CSRF são obtidas automaticamente na primeira chamada.

### `setup.py` — Entry point

Executa o fluxo completo em sequência:

```
python setup.py
    │
    ├── Cria/atualiza 11 datasets virtuais no Superset
    │       └── Marca coluna "mes" como timestamp em receita_mensal
    │
    ├── Cria/atualiza 5 charts
    │
    └── Cria/atualiza o dashboard com layout em tabs e native filters
            └── Exibe: http://localhost:8088/superset/dashboard/{id}/
```

---

## Modelo de dados

O banco `ecommerce` é populado automaticamente pelos scripts SQL em `mysql/init/`.

```
categorias (id, nome, descricao)
    └── produtos (id, nome, categoria_id, preco, custo, estoque, ativo, criado_em)
            └── itens_pedido (id, pedido_id, produto_id, quantidade, preco_unitario, subtotal)
                    └── pedidos (id, cliente_id, vendedor_id, status, canal,
                                 data_pedido, data_entrega, valor_total, desconto, frete)
                            ├── clientes (id, nome, email, cidade, estado, regiao, genero, data_nascimento)
                            └── vendedores (id, nome, regiao)
```

**Dados gerados automaticamente:**
- 5 categorias, 20 produtos, 30 clientes, 5 vendedores
- **350 pedidos** entre 2024-01-01 e 2026-03-31, com distribuição aleatória de:
  - Status: 80% entregue, 10% em trânsito, 10% cancelado
  - Canais: site, app, marketplace, loja física
  - 1 a 4 itens por pedido

---

## Dashboard

O dashboard **E-commerce — Análise de Vendas** é organizado em 5 abas:

| Aba | Conteúdo |
|---|---|
| Visão Geral | KPIs de receita, pedidos, ticket médio + gráfico mensal com variação % |
| Produtos e Canais | Desempenho por produto e canal de venda |
| Regiões e Vendedores | Análise geográfica e por vendedor |
| Perfil de Clientes | Segmentação demográfica e comportamental |
| Operação | Status de pedidos, prazos e logística |

**Filtros nativos interativos:**

| Filtro | Tipo | Efeito |
|---|---|---|
| Mês | Multi-select | Filtra todos os charts pelo mês selecionado |
| Mês Base | Single-select | Define o mês de referência na tabela comparativa |
| Mês de Comparação | Single-select | Define o mês a comparar na tabela comparativa |

---

## Resolução de problemas

**Container não sobe**
```bash
docker compose ps       # verifica status de cada container
make logs-all           # inspeciona os logs
```

**`python setup.py` falha com erro 401 ou de conexão**

O Superset ainda está inicializando. Aguarde até o log exibir `Superset pronto!` e tente novamente.

**Dashboard sem dados / gráficos vazios**

Verifique se os pedidos foram inseridos:
```bash
make mysql
# dentro do MySQL:
SELECT COUNT(*) FROM pedidos;   -- deve retornar 350
```

**Reconstrução limpa (apaga todos os dados)**
```bash
make reset
```
Isso destrói os volumes do MySQL e do Superset e recria tudo do zero.
