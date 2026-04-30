import os

SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'supersecretkey123changeme')

# Banco de metadados interno do Superset (SQLite para desenvolvimento local)
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset_home/superset.db'

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 1,
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 3600,
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 2,
}

FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
}

# Desabilitado apenas para desenvolvimento local
WTF_CSRF_ENABLED = False
TALISMAN_ENABLED = False
