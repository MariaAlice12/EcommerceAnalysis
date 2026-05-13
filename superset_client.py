"""Wrapper da API REST do Superset com upsert idempotente."""

import requests


class SupersetClient:
    def __init__(self, base="http://localhost:8088", username="admin", password="admin"):
        self.base = base
        self.username = username
        self.password = password
        self._token = None
        self._csrf = None

    @property
    def _headers(self):
        if not self._token:
            r = requests.post(f"{self.base}/api/v1/security/login", json={
                "username": self.username,
                "password": self.password,
                "provider": "db",
                "refresh": True,
            })
            r.raise_for_status()
            self._token = r.json()["access_token"]

            csrf = requests.get(
                f"{self.base}/api/v1/security/csrf_token/",
                headers={"Authorization": f"Bearer {self._token}"},
            )
            csrf.raise_for_status()
            self._csrf = csrf.json()["result"]

        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "X-CSRFToken": self._csrf,
            "Referer": self.base,
        }

    def _list(self, resource: str) -> list:
        r = requests.get(
            f"{self.base}/api/v1/{resource}/?q=(page_size:100)",
            headers=self._headers,
        )
        return r.json().get("result", [])

    def upsert_dataset(self, name: str, sql: str, schema: str, db_id: int) -> tuple[int, str]:
        existing = next((d for d in self._list("dataset") if d["table_name"] == name), None)
        create_payload = {"database": db_id, "schema": schema, "sql": sql.strip(), "table_name": name}
        update_payload = {"database_id": db_id, "schema": schema, "sql": sql.strip(), "table_name": name}

        if existing:
            requests.put(
                f"{self.base}/api/v1/dataset/{existing['id']}",
                headers=self._headers,
                json=update_payload,
            )
            ds_id = existing["id"]
            action = "updated"
        else:
            r = requests.post(f"{self.base}/api/v1/dataset/", headers=self._headers, json=create_payload)
            body = r.json()
            if "id" not in body:
                raise RuntimeError(f"Erro ao criar dataset '{name}': {body}")
            ds_id = body["id"]
            action = "created"

        requests.put(f"{self.base}/api/v1/dataset/{ds_id}/refresh", headers=self._headers)
        self._sync_columns(ds_id, sql)
        return ds_id, action

    def _sync_columns(self, ds_id: int, sql: str) -> None:
        """Add columns derived from SQL that the refresh endpoint misses on virtual datasets."""
        import re
        r = requests.get(f"{self.base}/api/v1/dataset/{ds_id}", headers=self._headers)
        current = {c["column_name"]: c for c in r.json()["result"]["columns"]}

        aliases = re.findall(r"\bAS\s+(\w+)", sql, re.IGNORECASE)
        missing = [a for a in aliases if a not in current]
        if not missing:
            return

        # existing columns: preserve id so the API updates instead of recreates
        keep = [{"id": c["id"], "column_name": c["column_name"]} for c in current.values()]
        new = [{"column_name": a, "type": "DOUBLE", "is_dttm": False} for a in missing]
        requests.put(
            f"{self.base}/api/v1/dataset/{ds_id}",
            headers=self._headers,
            json={"columns": keep + new},
        )

    def upsert_chart(
        self, name: str, viz_type: str, ds_id: int, params: str
    ) -> tuple[int, str]:
        existing = next((c for c in self._list("chart") if c["slice_name"] == name), None)
        payload = {
            "slice_name": name,
            "viz_type": viz_type,
            "datasource_id": ds_id,
            "datasource_type": "table",
            "params": params,
        }

        if existing:
            requests.put(
                f"{self.base}/api/v1/chart/{existing['id']}",
                headers=self._headers,
                json=payload,
            )
            chart_id = existing["id"]
            action = "updated"
        else:
            r = requests.post(f"{self.base}/api/v1/chart/", headers=self._headers, json=payload)
            body = r.json()
            if "id" not in body:
                raise RuntimeError(f"Erro ao criar chart '{name}': {body}")
            chart_id = body["id"]
            action = "created"

        return chart_id, action

    def upsert_dashboard(
        self,
        title: str,
        slug: str,
        chart_ids: list[int],
        position_json: str,
        metadata: str,
    ) -> tuple[int, str]:
        existing = next((d for d in self._list("dashboard") if d.get("slug") == slug), None)
        payload = {
            "dashboard_title": title,
            "published": True,
            "slug": slug,
            "position_json": position_json,
            "json_metadata": metadata,
        }

        if existing:
            requests.put(
                f"{self.base}/api/v1/dashboard/{existing['id']}",
                headers=self._headers,
                json=payload,
            )
            dash_id = existing["id"]
            action = "updated"
        else:
            r = requests.post(f"{self.base}/api/v1/dashboard/", headers=self._headers, json=payload)
            body = r.json()
            if "id" not in body:
                raise RuntimeError(f"Erro ao criar dashboard: {body}")
            dash_id = body["id"]
            action = "created"

        for cid in chart_ids:
            requests.put(
                f"{self.base}/api/v1/chart/{cid}",
                headers=self._headers,
                json={"dashboards": [dash_id]},
            )

        return dash_id, action
