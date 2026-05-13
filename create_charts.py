#!/usr/bin/env python3
"""Cria datasets e charts no Superset via API REST."""

import json
import sys
import requests

BASE = "http://localhost:8088"
DB_ID = 1

# ── Auth ──────────────────────────────────────────────────────────────────────
def get_token():
    r = requests.post(f"{BASE}/api/v1/security/login", json={
        "username": "admin", "password": "admin",
        "provider": "db", "refresh": True
    })
    return r.json()["access_token"]

def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# ── Cleanup ───────────────────────────────────────────────────────────────────
def cleanup(token):
    h = headers(token)
    charts = requests.get(f"{BASE}/api/v1/chart/?q=(page_size:100)", headers=h).json()
    for c in charts.get("result", []):
        requests.delete(f"{BASE}/api/v1/chart/{c['id']}", headers=h)
    datasets = requests.get(f"{BASE}/api/v1/dataset/?q=(page_size:100)", headers=h).json()
    for d in datasets.get("result", []):
        requests.delete(f"{BASE}/api/v1/dataset/{d['id']}", headers=h)
    dashboards = requests.get(f"{BASE}/api/v1/dashboard/?q=(page_size:100)", headers=h).json()
    for dash in dashboards.get("result", []):
        requests.delete(f"{BASE}/api/v1/dashboard/{dash['id']}", headers=h)
    print("── Limpeza concluída ─────────────────────────────────")

# ── Datasets ──────────────────────────────────────────────────────────────────
DATASETS = {
    "kpis_visao_geral": """
        SELECT
            SUM(valor_total)           AS receita_total,
            COUNT(*)                   AS total_pedidos,
            ROUND(AVG(valor_total), 2) AS ticket_medio
        FROM pedidos
        WHERE status != 'cancelado'
    """,
    "receita_mensal": """
        SELECT
            DATE_FORMAT(data_pedido, '%Y-%m-01') AS mes,
            DATE_FORMAT(data_pedido, '%b/%Y')    AS mes_label,
            ROUND(SUM(valor_total), 2)            AS receita,
            COUNT(*)                              AS total_pedidos,
            ROUND(AVG(valor_total), 2)            AS ticket_medio
        FROM pedidos
        WHERE status != 'cancelado'
        GROUP BY mes, mes_label
        ORDER BY mes
    """,
}

# ── Chart definitions ─────────────────────────────────────────────────────────
def make_charts(ds_ids):
    return [
        # ── Tab 1 – Visão Geral ───────────────────────────────────────────────
        {
            "slice_name": "Receita Total",
            "viz_type": "big_number_total",
            "datasource_id": ds_ids["kpis_visao_geral"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "receita_total"}, "aggregate": "SUM", "label": "Receita Total"},
                "subheader": "Pedidos entregues e em trânsito",
                "y_axis_format": "SMART_NUMBER",
                "header_font_size": 0.4,
                "subheader_font_size": 0.15,
                "color_scheme": "supersetColors",
            }),
        },
        {
            "slice_name": "Total de Pedidos",
            "viz_type": "big_number_total",
            "datasource_id": ds_ids["kpis_visao_geral"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "total_pedidos"}, "aggregate": "SUM", "label": "Total de Pedidos"},
                "subheader": "Excluindo cancelados",
                "y_axis_format": ",d",
                "header_font_size": 0.4,
                "subheader_font_size": 0.15,
                "color_scheme": "supersetColors",
            }),
        },
        {
            "slice_name": "Ticket Médio",
            "viz_type": "big_number_total",
            "datasource_id": ds_ids["kpis_visao_geral"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "big_number_total",
                "metric": {"expressionType": "SIMPLE", "column": {"column_name": "ticket_medio"}, "aggregate": "AVG", "label": "Ticket Médio"},
                "subheader": "Valor médio por pedido",
                "y_axis_format": "SMART_NUMBER",
                "header_font_size": 0.4,
                "subheader_font_size": 0.15,
                "color_scheme": "supersetColors",
            }),
        },
        {
            "slice_name": "Receita Mensal",
            "viz_type": "echarts_timeseries_bar",
            "datasource_id": ds_ids["receita_mensal"],
            "datasource_type": "table",
            "params": json.dumps({
                "viz_type": "echarts_timeseries_bar",
                "x_axis": "mes",
                "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "receita"}, "aggregate": "SUM", "label": "Receita"}],
                "x_axis_time_format": "%b/%Y",
                "y_axis_format": "SMART_NUMBER",
                "color_scheme": "supersetColors",
                "rich_tooltip": True,
                "show_legend": False,
            }),
        },
    ]


def main():
    token = get_token()
    h = headers(token)

    cleanup(token)
    print("── Criando datasets ──────────────────────────────────")
    ds_ids = {}
    for name, sql in DATASETS.items():
        r = requests.post(f"{BASE}/api/v1/dataset/", headers=h, json={
            "database": DB_ID,
            "schema": "ecommerce",
            "sql": sql.strip(),
            "table_name": name,
        })
        body = r.json()
        if "id" in body:
            ds_ids[name] = body["id"]
            requests.put(f"{BASE}/api/v1/dataset/{body['id']}/refresh", headers=h)
            print(f"  OK  {name} (id={body['id']})")
        else:
            print(f"  ERRO {name}: {body.get('message', body)}", file=sys.stderr)
            sys.exit(1)

    print("\n── Criando charts ────────────────────────────────────")
    chart_ids = []
    for chart in make_charts(ds_ids):
        r = requests.post(f"{BASE}/api/v1/chart/", headers=h, json={
            "slice_name":      chart["slice_name"],
            "viz_type":        chart["viz_type"],
            "datasource_id":   chart["datasource_id"],
            "datasource_type": "table",
            "params":          chart["params"],
        })
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
