import multiprocessing
import os

# Server socket
bind = '0.0.0.0:5000'
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 60
keepalive = 5

# Logging
accesslog = '/var/log/gunicorn_access.log'
errorlog = '/var/log/gunicorn_error.log'
loglevel = 'info'

# Process naming
proc_name = 'flask-finance-app'

# Server mechanics
daemon = False
pidfile = '/var/run/gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Application
raw_env = []
