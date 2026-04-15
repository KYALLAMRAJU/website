"""
Gunicorn configuration for Advaitam — AWS EC2 t4g.micro (2 vCPU, 1GB RAM)  # change this line according to your company (update instance type and specs)

Tuning rationale:
  - t4g.micro has 1GB RAM total.   # change this line according to your company (update based on your server RAM)
  - Each sync worker uses ~80-120MB.
  - Formula 2*CPU+1 = 5 workers × 120MB = 600MB RAM → risky on 1GB.
  - Using 2 workers + 2 threads each gives 4 concurrent requests safely.  # change this line according to your company
  - preload_app=True saves ~60MB via Python copy-on-write fork semantics.

Socket: /run/advaitam/gunicorn.sock  (Nginx proxies to this Unix socket)  # change this line according to your company (update socket name)
"""

# ========== BINDING ==========
bind = "unix:/run/advaitam/gunicorn.sock"  # change this line according to your company (update socket path to match your project name)

# ========== WORKER CONFIGURATION ==========
workers = (
    2  # change this line according to your company (adjust based on your server CPU count: 2*CPU+1)
)
threads = 2  # change this line according to your company (adjust based on your server specs)
worker_class = "sync"  # change this line according to your company (use "gevent" or "gthread" for async workloads)
worker_connections = (
    500  # change this line according to your company (adjust based on expected traffic)
)

# ========== TIMEOUTS ==========
timeout = 120  # change this line according to your company (adjust based on your longest request)
graceful_timeout = (
    30  # change this line according to your company (adjust based on your request patterns)
)
keepalive = 5

# ========== MEMORY MANAGEMENT ==========
max_requests = (
    1000  # change this line according to your company (adjust worker recycling frequency)
)
max_requests_jitter = 50
preload_app = True
worker_tmp_dir = "/dev/shm"

# ========== LOGGING ==========
accesslog = "/home/advaitam/app/logs/gunicorn_access.log"  # change this line according to your company (update to your app logs path)
errorlog = "/home/advaitam/app/logs/gunicorn_error.log"  # change this line according to your company (update to your app logs path)
loglevel = "warning"  # change this line according to your company (use "info" or "debug" for more verbose logging)
capture_output = True
