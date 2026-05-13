#!/usr/bin/env python3
"""Entry point único: cria ou atualiza datasets, charts e dashboard no Superset."""

import json
import sys

from config import (
    CHARTS,
    DASHBOARD_SLUG,
    DASHBOARD_TITLE,
    DATASETS,
    DB_ID,
    SCHEMA,
    build_layout,
    build_metadata,
)
from superset_client import SupersetClient


def main():
    client = SupersetClient()

    # ── Datasets ──────────────────────────────────────────────────────────────
    print("── Datasets ──────────────────────────────────────────")
    ds_ids = {}
    for name, sql in DATASETS.items():
        try:
            ds_id, action = client.upsert_dataset(name, sql, SCHEMA, DB_ID)
            ds_ids[name] = ds_id
            print(f"  {action:8}  {name} (id={ds_id})")
        except RuntimeError as e:
            print(f"  ERRO  {e}", file=sys.stderr)
            sys.exit(1)

    # ── Charts ────────────────────────────────────────────────────────────────
    print("\n── Charts ────────────────────────────────────────────")
    chart_ids = {}
    for chart in CHARTS:
        ds_id = ds_ids[chart["dataset"]]
        params = json.dumps({**chart["params"], "viz_type": chart["viz_type"]})
        try:
            chart_id, action = client.upsert_chart(chart["name"], chart["viz_type"], ds_id, params)
            chart_ids[chart["name"]] = chart_id
            print(f"  {action:8}  {chart['name']} (id={chart_id})")
        except RuntimeError as e:
            print(f"  ERRO  {e}", file=sys.stderr)
            sys.exit(1)

    # ── Dashboard ─────────────────────────────────────────────────────────────
    print("\n── Dashboard ─────────────────────────────────────────")
    position_json = json.dumps(build_layout(chart_ids))
    metadata = json.dumps(build_metadata(ds_ids["receita_mensal"], chart_ids))

    try:
        dash_id, action = client.upsert_dashboard(
            DASHBOARD_TITLE, DASHBOARD_SLUG, list(chart_ids.values()), position_json, metadata
        )
        print(f"  {action:8}  '{DASHBOARD_TITLE}' (id={dash_id})")
    except RuntimeError as e:
        print(f"  ERRO  {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n✓ Concluído — http://localhost:8088/superset/dashboard/{dash_id}/")


if __name__ == "__main__":
    main()
