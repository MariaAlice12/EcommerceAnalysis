FROM apache/superset:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
        default-libmysqlclient-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir \
        --target=/app/.venv/lib/python3.10/site-packages \
        mysqlclient PyMySQL

COPY docker-init.sh /app/docker-init.sh
RUN chmod +x /app/docker-init.sh

USER superset
CMD ["/bin/bash", "/app/docker-init.sh"]
