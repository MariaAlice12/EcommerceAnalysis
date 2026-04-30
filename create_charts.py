#!/usr/bin/env python3
"""Cria datasets e charts no Superset via API REST."""

import json
import sys
import requests

BASE = "http://localhost:8088"
DB_ID = 2

# ── Auth ──────────────────────────────────────────────────────────────────────
def get_token():
    r = requests.post(f"{BASE}/api/v1/security/login", json={
        "username": "admin", "password": "admin",
        "provider": "db", "refresh": True
    })
    return r.json()["access_token"]

def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def csrf(token):
    r = requests.get(f"{BASE}/api/v1/security/csrf_token/", headers=headers(token))
    return r.json()["result"]

# ── Datasets ──────────────────────────────────────────────────────────────────
DATASETS = {
    "receita_mensal": """
        SELECT
            DATE_FORMAT(data_pedido, '%Y-%m-01') AS mes,
            COUNT(*)                              AS total_pedidos,
            SUM(valor_total)                      AS receita
        FROM pedidos
        WHERE status != 'cancelado'
        GROUP BY mes
        ORDER BY mes
    """,

    "kpis_gerais": """
        SELECT
            COUNT(*)                                                        AS total_pedidos,
            SUM(CASE WHEN status='cancelado' THEN 1 ELSE 0 END)            AS cancelados,
            SUM(CASE WHEN status!='cancelado' THEN valor_total ELSE 0 END) AS receita_total,
            ROUND(SUM(CASE WHEN status!='cancelado' THEN valor_total ELSE 0 END)
                  / NULLIF(COUNT(CASE WHEN status!='cancelado' THEN 1 END),0), 2) AS ticket_medio,
            ROUND(SUM(CASE WHEN status='cancelado' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS taxa_cancelamento
        FROM pedidos
    """,

    "pedidos_por_status": """
        SELECT status, COUNT(*) AS total
        FROM pedidos
        GROUP BY status
    """,

    "receita_por_categoria": """
        SELECT
            c.nome                                                    AS categoria,
            ROUND(SUM(ip.subtotal), 2)                                AS receita,
            ROUND(SUM(ip.subtotal - ip.quantidade * p.custo), 2)      AS lucro,
            ROUND((SUM(ip.subtotal - ip.quantidade * p.custo))
                  / NULLIF(SUM(ip.subtotal),0) * 100, 1)              AS margem_pct
        FROM itens_pedido ip
        JOIN produtos p   ON p.id = ip.produto_id
        JOIN categorias c ON c.id = p.categoria_id
        JOIN pedidos pd   ON pd.id = ip.pedido_id
        WHERE pd.status != 'cancelado'
        GROUP BY c.id, c.nome
        ORDER BY receita DESC
    """,

    "top_produtos": """
        SELECT
            p.nome                                                   AS produto,
            c.nome                                                   AS categoria,
            SUM(ip.quantidade)                                       AS unidades,
            ROUND(SUM(ip.subtotal), 2)                               AS receita,
            ROUND((SUM(ip.subtotal - ip.quantidade * p.custo))
                  / NULLIF(SUM(ip.subtotal),0) * 100, 1)             AS margem_pct
        FROM itens_pedido ip
        JOIN produtos p   ON p.id = ip.produto_id
        JOIN categorias c ON c.id = p.categoria_id
        JOIN pedidos pd   ON pd.id = ip.pedido_id
        WHERE pd.status != 'cancelado'
        GROUP BY p.id, p.nome, c.nome
        ORDER BY receita DESC
        LIMIT 10
    """,

    "receita_por_canal": """
        SELECT
            canal,
            COUNT(*)                                                      AS pedidos,
            ROUND(SUM(valor_total), 2)                                    AS receita,
            ROUND(SUM(valor_total)/NULLIF(COUNT(*),0), 2)                 AS ticket_medio
        FROM pedidos
        WHERE status != 'cancelado'
        GROUP BY canal
        ORDER BY receita DESC
    """,

    "receita_por_regiao": """
        SELECT
            cl.regiao,
            COUNT(DISTINCT pd.id)          AS pedidos,
            ROUND(SUM(pd.valor_total), 2)  AS receita,
            COUNT(DISTINCT cl.id)          AS clientes
        FROM pedidos pd
        JOIN clientes cl ON cl.id = pd.cliente_id
        WHERE pd.status != 'cancelado'
        GROUP BY cl.regiao
        ORDER BY receita DESC
    """,

    "vendedores_performance": """
        SELECT
            v.nome                         AS vendedor,
            v.regiao,
            COUNT(pd.id)                   AS pedidos,
            ROUND(SUM(pd.valor_total), 2)  AS receita,
            ROUND(AVG(pd.valor_total), 2)  AS ticket_medio
        FROM pedidos pd
        JOIN vendedores v ON v.id = pd.vendedor_id
        WHERE pd.status != 'cancelado'
        GROUP BY v.id, v.nome, v.regiao
        ORDER BY receita DESC
    """,

    "clientes_faixa_etaria": """
        SELECT
            CASE
                WHEN TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE()) < 30 THEN 'Até 29'
                WHEN TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE()) < 40 THEN '30-39'
                WHEN TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE()) < 50 THEN '40-49'
                ELSE '50+'
            END AS faixa_etaria,
            genero,
            COUNT(*) AS total
        FROM clientes
        GROUP BY faixa_etaria, genero
    """,

    "clientes_por_regiao": """
        SELECT
            cl.regiao,
            COUNT(DISTINCT cl.id)                               AS clientes,
            COUNT(pd.id)                                        AS pedidos,
            ROUND(SUM(pd.valor_total), 2)                       AS receita,
            ROUND(AVG(pd.valor_total), 2)                       AS ticket_medio
        FROM clientes cl
        LEFT JOIN pedidos pd ON pd.cliente_id = cl.id AND pd.status != 'cancelado'
        GROUP BY cl.regiao
        ORDER BY receita DESC
    """,

    "cancelamentos_por_mes": """
        SELECT
            DATE_FORMAT(data_pedido, '%Y-%m-01')                            AS mes,
            COUNT(*)                                                         AS total,
            SUM(CASE WHEN status='cancelado' THEN 1 ELSE 0 END)             AS cancelados,
            ROUND(SUM(CASE WHEN status='cancelado' THEN 1 ELSE 0 END)*100.0
                  / COUNT(*), 1)                                             AS taxa_pct
        FROM pedidos
        GROUP BY mes
        ORDER BY mes
    """,
}

