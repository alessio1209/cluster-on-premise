# 🚀 K3s Enterprise GitOps Pipeline

Questo repository contiene l'infrastruttura completa e il codice sorgente per un'applicazione Full-Stack distribuita su un cluster Kubernetes (K3s) on-premise, automatizzata tramite una pipeline CI/CD basata sul paradigma GitOps.

## 🏗️ Architettura del Sistema

Il progetto simula un ambiente di produzione Enterprise, utilizzando strumenti Cloud-Native per garantire automazione, sicurezza e scalabilità.

* **Infrastruttura:** Cluster K3s on-premise (Debian).
* **Continuous Integration (CI):** Jenkins (eseguito nativamente sul cluster tramite Jenkins Kubernetes Plugin e Pod effimeri).
* **Image Building:** Kaniko (per build rootless e sicure all'interno del cluster).
* **Security (DevSecOps):** Trivy (per la scansione delle vulnerabilità del file system).
* **Container Registry:** Docker Hub.
* **Continuous Deployment (CD):** ArgoCD (approccio GitOps puro).
* **Ingress & Routing:** Traefik.

## 🔄 Il Flusso CI/CD (GitOps Workflow)

1.  **Code Commit:** Lo sviluppatore effettua un push del codice sorgente (es. Python/FastAPI o HTML) sul ramo `main` di questo repository.
2.  **Pipeline Trigger:** Jenkins avvia la pipeline definita nel `Jenkinsfile`.
3.  **Security Scan:** Trivy analizza il repository alla ricerca di vulnerabilità.
4.  **Build & Push:** Kaniko costruisce la nuova immagine container taggandola con il Git Commit Hash e la carica su Docker Hub.
5.  **GitOps Update:** Jenkins modifica automaticamente il manifesto Kubernetes (`python-deployment.yaml`), aggiornando il tag dell'immagine con l'ultimo Hash, ed effettua un push automatico sul repository tramite un Service Account / PAT.
6.  **Automated Deployment:** ArgoCD rileva la discrepanza tra lo stato desiderato (su GitHub) e lo stato attuale (sul cluster). Esegue automaticamente la sincronizzazione (Sync) avviando i nuovi Pod ed effettuando un rollout senza interruzioni.

## 📂 Struttura del Repository

* `main.py` / `index.html`: Codice sorgente dell'applicazione e frontend.
* `Dockerfile`: Istruzioni per la containerizzazione dell'applicazione.
* `Jenkinsfile`: Definizione dichiarativa della pipeline di Continuous Integration.
* `python-deployment.yaml`: Manifesto Kubernetes per l'applicazione (Deployment, Service, Ingress), costantemente monitorato da ArgoCD.
* `ansible/`: Script e playbook per la configurazione dei nodi del cluster.
* `k8s/database/`: Manifesti per il deployment del database PostgreSQL.

## 🚀 Come testare il flusso

Per innescare un nuovo rilascio automatico:
1. Modificare l'applicazione (es. aggiornare un titolo in `index.html`).
2. Eseguire il push su GitHub.
3. Avviare la build su Jenkins.
4. Osservare ArgoCD sincronizzare il cluster e applicare la nuova versione in tempo reale.

---
*Progetto realizzato per dimostrare competenze avanzate in ambito Cloud Engineering, Kubernetes e automazione CI/CD.*

