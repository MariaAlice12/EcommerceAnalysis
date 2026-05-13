#!/usr/bin/env python3
"""Cria o dashboard de e-commerce no Superset."""

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

# IDs dos charts criados pelo create_charts.py
CHARTS = {
    "receita_total":  1,
    "total_pedidos":  2,
    "ticket_medio":   3,
    "receita_mensal": 4,
}

def chart_component(id_, width=8, height=5):
    return {
        "id": f"CHART-{id_}",
        "type": "CHART",
        "meta": {"chartId": id_, "sliceId": id_, "width": width, "height": height},
        "children": [],
    }

def build_layout():
    c = CHARTS
    return {
        "ROOT_ID": {"id": "ROOT_ID", "type": "ROOT", "children": ["GRID_ID"]},
        "GRID_ID": {"id": "GRID_ID", "type": "GRID", "children": ["TABS_ID"]},
        "TABS_ID": {"id": "TABS_ID", "type": "TABS", "children": ["TAB_1"]},

        # ── Tab 1: Visão Geral ────────────────────────────────────────────────
        "TAB_1": {
            "id": "TAB_1", "type": "TAB",
            "meta": {"text": "1. Visão Geral"},
            "children": ["ROW_1_1", "ROW_1_2"],
        },
        "ROW_1_1": {
            "id": "ROW_1_1", "type": "ROW",
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "children": [
                f"CHART-{c['receita_total']}",
                f"CHART-{c['total_pedidos']}",
                f"CHART-{c['ticket_medio']}",
            ],
        },
        f"CHART-{c['receita_total']}": {**chart_component(c['receita_total'],  4, 18)},
        f"CHART-{c['total_pedidos']}": {**chart_component(c['total_pedidos'],  4, 18)},
        f"CHART-{c['ticket_medio']}":  {**chart_component(c['ticket_medio'],   4, 18)},

        "ROW_1_2": {
            "id": "ROW_1_2", "type": "ROW",
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "children": [f"CHART-{c['receita_mensal']}"],
        },
        f"CHART-{c['receita_mensal']}": {**chart_component(c['receita_mensal'], 12, 28)},
    }


def build_metadata(ds_id_receita_mensal):
    kpi_chart_ids = [CHARTS["receita_total"], CHARTS["total_pedidos"], CHARTS["ticket_medio"]]
    return {
        "native_filter_configuration": [
            {
                "id": "NATIVE_FILTER-mes_label",
                "name": "Mês",
                "type": "NATIVE_FILTER",
                "filterType": "filter_select",
                "description": "",
                "targets": [{"datasetId": ds_id_receita_mensal, "column": {"name": "mes_label"}}],
                "defaultDataMask": {"extraFormData": {}, "filterState": {}, "ownState": {}},
                "controlValues": {
                    "enableEmptyFilter": False,
                    "defaultToFirstItem": False,
                    "creatable": False,
                    "multiSelect": True,
                    "searchAllOptions": False,
                    "inverseSelection": False,
                },
                "cascadeParentIds": [],
                "scope": {
                    "rootPath": ["ROOT_ID"],
                    "excluded": kpi_chart_ids,
                },
            }
        ],
        "timed_refresh_immune_slices": [],
        "expanded_slices": {},
        "refresh_frequency": 0,
        "color_scheme": "",
        "label_colors": {},
        "shared_label_colors": [],
        "map_label_colors": {},
        "color_scheme_domain": [],
        "cross_filters_enabled": True,
    }


def main():
    token = get_token()

    datasets = requests.get(
        f"{BASE}/api/v1/dataset/?q=(page_size:100)", headers=h(token)
    ).json().get("result", [])
    ds_receita_mensal = next(
        (d["id"] for d in datasets if d["table_name"] == "receita_mensal"), None
    )
    if ds_receita_mensal is None:
        print("Erro: dataset 'receita_mensal' não encontrado. Rode create_charts.py primeiro.")
        return

    all_chart_ids = list(CHARTS.values())

    r = requests.post(f"{BASE}/api/v1/dashboard/", headers=h(token), json={
        "dashboard_title": "E-commerce — Análise de Vendas",
        "published": True,
        "slug": "ecommerce-vendas",
        "position_json": json.dumps(build_layout()),
    })
    body = r.json()
    if "id" not in body:
        print("Erro ao criar dashboard:", body)
        return

    dash_id = body["id"]
    print(f"Dashboard criado: id={dash_id}")

    for cid in all_chart_ids:
        requests.put(f"{BASE}/api/v1/chart/{cid}", headers=h(token), json={"dashboards": [dash_id]})

    r = requests.put(f"{BASE}/api/v1/dashboard/{dash_id}", headers=h(token), json={
        "json_metadata": json.dumps(build_metadata(ds_receita_mensal)),
    })
    if r.status_code == 200:
        print("Filtro nativo aplicado.")
    else:
        print("Erro ao aplicar filtro:", r.json())

    print(f"\nAcesse: http://localhost:8088/superset/dashboard/{dash_id}/")


if __name__ == "__main__":
    main()
