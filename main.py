from fastapi import FastAPI #importiamo le librerie necessarie per creare il nostro server
import socket #libreria che permette a python di comunicare con il sistema operativo e la rete (ci serve per scoprire il nome della macchina)

app = FastAPI() #creiamo l'oggetto app, che è il motore del nostro server

@app.get("/") #si chiama decoratore. Se qualcuno si collega all'indirizzo principale (la root, indicata con /) usando il metodo GET (quello standard dei broswer) esegui la funzione che è sotto
def read_root (): #funzione python
	return { #ritorniamo un dizionario python. FastAPI trasforma automaticamente questo dizionario in un formato JSON, linguaggio universale con cui comunicano le app moderne
		"status": "success",
		"message": "Benvenuto nella mia App Python su K3s!",
		"pod_name": socket.gethostname() #chiede al sistema operativo come si chiama e dato che python girerà dentro un container kubernetes, il nome del sistema operativo sarà esattamente il nome del pod (es. app-python-6cd98...). Quando ricarichiamo la pagina web, vedremo questo nome cambiare, dimostrando che il Load Balancer sta smistando il traffico tra i vari container
	}
