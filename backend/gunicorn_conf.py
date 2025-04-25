"""
Gunicorn configuration file for the Wagtail application.

This file reads configuration values from environment variables using environs library.
"""
import multiprocessing
from environs import Env

# Initialize environment variable reader
env = Env()
env.read_env()

# Worker configuration
# Recommended: 2-4 x $(NUM_CORES)
workers_per_core = int(env.str("GUNICORN_WORKERS_PER_CORE", "").strip() or 2)
max_workers = int(env.str("GUNICORN_MAX_WORKERS", "").strip() or 8)
web_concurrency_str = env.str("GUNICORN_WEB_CONCURRENCY", "").strip()
web_concurrency = int(web_concurrency_str) if web_concurrency_str else None

# Calculate the number of workers if web_concurrency is not explicitly set
if not web_concurrency:
    cores = multiprocessing.cpu_count()
    web_concurrency = min(max_workers, int(cores * workers_per_core))

# Set workers based on web concurrency
workers = web_concurrency
# Always bind to 0.0.0.0 and use port from environment or default to 8000
# First try GUNICORN_PORT, then fallback to DJANGO_PORT for backward compatibility
port_str = env.str("GUNICORN_PORT", "").strip() or env.str("DJANGO_PORT", "").strip() or "8000"
port = port_str
bind = f"0.0.0.0:{port}"
# Other Gunicorn settings with sensible defaults
keepalive = int(env.str("GUNICORN_KEEPALIVE", "").strip() or 5)
timeout = int(env.str("GUNICORN_TIMEOUT", "").strip() or 120)  # Set to 120s to match docker-entrypoint.sh fallback
graceful_timeout = int(env.str("GUNICORN_GRACEFUL_TIMEOUT", "").strip() or 120)  # Set to 120s to match docker-entrypoint.sh fallback
timeout = env.int("GUNICORN_TIMEOUT", 120)  # Set to 120s to match docker-entrypoint.sh fallback
# Log configuration
accesslog = env.str("GUNICORN_ACCESS_LOG", "").strip() or "-"  # - means stdout
errorlog = env.str("GUNICORN_ERROR_LOG", "").strip() or "-"    # - means stderr
loglevel = env.str("GUNICORN_LOG_LEVEL", "").strip() or "info"

# Thread configuration
threads = int(env.str("GUNICORN_THREADS", "").strip() or 4)

# Worker class - use gthread by default for better handling of blocking operations
worker_class = env.str("GUNICORN_WORKER_CLASS", "").strip() or "gthread"
# Worker class - use gthread by default for better handling of blocking operations
worker_class = env.str("GUNICORN_WORKER_CLASS", "gthread")

# Load application
wsgi_app = "ropon.wsgi:application"