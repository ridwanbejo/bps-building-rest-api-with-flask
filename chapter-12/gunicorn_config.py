import os
import multiprocessing


worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2))
threads = int(os.environ.get('GUNICORN_THREADS', multiprocessing.cpu_count() * 2))  # This setting only affects the gthread worker types.
worker_connection = os.environ.get('GUNICORN_WORKER_CONNECTION', 2000)  # This setting only affects the gthread, eventlet and gevent worker types.
timeout = os.environ.get('GUNICORN_TIMEOUT', 30)
graceful_timeout = os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 30)

bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')

forwarded_allow_ips = '*'

secure_scheme_headers = { 'X-Forwarded-Proto': 'https' }
