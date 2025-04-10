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
workers_per_core = env.float("GUNICORN_WORKERS_PER_CORE", 2)
max_workers = env.int("GUNICORN_MAX_WORKERS", 8)
web_concurrency = env.int("GUNICORN_WEB_CONCURRENCY", None)

# Calculate the number of workers if web_concurrency is not explicitly set
if not web_concurrency:
    cores = multiprocessing.cpu_count()
    web_concurrency = min(max_workers, int(cores * workers_per_core))

# Set workers based on web concurrency
workers = web_concurrency

# Always bind to 0.0.0.0 and use port from environment or default to 8000
# First try GUNICORN_PORT, then fallback to DJANGO_PORT for backward compatibility
port = env.str("GUNICORN_PORT", env.str("DJANGO_PORT", "8000"))
bind = f"0.0.0.0:{port}"

# Other Gunicorn settings with sensible defaults
keepalive = env.int("GUNICORN_KEEPALIVE", 5)
timeout = env.int("GUNICORN_TIMEOUT", 120)  # Set to 120s to match docker-entrypoint.sh fallback
graceful_timeout = env.int("GUNICORN_GRACEFUL_TIMEOUT", 120)  # Set to 120s to match docker-entrypoint.sh fallback

# Log configuration
accesslog = env.str("GUNICORN_ACCESS_LOG", "-")  # - means stdout
errorlog = env.str("GUNICORN_ERROR_LOG", "-")    # - means stderr
loglevel = env.str("GUNICORN_LOG_LEVEL", "info")

# Thread configuration
threads = env.int("GUNICORN_THREADS", 4)

# Worker class - use gthread by default for better handling of blocking operations
worker_class = env.str("GUNICORN_WORKER_CLASS", "gthread")

# Load application
wsgi_app = "ropon.wsgi:application"