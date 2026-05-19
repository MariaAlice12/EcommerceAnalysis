"""Definições declarativas de datasets, charts e dashboard."""

import json

DB_ID = 1
SCHEMA = "ecommerce"
DASHBOARD_TITLE = "E-commerce — Análise de Vendas"
DASHBOARD_SLUG = "ecommerce-vendas"

# ── Datasets ──────────────────────────────────────────────────────────────────

_MES_BASE_SQL = """
    SELECT
        DATE_FORMAT(data_pedido, '%Y-%m-01') AS mes,
        DATE_FORMAT(data_pedido, '%b/%Y')    AS mes_label,
        ROUND(SUM(valor_total), 2)           AS receita,
        COUNT(*)                             AS total_pedidos,
        ROUND(AVG(valor_total), 2)           AS ticket_medio
    FROM pedidos
    WHERE status != 'cancelado'
    GROUP BY mes, mes_label
"""

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
    "receita_mensal": f"""
        WITH base AS ({_MES_BASE_SQL})
        SELECT
            mes,
            mes_label,
            receita,
            total_pedidos,
            ticket_medio,
            ROUND(
                (receita - LAG(receita) OVER (ORDER BY mes))
                / LAG(receita) OVER (ORDER BY mes) * 100,
                2
            ) AS variacao_pct
        FROM base
        ORDER BY mes
    """,
    # Produz uma linha por par de meses (a < b). Os filtros nativos "Mês Base" e
    # "Mês de Comparação" injetam WHERE mes_base = X AND mes_comparacao = Y na
    # query externa, retornando exatamente a linha do par escolhido.
    "comparacao_mensal": f"""
        SELECT
            a.mes_label                                                            AS mes_base,
            b.mes_label                                                            AS mes_comparacao,
            a.receita                                                              AS receita_base,
            b.receita                                                              AS receita_comparacao,
            ROUND((b.receita - a.receita) / a.receita * 100, 2)                   AS var_receita_pct,
            a.total_pedidos                                                        AS pedidos_base,
            b.total_pedidos                                                        AS pedidos_comparacao,
            ROUND((b.total_pedidos - a.total_pedidos) / a.total_pedidos * 100, 2) AS var_pedidos_pct,
            a.ticket_medio                                                         AS ticket_base,
            b.ticket_medio                                                         AS ticket_comparacao,
            ROUND((b.ticket_medio - a.ticket_medio) / a.ticket_medio * 100, 2)    AS var_ticket_pct
        FROM ({_MES_BASE_SQL}) a
        CROSS JOIN ({_MES_BASE_SQL}) b
        WHERE a.mes < b.mes
        ORDER BY a.mes, b.mes
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
        "viz_type": "mixed_timeseries",
        "dataset": "receita_mensal",
        "params": {
            "viz_type": "mixed_timeseries",
            "granularity_sqla": "mes",
            "time_grain_sqla": "P1M",
            "time_range": "No filter",
            "metrics": [
                {
                    "expressionType": "SIMPLE",
                    "column": {"column_name": "receita"},
                    "aggregate": "SUM",
                    "label": "Receita",
                }
            ],
            "groupby": [],
            "metrics_b": [
                {
                    "expressionType": "SIMPLE",
                    "column": {"column_name": "variacao_pct"},
                    "aggregate": "AVG",
                    "label": "Variação %",
                }
            ],
            "groupby_b": [],
            "seriesType": "bar",
            "seriesTypeB": "line",
            "yAxisIndex": 0,
            "yAxisIndexB": 1,
            "y_axis_format": "SMART_NUMBER",
            "y_axis_2_format": ".1f",
            "color_scheme": "supersetColors",
            "rich_tooltip": True,
            "show_legend": True,
        },
    },
    {
        "name": "Tabela Comparativa",
        "viz_type": "table",
        "dataset": "comparacao_mensal",
        "params": {
            "viz_type": "table",
            "query_mode": "raw",
            "all_columns": [
                "mes_base",
                "mes_comparacao",
                "receita_base",
                "receita_comparacao",
                "var_receita_pct",
                "pedidos_base",
                "pedidos_comparacao",
                "var_pedidos_pct",
                "ticket_base",
                "ticket_comparacao",
                "var_ticket_pct",
            ],
            "order_by_cols": [],
            "row_limit": 100,
            "server_pagination": False,
            "show_totals": False,
            "show_cell_bars": False,
            "include_search": False,
            "page_length": 0,
            "column_config": {
                "receita_base":        {"d3NumberFormat": ",.2f"},
                "receita_comparacao":  {"d3NumberFormat": ",.2f"},
                "ticket_base":         {"d3NumberFormat": ",.2f"},
                "ticket_comparacao":   {"d3NumberFormat": ",.2f"},
                "var_receita_pct":     {"d3NumberFormat": "+.2f", "colorPositiveNegative": True},
                "var_pedidos_pct":     {"d3NumberFormat": "+.2f", "colorPositiveNegative": True},
                "var_ticket_pct":      {"d3NumberFormat": "+.2f", "colorPositiveNegative": True},
            },
            "conditional_formatting": [
                {"operator": ">", "targetValue": 0, "colorScheme": "#ACE1AF", "column": "var_receita_pct"},
                {"operator": "<", "targetValue": 0, "colorScheme": "#FFA8A8", "column": "var_receita_pct"},
                {"operator": ">", "targetValue": 0, "colorScheme": "#ACE1AF", "column": "var_pedidos_pct"},
                {"operator": "<", "targetValue": 0, "colorScheme": "#FFA8A8", "column": "var_pedidos_pct"},
                {"operator": ">", "targetValue": 0, "colorScheme": "#ACE1AF", "column": "var_ticket_pct"},
                {"operator": "<", "targetValue": 0, "colorScheme": "#FFA8A8", "column": "var_ticket_pct"},
            ],
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
    tc = chart_ids["Tabela Comparativa"]

    return {
        "ROOT_ID": {"id": "ROOT_ID", "type": "ROOT", "children": ["GRID_ID"]},
        "GRID_ID": {"id": "GRID_ID", "type": "GRID", "children": ["TABS_ID"]},
        "TABS_ID": {"id": "TABS_ID", "type": "TABS", "children": ["TAB_1"]},
        "TAB_1": {
            "id": "TAB_1",
            "type": "TAB",
            "meta": {"text": "1. Visão Geral"},
            "children": ["ROW_1_1", "ROW_1_2", "ROW_1_3"],
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
        "ROW_1_3": {
            "id": "ROW_1_3",
            "type": "ROW",
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "children": [f"CHART-{tc}"],
        },
        f"CHART-{tc}": component("Tabela Comparativa", 12, 20),
    }


def build_metadata(ds_id_receita_mensal: int, ds_id_comparacao: int, chart_ids: dict) -> dict:
    empty_mask = {"extraFormData": {}, "filterState": {}, "ownState": {}}
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
                "defaultDataMask": empty_mask,
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
            },
            {
                "id": "NATIVE_FILTER-mes_base",
                "name": "Mês Base",
                "type": "NATIVE_FILTER",
                "filterType": "filter_select",
                "description": "Mês de referência (ponto de partida da comparação)",
                "targets": [
                    {"datasetId": ds_id_comparacao, "column": {"name": "mes_base"}},
                ],
                "defaultDataMask": empty_mask,
                "controlValues": {
                    "enableEmptyFilter": False,
                    "defaultToFirstItem": False,
                    "creatable": False,
                    "multiSelect": False,
                    "searchAllOptions": False,
                    "inverseSelection": False,
                },
                "cascadeParentIds": [],
                "scope": {"rootPath": ["ROOT_ID"], "excluded": []},
            },
            {
                "id": "NATIVE_FILTER-mes_comparacao",
                "name": "Mês de Comparação",
                "type": "NATIVE_FILTER",
                "filterType": "filter_select",
                "description": "Mês a ser comparado com o Mês Base",
                "targets": [
                    {"datasetId": ds_id_comparacao, "column": {"name": "mes_comparacao"}},
                ],
                "defaultDataMask": empty_mask,
                "controlValues": {
                    "enableEmptyFilter": False,
                    "defaultToFirstItem": False,
                    "creatable": False,
                    "multiSelect": False,
                    "searchAllOptions": False,
                    "inverseSelection": False,
                },
                "cascadeParentIds": [],
                "scope": {"rootPath": ["ROOT_ID"], "excluded": []},
            },
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