# ── Chart definitions ─────────────────────────────────────────────────────────
def make_charts(ds_ids):
    return [
        # ── Página 1: Visão Geral ──────────────────────────────────────────
        {
            "slice_name": "Receita Total",
            "viz_type": "big_number_total",
            "datasource_id": ds_ids["kpis_gerais"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "receita_total"}, "aggregate": "SUM", "label": "Receita Total"},
                "subheader": "Pedidos entregues e em trânsito",
                "y_axis_format": "SMART_NUMBER",
            }),
        },
        {
            "slice_name": "Total de Pedidos",
            "viz_type": "big_number_total",
            "datasource_id": ds_ids["kpis_gerais"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "total_pedidos"}, "aggregate": "SUM", "label": "Total de Pedidos"},
                "subheader": "Total geral",
                "y_axis_format": "SMART_NUMBER",
            }),
        },
        {
            "slice_name": "Ticket Médio",
            "viz_type": "big_number_total",
            "datasource_id": ds_ids["kpis_gerais"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "ticket_medio"}, "aggregate": "AVG", "label": "Ticket Médio"},
                "subheader": "Valor médio por pedido",
                "y_axis_format": "SMART_NUMBER",
            }),
        },
        {
            "slice_name": "Taxa de Cancelamento (%)",
            "viz_type": "big_number_total",
            "datasource_id": ds_ids["kpis_gerais"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "taxa_cancelamento"}, "aggregate": "AVG", "label": "Taxa de Cancelamento"},
                "subheader": "% sobre total de pedidos",
                "y_axis_format": ".1f",
            }),
        },
        {
            "slice_name": "Receita Mensal",
            "viz_type": "echarts_timeseries_line",
            "datasource_id": ds_ids["receita_mensal"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "echarts_timeseries_line",
                "x_axis": "mes",
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "receita"}, "aggregate": "SUM", "label": "Receita"}],
                "x_axis_time_format": "%b/%Y",
                "y_axis_format": "SMART_NUMBER",
                "area": True,
                "opacity": 0.3,
            }),
        },
        {
            "slice_name": "Pedidos por Status",
            "viz_type": "pie",
            "datasource_id": ds_ids["pedidos_por_status"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "pie",
                "groupby": ["status"],
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "total"}, "aggregate": "SUM", "label": "Total"},
                "donut": True,
                "show_labels": True,
                "label_type": "key_percent",
            }),
        },

        # ── Página 2: Produtos ─────────────────────────────────────────────
        {
            "slice_name": "Top 10 Produtos por Receita",
            "viz_type": "bar",
            "datasource_id": ds_ids["top_produtos"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "bar",
                "groupby": ["produto"],
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "receita"}, "aggregate": "SUM", "label": "Receita"}],
                "y_axis_format": "SMART_NUMBER",
                "bar_stacked": False,
            }),
        },
        {
            "slice_name": "Receita por Categoria",
            "viz_type": "pie",
            "datasource_id": ds_ids["receita_por_categoria"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "pie",
                "groupby": ["categoria"],
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "receita"}, "aggregate": "SUM", "label": "Receita"},
                "donut": True,
                "show_labels": True,
                "label_type": "key_percent",
            }),
        },
        {
            "slice_name": "Receita por Canal de Venda",
            "viz_type": "bar",
            "datasource_id": ds_ids["receita_por_canal"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "bar",
                "groupby": ["canal"],
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "receita"}, "aggregate": "SUM", "label": "Receita"}],
                "y_axis_format": "SMART_NUMBER",
            }),
        },
        {
            "slice_name": "Margem por Categoria",
            "viz_type": "bar",
            "datasource_id": ds_ids["receita_por_categoria"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "bar",
                "groupby": ["categoria"],
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "margem_pct"}, "aggregate": "AVG", "label": "Margem (%)"}],
                "y_axis_format": ".1f",
            }),
        },

        # ── Página 3: Geografia e Vendedores ──────────────────────────────
        {
            "slice_name": "Receita por Região",
            "viz_type": "bar",
            "datasource_id": ds_ids["receita_por_regiao"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "bar",
                "groupby": ["regiao"],
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "receita"}, "aggregate": "SUM", "label": "Receita"}],
                "y_axis_format": "SMART_NUMBER",
            }),
        },
        {
            "slice_name": "Ranking de Vendedores",
            "viz_type": "bar",
            "datasource_id": ds_ids["vendedores_performance"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "bar",
                "groupby": ["vendedor"],
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "receita"}, "aggregate": "SUM", "label": "Receita"}],
                "y_axis_format": "SMART_NUMBER",
            }),
        },
        {
            "slice_name": "Pedidos por Região",
            "viz_type": "bar",
            "datasource_id": ds_ids["receita_por_regiao"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "bar",
                "groupby": ["regiao"],
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "pedidos"}, "aggregate": "SUM", "label": "Pedidos"}],
            }),
        },

        # ── Página 4: Clientes ────────────────────────────────────────────
        {
            "slice_name": "Clientes por Faixa Etária",
            "viz_type": "pie",
            "datasource_id": ds_ids["clientes_faixa_etaria"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "pie",
                "groupby": ["faixa_etaria"],
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "total"}, "aggregate": "SUM", "label": "Clientes"},
                "donut": False,
                "show_labels": True,
                "label_type": "key_percent",
            }),
        },
        {
            "slice_name": "Distribuição por Gênero",
            "viz_type": "pie",
            "datasource_id": ds_ids["clientes_faixa_etaria"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "pie",
                "groupby": ["genero"],
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "total"}, "aggregate": "SUM", "label": "Clientes"},
                "donut": True,
                "show_labels": True,
                "label_type": "key_percent",
            }),
        },
        {
            "slice_name": "Receita por Região dos Clientes",
            "viz_type": "bar",
            "datasource_id": ds_ids["clientes_por_regiao"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "bar",
                "groupby": ["regiao"],
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "receita"}, "aggregate": "SUM", "label": "Receita"}],
                "y_axis_format": "SMART_NUMBER",
            }),
        },

        # ── Página 5: Operação ────────────────────────────────────────────
        {
            "slice_name": "Taxa de Cancelamento por Mês",
            "viz_type": "echarts_timeseries_line",
            "datasource_id": ds_ids["cancelamentos_por_mes"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "echarts_timeseries_line",
                "x_axis": "mes",
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "taxa_pct"}, "aggregate": "AVG", "label": "Taxa Cancelamento (%)"}],
                "x_axis_time_format": "%b/%Y",
                "y_axis_format": ".1f",
            }),
        },
        {
            "slice_name": "Cancelamentos por Mês (Volume)",
            "viz_type": "echarts_timeseries_bar",
            "datasource_id": ds_ids["cancelamentos_por_mes"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "echarts_timeseries_bar",
                "x_axis": "mes",
                "metrics": [
                    {"expressionType": "SIMPLE", "column": {"column_name": "total"}, "aggregate": "SUM", "label": "Total"},
                    {"expressionType": "SIMPLE", "column": {"column_name": "cancelados"}, "aggregate": "SUM", "label": "Cancelados"},
                ],
                "x_axis_time_format": "%b/%Y",
            }),
        },
        {
            "slice_name": "Ticket Médio por Vendedor",
            "viz_type": "bar",
            "datasource_id": ds_ids["vendedores_performance"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "bar",
                "groupby": ["vendedor"],
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "ticket_medio"}, "aggregate": "AVG", "label": "Ticket Médio"}],
                "y_axis_format": "SMART_NUMBER",
            }),
        },
    ]


