# AI Chatbot Management System

An end‑to‑end AI chatbot management platform built with **Flask**, **Rasa 3.x**, **TensorFlow 2.12**, and containerized with **Docker**, with optional deployment manifests for **Kubernetes**.  

This project lets you train an NLU model with Rasa, manage agents via a web UI, and chat with the bot through a browser.

***

## Features

- Web UI built with **Flask** for chatting with the bot and managing agents.  
- **Rasa NLU** integration for intent classification and entity extraction.  
- Simple training script to build a Rasa model from the `rasa_project` directory.  
- **SQLite** (via SQLAlchemy) for lightweight data storage.  
- **Dockerfile** for containerizing the entire app.  
- Minimal **Kubernetes Deployment + Service** manifests for orchestration.

***

## Project Structure

```text
AI-CHATBOT-MGMT/
├── app.py               # Flask entrypoint
├── requirements.txt     # Python dependencies
├── train_rasa.py        # Script to train Rasa NLU model
├── rasa_project/        # Rasa config, NLU data, etc.
├── models/              # Trained Rasa models (generated)
├── scripts/             # Rasa integration, DB models, helpers
├── templates/           # HTML templates (Flask)
├── static/              # CSS, JS, images
├── Dockerfile           # Container definition
├── k8s-deployment.yaml  # Kubernetes Deployment
└── k8s-service.yaml     # Kubernetes Service
```

***

## Prerequisites

- Python 3.10  
- pip  
- Docker Desktop (for containerization)  
- (Optional) A local Kubernetes cluster (Docker Desktop Kubernetes / Minikube)  

***

## 1. Local Development (without Docker)

### Create and activate virtual environment

```bash
python -m venv myenv
# Windows (PowerShell)
.\myenv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Train the Rasa NLU model

```bash
python train_rasa.py
```

This creates a model file under `models/` (for example `nlu-YYYYMMDD-HHMMSS-xxxx.tar.gz`).

### Run the Flask app

Make sure `app.py` runs with:

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

Then start:

```bash
python app.py
```

Open your browser at:

```text
http://localhost:5000
```

You should see the chatbot interface where you can start chatting with the trained bot.

***

## 2. Containerization with Docker

### Build the image

```bash
docker build -t ai-chatbot-mgmt:latest .
```

### Run the container

```bash
docker run --rm -p 5000:5000 ai-chatbot-mgmt:latest
```

- The Flask app inside the container listens on `0.0.0.0:5000`.  
- Port `5000` on your host is mapped to port `5000` in the container.

Access the app at:

```text
http://localhost:5000
```

To verify the container is running:

```bash
docker ps
```

You should see `ai-chatbot-mgmt:latest` with `0.0.0.0:5000->5000/tcp`.

***

## 3. Kubernetes (Optional, for Mini‑Project Demonstration)

> These manifests are intentionally minimal and meant for educational/demo purposes.

### Deployment

`k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-chatbot-mgmt
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-chatbot-mgmt
  template:
    metadata:
      labels:
        app: ai-chatbot-mgmt
    spec:
      containers:
        - name: ai-chatbot-mgmt
          image: yourdockerid/ai-chatbot-mgmt:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
```

### Service

`k8s-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-chatbot-mgmt-service
spec:
  type: NodePort
  selector:
    app: ai-chatbot-mgmt
  ports:
    - name: http
      port: 80
      targetPort: 5000
      nodePort: 30080
```

### Apply manifests

Make sure a local Kubernetes cluster is running, then:

```bash
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
kubectl get pods
kubectl get svc ai-chatbot-mgmt-service
```

Access via:

```text
http://localhost:30080
```

(or use your cluster’s node IP if required).

***

## 4. Rasa NLU Details

- Intents, entities, and training examples live under `rasa_project/` (e.g., `nlu.yml`, `config.yml`).  
- `train_rasa.py` wraps the Rasa training command, writing the resulting model to the `models/` directory, which the Flask app loads on startup.  
- The current configuration trains **NLU only** (no stories), which is sufficient for FAQ‑style bots or intent/entity extraction.

***

## 5. Typical Workflow

1. Edit NLU data in `rasa_project/`.  
2. Run `python train_rasa.py` to retrain the model.  
3. Start the app:
   - Locally: `python app.py`, or  
   - In Docker: `docker run -p 5000:5000 ai-chatbot-mgmt:latest`.  
4. Open `http://localhost:5000` and test the chatbot.  
5. (Optional) Deploy the same image to a Kubernetes cluster using the provided YAML files.

***

## 6. Notes & Limitations

- The development server used here (Flask built‑in) is not intended for high‑traffic production.  
- Training large Rasa models may be resource‑intensive; this setup targets mini‑project / demo scale.  
- For real deployments, consider:
  - A production WSGI server (gunicorn/uwsgi).  
  - Separate Rasa services and a dedicated database.  
  - Proper environment variables and secrets management.

***

## 7. How to Mention in Your Report

You can summarise the deployment story as:

- “The chatbot backend is built with Flask and integrates a Rasa NLU model trained using TensorFlow.”  
- “The complete application is containerized using Docker, enabling consistent execution across environments.”  
- “Kubernetes manifests are provided to orchestrate the container, demonstrating how the system could be scaled and managed in a cluster.”

***

Feel free to adjust text, project name, and sections like screenshots or contributors to match your college mini‑project format.