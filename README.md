# Dashboard de E-commerce — Apache Superset

Dashboard de e-commerce construído no Apache Superset, rodando completamente via Docker. Inclui banco de dados MySQL com dados fictícios de e-commerce, configuração automática via scripts Python e um dashboard com 5 abas temáticas.

## Visão geral

A stack é composta por três containers:

| Container | Imagem | Função |
|---|---|---|
| `superset_mysql` | MySQL 8.0 | Banco de dados com os dados do negócio |
| `superset_redis` | Redis 7 | Cache de queries e sessões |
| `superset_app` | Apache Superset (customizado) | Ferramenta de BI |

O banco é populado automaticamente com tabelas de categorias, produtos, clientes, vendedores, pedidos e itens de pedido. O dashboard é organizado em 5 abas: **Visão Geral**, **Produtos e Canais**, **Regiões e Vendedores**, **Perfil de Clientes** e **Operação**.

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/)
- Python 3 com a biblioteca `requests` (`pip install requests`)

## Como rodar

### 1. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (ou use o existente):

```env
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_DATABASE=ecommerce
MYSQL_USER=superset
MYSQL_PASSWORD=supersetpass
SUPERSET_SECRET_KEY=uma_chave_secreta_qualquer
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
ADMIN_EMAIL=admin@example.com
```

### 2. Suba os containers

```bash
make up
# ou: docker compose up -d
```

### 3. Aguarde a inicialização

O Superset leva aproximadamente **90 segundos** para inicializar. Acompanhe os logs se quiser:

```bash
make logs
```

Quando estiver pronto, acesse: **http://localhost:8088**
Login: `admin` / `admin`

### 4. Adicione a conexão com o banco

No Superset, acesse **Settings → Database Connections → + Database** e configure:

| Campo | Valor |
|---|---|
| Host | `mysql` |
| Porta | `3306` |
| Database | `ecommerce` |
| User | `superset` |
| Password | `supersetpass` |

### 5. Crie os datasets, gráficos e dashboard

```bash
python create_charts.py
python create_dashboard.py
```

O `create_charts.py` cria 11 datasets virtuais e todos os gráficos via API REST. O `create_dashboard.py` monta o dashboard com layout em tabs.

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

## Estrutura do projeto

```
dash-apache-superset/
├── docker-compose.yml         # define os 3 containers
├── Makefile                   # atalhos de comandos
├── .env                       # variáveis de ambiente (senhas, nomes)
├── .gitignore
├── mysql/
│   └── init/
│       ├── 01_schema.sql      # criação das tabelas
│       └── 02_data.sql        # dados de exemplo
├── superset/
│   ├── Dockerfile             # imagem customizada com driver MySQL
│   ├── docker-init.sh         # inicialização do Superset
│   └── superset_config.py     # configurações (cache, banco, segurança)
├── create_charts.py           # cria datasets e charts via API
├── create_dashboard.py        # cria o dashboard com layout em tabs via API
└── fix_dashboard.py           # corrige/atualiza o dashboard se necessário
```
