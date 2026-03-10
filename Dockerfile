#immagine python ufficiale e leggera. Sistema operativo Debian base e leggero con python 3.9 gia installato
FROM python:3.9-slim 

#cartella di lavoro nel container. Crea una cartella chiamata /app dentro il container ed entra lì. Tutti i comandi successivi verranno lanciati in questa cartella
WORKDIR /app

#copia i requisiti e installabili. Prende il file requirements.txt dal mio pc e lo copia nella cartella /app. RUN pip install --no-cache-dir -r requirements.txt installa le librerie che abbiamo elencato, l'opzione --no-cache-dir non salverà i file temporanei di installazione, così l'immagine sarà più leggera
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copia tutto il codice dell'app. Prende il codice del main.py e lo copia nel container.
COPY . .

#esponi la porta usata da FastAPI. "Post-it" informativo, dice che il container ascolta sulla porta 8000. Non apre realmente la porta, per quello ci pensa kubernetes
EXPOSE 8000

#comando lanciato quando il container si accende. Univorn è il server web reale che fa girare FastAPI. Main:app crea nel file main l'oggetto chiamato app. --host 0.0.0.0 è fondamentale in docker perchè dice di ascoltare su tutte le schede di rete, se non lo mettiamo il server ascolterà solo se stesso e K3s non riuscirà a parlargli
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
