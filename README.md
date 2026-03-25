# 🚀 Enterprise On-Premise K8s Cluster con GitOps & CI/CD

Questo repository contiene l'intera infrastruttura as Code (IaC), l'applicazione backend e le pipeline di automazione per un cluster Kubernetes on-premise multi-nodo, progettato con architettura GitOps.

## 🏗️ Architettura del Sistema

Il progetto simula un ambiente di Produzione reale, utilizzando un approccio distribuito e automatizzato al 100%. Il ciclo di vita del software è gestito interamente senza interventi manuali sui server, passando dal codice sorgente al deployment in pochi minuti.

### 🛠️ Lo Stack Tecnologico utilizzato:

* **Kubernetes (K3s):** L'orchestratore alla base di tutto. Configurato in modalità Multi-Nodo (1 Master / Control Plane + 1 Worker Node) per garantire alta affidabilità e distribuzione del carico.
* **Traefik (Ingress Controller):** Agisce da "Portinaio" (Load Balancer e Reverse Proxy) del cluster, instradando il traffico esterno (`miosito.local`) verso i servizi corretti all'interno della rete virtuale di K3s.
* **PostgreSQL:** Database relazionale distribuito sul nodo Worker.
* **Python (FastAPI):** Applicazione backend containerizzata, che si connette al database per gestire ed esporre un'anagrafica dipendenti.
* **Docker & DockerHub:** Strumenti di containerizzazione e Registry pubblico per l'archiviazione delle immagini dell'applicazione.
* **GitHub Actions (Continuous Integration):** Pipeline automatizzata che compila il codice ad ogni push.
* **ArgoCD (Continuous Deployment / GitOps):** Il "maggiordomo" all'interno del cluster che assicura che lo stato dell'infrastruttura reale sia sempre identico a quello dichiarato su GitHub.

---

## 🔄 Il Ciclo CI/CD (The GitOps Loop)

Il cuore di questo progetto è l'automazione totale del rilascio. Ecco cosa succede "sotto il cofano" quando uno sviluppatore modifica il codice HTML o Python:

1. **Push su GitHub:** Lo sviluppatore invia il nuovo codice sul ramo `main` o `feature/*`.
2. **Trigger della CI (GitHub Actions):** * Il robot di GitHub fa il checkout del codice.
   * Genera un tag univoco basato sull'hash del commit (`git rev-parse --short HEAD`).
   * Compila la nuova immagine Docker e fa il push su DockerHub.
   * **La Magia:** Il robot apre il file `python-deployment.yaml`, aggiorna il tag dell'immagine alla nuova versione e fa un *commit automatico* sul repository.
3. **Trigger della CD (ArgoCD):**
   * ArgoCD (che "osserva" il repository H24) si accorge del nuovo commit fatto dal robot.
   * Rileva che lo stato desiderato (nuovo tag YAML) diverge dallo stato attuale (vecchio tag nel cluster).
   * Avvia in automatico un *Rolling Update*: crea i nuovi Pod Python, aspetta che siano sani e distrugge quelli vecchi senza causare disservizi (Zero Downtime).

---

## 🛑 Troubleshooting & Lesson Learned (Vita da DevOps)

Costruire questo cluster on-premise ha richiesto vere abilità di System Administration e Network Troubleshooting. Tra le sfide risolte:

* **Custom DNS Patching:** K3s sovrascriveva il file resolv.conf della macchina host. Abbiamo creato un file `coredns-patch.yaml` per forzare i DNS di Google (`8.8.8.8`) nel ConfigMap di `kube-system`, permettendo ad ArgoCD di risolvere domini esterni (come github.com).
* **Split-Brain & Network Partition (Flannel / iptables):** Il master e il worker perdevano la connessione interna (generando `Gateway Timeout` su Traefik). Il problema è stato debuggato analizzando gli *Endpoints* di Kubernetes ed eseguendo dei `ping` eseguiti direttamente dall'interno dei container (`kubectl exec`). È stato risolto effettuando il flush delle vecchie regole firewall di iptables e riavviando l'agent K3s e il networking di Debian per ricostruire il tunnel Flannel.
* **Gestione dello Stato "Unknown" in ArgoCD:** Compresa la differenza tra *Health Status* (salute fisica dei Pod) e *Sync Status* (allineamento con il repository Git remoto).

---

