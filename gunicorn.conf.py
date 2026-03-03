"""
Gunicorn configuration for Advaitam — AWS EC2 t4g.micro (2 vCPU, 1GB RAM)

Tuning rationale:
  - t4g.micro has 1GB RAM total.
  - Each sync worker uses ~80-120MB.
  - Formula 2*CPU+1 = 5 workers × 120MB = 600MB RAM → risky on 1GB.
  - Using 2 workers + 2 threads each gives 4 concurrent requests safely.
  - preload_app=True saves ~60MB via Python copy-on-write fork semantics.

Socket: /run/advaitam/gunicorn.sock  (Nginx proxies to this Unix socket)
"""

# ========== BINDING ==========
# Unix socket — faster than TCP for same-machine Nginx → Gunicorn IPC
bind = "unix:/run/advaitam/gunicorn.sock"

# ========== WORKER CONFIGURATION ==========
# DO NOT use the 2*CPU+1 formula for t4g.micro — it causes OOM.
# 2 workers × 2 threads = 4 concurrent requests, ~240-280MB total RAM usage.
workers = 2
threads = 2
worker_class = "sync"
worker_connections = 500

# ========== TIMEOUTS ==========
timeout = 120  # Kill worker if request takes > 120s (audio streaming needs this)
graceful_timeout = 30  # Give workers 30s to finish in-flight requests on reload
keepalive = 5  # Keep connections alive for 5s (behind Nginx, this is fine)

# ========== MEMORY MANAGEMENT ==========
# Recycle workers periodically to prevent slow memory leaks
max_requests = 1000
max_requests_jitter = 50  # Stagger recycling to avoid simultaneous restarts
preload_app = True  # Load Django app before forking → saves ~60MB via CoW
worker_tmp_dir = "/dev/shm"  # Use RAM-based tmpfs for heartbeat files (faster)

# ========== LOGGING ==========
accesslog = "/home/advaitam/app/logs/gunicorn_access.log"
errorlog = "/home/advaitam/app/logs/gunicorn_error.log"
loglevel = "warning"
capture_output = True  # Redirect Django print() / stderr to error log
