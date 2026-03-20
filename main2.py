from fastapi import FastAPI #importiamo le librerie necessarie per creare il nostro server
import socket #libreria che permette a python di comunicare con il sistema operativo e la rete (ci serve per scoprire il nome della macchina)
import os #importa il modulo del sistema operativo. Ci serve per leggere le variabili d'ambiente
import psycopg2 #interprete ufficiale che insegna a Python come parlare la lingua di PostgreSQL sulla rete
from psycopg2 import OperationalError #importiamo un tipo di errore specifico. Se il database è spento o la password è sbagliata, questa funzione cattura l'errore senza far crashare brutalmente tutta l'app python

app = FastAPI() #creiamo l'oggetto app, che è il motore del nostro server

@app.get("/") #si chiama decoratore. Se qualcuno si collega all'indirizzo principale (la root, indicata con /) usando il metodo GET (quello standard dei broswer) esegui la funzione che è sotto
def read_root (): #funzione python
	return { #ritorniamo un dizionario python. FastAPI trasforma automaticamente questo dizionario in un formato JSON, linguaggio universale con cui comunicano le app moderne
		"status": "success",
		"message": "Benvenuto nella mia App Python su K3s!",
		"pod_name": socket.gethostname() #chiede al sistema operativo come si chiama e dato che python girerà dentro un container kubernetes, il nome del sistema operativo sarà esattamente il nome del pod (es. app-python-6cd98...). Quando ricarichiamo la pagina web, vedremo questo nome cambiare, dimostrando che il Load Balancer sta smistando il traffico tra i vari container
	}

@app.get("/db-test") #diciamo a FastAPI che se un utente digita l'indirizzo, ad esempio tuo-sito.com/db-test, esegui il codice qui sotto
def test_db_connection():
	try:
		#non scriviamo le password nel codice, faremo in modo che le leggerà dal file delle variabili d'ambiente
		db_host = os.environ.get("DB_HOST", "postgres") #il nome del nostro servizio. Kubernetes trasformerà questa parola nell'IP corretto
		db_password = os.environ.get("DB_PASSWORD", "") 
		#tentativo di connessione al database
		conn = psycopg2.connect(
			host=db_host, 
			database="postgres",
			user="postgres",
			password=db_password
		)

		#apriamo un cursore all'interno del database (come una finestra di terminale)
		cursor = conn.cursor()
		cursor.execute("SELECT version ();") #esegue questo comando all'interno del database
		db_version = cursor.fetchone() #prende la prima riga della risposta che il db ha dato

		#è fondamentale chiudere la finestra di comunicazione per evitare futuri blocchi
		cursor.close()
		conn.close()

		return {
			"status": "success",
			"message": "Connessione al Database riuscita!",
			"db_version": db_version[0],
			"pod_name": socket.gethostname()
		}

	except OperationalError as e: #se la riga conn = psycopg2.connect(...) falisce, il codice salta direttamente qui, ignorando il resto
		return {
			"status": "error",
                        "message": "Connessione al Database non riuscita!",
                        "error_details": str(e),
                        "pod_name": socket.gethostname()
                }

