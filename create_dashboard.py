#!/usr/bin/env python3
"""Cria o dashboard de e-commerce no Superset com layout em 5 páginas (tabs)."""

import json
import requests

BASE = "http://localhost:8088"

def get_token():
    r = requests.post(f"{BASE}/api/v1/security/login", json={
        "username": "admin", "password": "admin",
        "provider": "db", "refresh": True
    })
    return r.json()["access_token"]

def h(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# IDs dos charts criados (na ordem do script anterior)
CHARTS = {
    "receita_total":          29,
    "total_pedidos":          30,
    "ticket_medio":           31,
    "taxa_cancelamento":      32,
    "receita_mensal":         33,
    "pedidos_status":         34,
    "top_produtos":           35,
    "receita_categoria":      36,
    "receita_canal":          37,
    "margem_categoria":       38,
    "receita_regiao":         39,
    "ranking_vendedores":     40,
    "pedidos_regiao":         41,
    "faixa_etaria":           42,
    "genero":                 43,
    "receita_regiao_cliente": 44,
    "cancelamento_mes":       45,
    "cancelamento_volume":    46,
    "ticket_vendedor":        47,
}

def row(id_, width=24, height=8):
    """Gera um componente de chart dentro do layout."""
    return {
        "id": f"CHART-{id_}",
        "type": "CHART",
        "meta": {"chartId": id_, "width": width, "height": height},
        "children": [],
    }

def build_layout():
    """
    Layout em 5 tabs (abas), cada uma representando uma página do storytelling.
    Estrutura: ROOT > GRID > ROW > CHART
    """
    c = CHARTS

    layout = {
        "ROOT_ID": {
            "id": "ROOT_ID",
            "type": "ROOT",
            "children": ["GRID_ID"],
        },
        "GRID_ID": {
            "id": "GRID_ID",
            "type": "GRID",
            "children": ["TABS_ID"],
        },
        "TABS_ID": {
            "id": "TABS_ID",
            "type": "TABS",
            "children": ["TAB_1", "TAB_2", "TAB_3", "TAB_4", "TAB_5"],
        },

        # ── Tab 1: Visão Geral ──────────────────────────────────────────────
        "TAB_1": {
            "id": "TAB_1", "type": "TAB",
            "meta": {"text": "1. Visão Geral"},
            "children": ["ROW_1_1", "ROW_1_2"],
        },
        "ROW_1_1": {
            "id": "ROW_1_1", "type": "ROW",
            "children": [f"CHART-{c['receita_total']}", f"CHART-{c['total_pedidos']}",
                         f"CHART-{c['ticket_medio']}", f"CHART-{c['taxa_cancelamento']}"],
        },
        f"CHART-{c['receita_total']}":      {**row(c['receita_total'],      6, 5)},
        f"CHART-{c['total_pedidos']}":      {**row(c['total_pedidos'],      6, 5)},
        f"CHART-{c['ticket_medio']}":       {**row(c['ticket_medio'],       6, 5)},
        f"CHART-{c['taxa_cancelamento']}":  {**row(c['taxa_cancelamento'],  6, 5)},
        "ROW_1_2": {
            "id": "ROW_1_2", "type": "ROW",
            "children": [f"CHART-{c['receita_mensal']}", f"CHART-{c['pedidos_status']}"],
        },
        f"CHART-{c['receita_mensal']}":     {**row(c['receita_mensal'],     16, 9)},
        f"CHART-{c['pedidos_status']}":     {**row(c['pedidos_status'],      8, 9)},

        # ── Tab 2: Produtos e Canais ────────────────────────────────────────
        "TAB_2": {
            "id": "TAB_2", "type": "TAB",
            "meta": {"text": "2. Produtos e Canais"},
            "children": ["ROW_2_1", "ROW_2_2"],
        },
        "ROW_2_1": {
            "id": "ROW_2_1", "type": "ROW",
            "children": [f"CHART-{c['top_produtos']}", f"CHART-{c['receita_categoria']}"],
        },
        f"CHART-{c['top_produtos']}":       {**row(c['top_produtos'],       14, 10)},
        f"CHART-{c['receita_categoria']}":  {**row(c['receita_categoria'],  10, 10)},
        "ROW_2_2": {
            "id": "ROW_2_2", "type": "ROW",
            "children": [f"CHART-{c['receita_canal']}", f"CHART-{c['margem_categoria']}"],
        },
        f"CHART-{c['receita_canal']}":      {**row(c['receita_canal'],      12, 8)},
        f"CHART-{c['margem_categoria']}":   {**row(c['margem_categoria'],   12, 8)},

        # ── Tab 3: Geografia e Vendedores ───────────────────────────────────
        "TAB_3": {
            "id": "TAB_3", "type": "TAB",
            "meta": {"text": "3. Regiões e Vendedores"},
            "children": ["ROW_3_1", "ROW_3_2"],
        },
        "ROW_3_1": {
            "id": "ROW_3_1", "type": "ROW",
            "children": [f"CHART-{c['receita_regiao']}", f"CHART-{c['pedidos_regiao']}"],
        },
        f"CHART-{c['receita_regiao']}":     {**row(c['receita_regiao'],     12, 8)},
        f"CHART-{c['pedidos_regiao']}":     {**row(c['pedidos_regiao'],     12, 8)},
        "ROW_3_2": {
            "id": "ROW_3_2", "type": "ROW",
            "children": [f"CHART-{c['ranking_vendedores']}", f"CHART-{c['ticket_vendedor']}"],
        },
        f"CHART-{c['ranking_vendedores']}": {**row(c['ranking_vendedores'], 12, 8)},
        f"CHART-{c['ticket_vendedor']}":    {**row(c['ticket_vendedor'],    12, 8)},

        # ── Tab 4: Perfil de Clientes ───────────────────────────────────────
        "TAB_4": {
            "id": "TAB_4", "type": "TAB",
            "meta": {"text": "4. Perfil de Clientes"},
            "children": ["ROW_4_1"],
        },
        "ROW_4_1": {
            "id": "ROW_4_1", "type": "ROW",
            "children": [f"CHART-{c['faixa_etaria']}", f"CHART-{c['genero']}",
                         f"CHART-{c['receita_regiao_cliente']}"],
        },
        f"CHART-{c['faixa_etaria']}":             {**row(c['faixa_etaria'],             8, 9)},
        f"CHART-{c['genero']}":                   {**row(c['genero'],                   8, 9)},
        f"CHART-{c['receita_regiao_cliente']}":   {**row(c['receita_regiao_cliente'],   8, 9)},

        # ── Tab 5: Operação ─────────────────────────────────────────────────
        "TAB_5": {
            "id": "TAB_5", "type": "TAB",
            "meta": {"text": "5. Operação"},
            "children": ["ROW_5_1"],
        },
        "ROW_5_1": {
            "id": "ROW_5_1", "type": "ROW",
            "children": [f"CHART-{c['cancelamento_mes']}", f"CHART-{c['cancelamento_volume']}"],
        },
        f"CHART-{c['cancelamento_mes']}":    {**row(c['cancelamento_mes'],    12, 9)},
        f"CHART-{c['cancelamento_volume']}": {**row(c['cancelamento_volume'], 12, 9)},
    }

    return layout


def main():
    token = get_token()

    all_chart_ids = list(CHARTS.values())

    payload = {
        "dashboard_title": "E-commerce — Análise de Vendas",
        "published": True,
        "slug": "ecommerce-vendas",
        "position_json": json.dumps(build_layout()),
    }

    r = requests.post(f"{BASE}/api/v1/dashboard/", headers=h(token), json=payload)
    body = r.json()

    if "id" not in body:
        print("Erro ao criar dashboard:", body)
        return

    dash_id = body["id"]
    print(f"Dashboard criado: id={dash_id}")

    # Associa os charts ao dashboard
    for cid in all_chart_ids:
        requests.put(
            f"{BASE}/api/v1/chart/{cid}",
            headers=h(token),
            json={"dashboards": [dash_id]},
        )

    print(f"\nAcesse: http://localhost:8088/superset/dashboard/{dash_id}/")


if __name__ == "__main__":
    main()
