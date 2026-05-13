"""Definições declarativas de datasets, charts e dashboard."""

import json

DB_ID = 1
SCHEMA = "ecommerce"
DASHBOARD_TITLE = "E-commerce — Análise de Vendas"
DASHBOARD_SLUG = "ecommerce-vendas"

# ── Datasets ──────────────────────────────────────────────────────────────────

DATASETS = {
    "kpis_visao_geral": """
        SELECT
            DATE_FORMAT(data_pedido, '%b/%Y') AS mes_label,
            SUM(valor_total)                  AS receita_total,
            COUNT(*)                          AS total_pedidos,
            ROUND(AVG(valor_total), 2)        AS ticket_medio
        FROM pedidos
        WHERE status != 'cancelado'
        GROUP BY mes_label
    """,
    "receita_mensal": """
        SELECT
            DATE_FORMAT(data_pedido, '%Y-%m-01') AS mes,
            DATE_FORMAT(data_pedido, '%b/%Y')    AS mes_label,
            ROUND(SUM(valor_total), 2)           AS receita,
            COUNT(*)                             AS total_pedidos,
            ROUND(AVG(valor_total), 2)           AS ticket_medio
        FROM pedidos
        WHERE status != 'cancelado'
        GROUP BY mes, mes_label
        ORDER BY mes
    """,
}

# ── Charts ────────────────────────────────────────────────────────────────────
# "dataset" referencia a chave em DATASETS; datasource_id é resolvido em runtime.

CHARTS = [
    {
        "name": "Receita Total",
        "viz_type": "big_number_total",
        "dataset": "receita_mensal",
        "params": {
            "viz_type": "big_number_total",
            "metric": {
                "expressionType": "SIMPLE",
                "column": {"column_name": "receita"},
                "aggregate": "SUM",
                "label": "Receita Total",
            },
            "subheader": "Pedidos entregues e em trânsito",
            "y_axis_format": "SMART_NUMBER",
            "header_font_size": 0.4,
            "subheader_font_size": 0.15,
            "color_scheme": "supersetColors",
        },
    },
    {
        "name": "Total de Pedidos",
        "viz_type": "big_number_total",
        "dataset": "receita_mensal",
        "params": {
            "viz_type": "big_number_total",
            "metric": {
                "expressionType": "SIMPLE",
                "column": {"column_name": "total_pedidos"},
                "aggregate": "SUM",
                "label": "Total de Pedidos",
            },
            "subheader": "Excluindo cancelados",
            "y_axis_format": ",d",
            "header_font_size": 0.4,
            "subheader_font_size": 0.15,
            "color_scheme": "supersetColors",
        },
    },
    {
        "name": "Ticket Médio",
        "viz_type": "big_number_total",
        "dataset": "receita_mensal",
        "params": {
            "viz_type": "big_number_total",
            "metric": {
                "expressionType": "SQL",
                "sqlExpression": "SUM(receita) / SUM(total_pedidos)",
                "label": "Ticket Médio",
            },
            "subheader": "Valor médio por pedido",
            "y_axis_format": "SMART_NUMBER",
            "header_font_size": 0.4,
            "subheader_font_size": 0.15,
            "color_scheme": "supersetColors",
        },
    },
    {
        "name": "Receita Mensal",
        "viz_type": "echarts_timeseries_bar",
        "dataset": "receita_mensal",
        "params": {
            "viz_type": "echarts_timeseries_bar",
            "x_axis": "mes_label",
            "metrics": [
                {
                    "expressionType": "SIMPLE",
                    "column": {"column_name": "receita"},
                    "aggregate": "SUM",
                    "label": "Receita",
                }
            ],
            "x_axis_time_format": "%b/%Y",
            "y_axis_format": "SMART_NUMBER",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": False,
        },
    },
]

# ── Layout e metadados do dashboard ──────────────────────────────────────────


def build_layout(chart_ids: dict) -> dict:
    """
    Monta o position_json do dashboard.
    chart_ids: {nome_do_chart: id_no_superset}
    """

    def component(name, width, height):
        cid = chart_ids[name]
        return {
            "id": f"CHART-{cid}",
            "type": "CHART",
            "meta": {"chartId": cid, "sliceId": cid, "width": width, "height": height},
            "children": [],
        }

    rt = chart_ids["Receita Total"]
    tp = chart_ids["Total de Pedidos"]
    tm = chart_ids["Ticket Médio"]
    rm = chart_ids["Receita Mensal"]

    return {
        "ROOT_ID": {"id": "ROOT_ID", "type": "ROOT", "children": ["GRID_ID"]},
        "GRID_ID": {"id": "GRID_ID", "type": "GRID", "children": ["TABS_ID"]},
        "TABS_ID": {"id": "TABS_ID", "type": "TABS", "children": ["TAB_1"]},
        "TAB_1": {
            "id": "TAB_1",
            "type": "TAB",
            "meta": {"text": "1. Visão Geral"},
            "children": ["ROW_1_1", "ROW_1_2"],
        },
        "ROW_1_1": {
            "id": "ROW_1_1",
            "type": "ROW",
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "children": [f"CHART-{rt}", f"CHART-{tp}", f"CHART-{tm}"],
        },
        f"CHART-{rt}": component("Receita Total", 4, 18),
        f"CHART-{tp}": component("Total de Pedidos", 4, 18),
        f"CHART-{tm}": component("Ticket Médio", 4, 18),
        "ROW_1_2": {
            "id": "ROW_1_2",
            "type": "ROW",
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "children": [f"CHART-{rm}"],
        },
        f"CHART-{rm}": component("Receita Mensal", 12, 28),
    }


def build_metadata(ds_id_receita_mensal: int, chart_ids: dict) -> dict:
    return {
        "native_filter_configuration": [
            {
                "id": "NATIVE_FILTER-mes_label",
                "name": "Mês",
                "type": "NATIVE_FILTER",
                "filterType": "filter_select",
                "description": "",
                "targets": [
                    {"datasetId": ds_id_receita_mensal, "column": {"name": "mes_label"}},
                ],
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
                "scope": {"rootPath": ["ROOT_ID"], "excluded": []},
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
