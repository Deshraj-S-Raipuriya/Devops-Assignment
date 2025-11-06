from flask import Flask, jsonify, Response
import os
import time
import psutil
import socket
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Initialize Flask app
app = Flask(__name__)

# Environment variables
APP_VERSION = os.getenv('APP_VERSION', '1.0')
APP_TITLE = os.getenv('APP_TITLE', 'DevOps for Cloud Assignment')

# Identify pod name (Kubernetes injects HOSTNAME automatically)
POD_NAME = os.getenv('HOSTNAME', socket.gethostname())

# Prometheus Metrics (with labels)
REQUEST_COUNT = Counter(
    "request_count_total",
    "Total number of requests handled by each pod",
    ["pod"]
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    ["pod"]
)

CPU_UTILIZATION = Gauge(
    "cpu_utilization_percent",
    "Current CPU utilization percentage",
    ["pod"]
)
MEMORY_USAGE = Gauge(
    "memory_usage_mb",
    "Current memory usage in MB",
    ["pod"]
)

# Endpoint: /get_info
@app.route('/get_info', methods=['GET'])
def get_info():
    start_time = time.time()
    try:
        REQUEST_COUNT.labels(pod=POD_NAME).inc()
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)

        # Update gauges
        CPU_UTILIZATION.labels(pod=POD_NAME).set(cpu_usage)
        MEMORY_USAGE.labels(pod=POD_NAME).set(memory_usage)

        response = jsonify({
            "APP_TITLE": APP_TITLE,
            "APP_VERSION": APP_VERSION,
            "POD_NAME": POD_NAME,
            "CPU_UTILIZATION": cpu_usage,
            "MEMORY_USAGE_MB": round(memory_usage, 2)
        })
        response.status_code = 200
    except Exception as e:
        response = jsonify({"error": str(e)})
        response.status_code = 500
    finally:
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(pod=POD_NAME).observe(latency)
    return response

# Prometheus metrics endpoint
@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