def main():
    token = get_token()
    h = headers(token)

    print("── Criando datasets ──────────────────────────────────")
    ds_ids = {}
    for name, sql in DATASETS.items():
        payload = {
            "database": DB_ID,
            "schema": "ecommerce",
            "sql": sql.strip(),
            "table_name": name,
        }
        r = requests.post(f"{BASE}/api/v1/dataset/", headers=h, json=payload)
        body = r.json()
        if "id" in body:
            ds_ids[name] = body["id"]
            print(f"  OK  {name} (id={body['id']})")
        else:
            print(f"  ERRO {name}: {body.get('message', body)}", file=sys.stderr)
            sys.exit(1)

    print("\n── Criando charts ────────────────────────────────────")
    chart_ids = []
    for chart in make_charts(ds_ids):
        payload = {
            "slice_name":     chart["slice_name"],
            "viz_type":       chart["viz_type"],
            "datasource_id":  chart["datasource_id"],
            "datasource_type": "table",
            "params":         chart["params"],
        }
        r = requests.post(f"{BASE}/api/v1/chart/", headers=h, json=payload)
        body = r.json()
        if "id" in body:
            chart_ids.append(body["id"])
            print(f"  OK  {chart['slice_name']} (id={body['id']})")
        else:
            print(f"  ERRO {chart['slice_name']}: {body.get('message', body)}", file=sys.stderr)

    print(f"\n✓ {len(chart_ids)} charts criados.")
    print("IDs:", chart_ids)


if __name__ == "__main__":
    main()
