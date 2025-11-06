# Devops for Cloud Assignment

This project demonstrates the full lifecycle of a simple Python **Flask** application, including:
1.  **Backend Application** setup with Flask.
2.  **Dockerization** of the application.
3.  **Kubernetes Deployment** with a **ConfigMap** and **LoadBalancer Service**.
4.  **Prometheus Monitoring** setup on the Kubernetes cluster.

[cite_start]The Flask application exposes a single endpoint, `/get_info`, which returns the application title and version [cite: 922, 924-927].

## Project Structure

The project includes the following core files:
├── main.py # Flask application code 
├── requirements.txt # Python dependencies 
├── Dockerfile # Instructions for building the Docker image 
├── config-2024mt03541.yaml # Kubernetes ConfigMap for environment variables 
├── dep-2024mt03541.yaml # Kubernetes Deployment for the Flask application 
├── svc-2024mt03541.yaml # Kubernetes LoadBalancer Service 
├── prometheus-config.yaml # Prometheus configuration file 
├── prometheus-deployment.yaml # Kubernetes Deployment for Prometheus 
└── prometheus-service.yaml # Kubernetes Service for Prometheus UI access

## 1. Backend Application (Flask)

### Prerequisites

* Python 3.11+
* `pip`

### Step 1: Project Setup

```bash
mkdir app-2024mt03541
cd app-2024mt03541
touch main.py
Step 2: Install Dependencies
Create a requirements.txt file (if not using pip install directly):

requirements.txt

Plaintext

flask>=3.1.x
python-dotenv>=1.0
Install dependencies:

Bash

pip install flask uvicorn python-dotenv
# or using requirements file
python -m pip install -r requirements.txt
Step 3: main.py
This file contains the simple Flask application .

Python

import os
from flask import Flask, jsonify

app = Flask(__name__)

# Get environment variables or set default
APP_VERSION = os.getenv('APP_VERSION', '1.0')
APP_TITLE = os.getenv('APP_TITLE', 'Devops for Cloud Assignment')

@app.route('/get_info', methods=['GET'])
def get_info():
    return jsonify({
        "APP_TITLE": APP_TITLE,
        "APP_VERSION": APP_VERSION
    })

if __name__ == "__main__":
    # Important: host='0.0.0.0' allows access from outside the container/pod
    app.run(host='0.0.0.0', port=8000)
Step 4: Run Application
Bash

python main.py
Access the endpoint in your browser: http://localhost:8000/get_info.

2. Dockerization
Step 1: Dockerfile
Dockerfile

# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY main.py .

# Install Flask (using a minimal set of requirements for simplicity)
# Install Flask & additional dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]
Step 2: Build and Run
Build the Docker image:

Bash

docker build -t img-2024mt03541 .
Run the container, mapping port 8000:

Bash

docker run -d --name cnr-2024mt03541 -p 8000:8000 img-2024mt03541
Verify the container is running:

Bash

docker ps
Verify the application is accessible: http://localhost:8000/get_info.

3. Kubernetes Deployment
This setup deploys the containerized application to Kubernetes (e.g., Minikube) with 2 replicas and exposes it via a LoadBalancer Service.


Prerequisites
A running Kubernetes cluster (e.g., Minikube).

kubectl

Step 1: ConfigMap (config-2024mt03541.yaml)
Defines environment variables for the application .

YAML

apiVersion: v1
kind: ConfigMap
metadata:
  name: config-2024mt03541
data:
  APP_VERSION: "1.0"
  APP_TITLE: "Devops for Cloud Assignment"
Step 2: Deployment (dep-2024mt03541.yaml)
Defines the deployment with 2 replicas and mounts the ConfigMap as environment variables .

YAML

apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-2024mt03541
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: flask-container
        image: img-2024mt03541
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: config-2024mt03541

Step 3: Service (svc-2024mt03541.yaml)
Exposes the deployment using a LoadBalancer type, routing port 80 externally to the container port 8000 .

YAML

apiVersion: v1
kind: Service
metadata:
  name: svc-2024mt03541
spec:
  type: LoadBalancer
  selector:
    app: flask-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
Step 4: Apply and Verify
Apply the configuration files:

Bash

kubectl apply -f config-2024mt03541.yaml
kubectl apply -f dep-2024mt03541.yaml
kubectl apply -f svc-2024mt03541.yaml
Verify the pods and service status:

Bash

kubectl get pods
kubectl get svc
Access the application via the LoadBalancer IP/NodePort (for Minikube, use minikube ip):

Bash

# Example access using Minikube IP
http://<minikube_ip>/get_info
4. Prometheus Monitoring
Step 1: Install Prometheus (Using Helm)
Use Helm to install Prometheus into a dedicated namespace.


Bash

kubectl create namespace prometheus
helm repo add prometheus-community [https://prometheus-community.github.io/helm-charts](https://prometheus-community.github.io/helm-charts)
helm repo update
helm install prometheus prometheus-community/prometheus -n prometheus
Step 2: Configuration (prometheus-config.yaml)
This configures Prometheus to scrape the Flask application pods labeled app: flask-app .

YAML

global:
  scrape_interval: 5s
scrape_configs:
# Scrape configuration for Flask app pods
- job_name: 'flask-app'
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  # Keep only the flask-app pods
  - source_labels: [__meta_kubernetes_pod_label_app]
    action: keep
    regex: flask-app
  # Replace pod IP and port to target the application on port 8000
  - source_labels: [__meta_kubernetes_pod_ip]
    target_label: __address__
    regex: (.*)
    replacement: ${1}:8000
Step 3: Apply Prometheus Configuration (Alternative/Manual Deployment)
The following YAMLs define a manual deployment and service for Prometheus, using the configuration above.

prometheus-deployment.yaml

YAML

# ... (Deployment object for Prometheus using prom/prometheus:latest image)
# ... (Mounts prometheus-config as a volume)
prometheus-service.yaml

YAML

# ... (Service object to expose Prometheus UI on NodePort 30090 or via port-forward)
Apply the manual configuration:

Bash

# If using the manual deployment files:
kubectl apply -f prometheus-config.yaml
kubectl apply -f prometheus-deployment.yaml
kubectl apply -f prometheus-service.yaml
Step 4: Access Prometheus UI
Use port-forwarding to access the Prometheus server locally:

Bash

kubectl port-forward --address 0.0.0.0 service/prometheus-server -n prometheus 9090:80
Open the Prometheus UI in your browser: http://localhost:9090/.