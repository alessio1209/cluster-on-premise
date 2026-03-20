from fastapi.responses import FileResponse #un' API web serve a scambiare "dati grezzi" (JSON). Per far comportare la nostra applicazione come un vero server web (come nginx o apache) e spedisca fisicamente un file al computer di chi si collega, dobbiamo importare questo strumento
from fastapi import FastAPI, HTTPException #importiamo il motore del sito e il gestore degli errori web (ad esempio error 404 o 500 ecc...)
from pydantic import BaseModel #serve a creare delle regole su come devono essere fatti i dati che gli utenti ci inviano
import socket #libreria che permette a python di comunicare con il sistema operativo e la rete (ci serve per scoprire il nome della macchina)
import os #importa il modulo del sistema operativo. Ci serve per leggere le variabili d'ambiente
import psycopg2 #traduttore ufficiale che permette a Python di parlare con PostgreSQL
from psycopg2 import OperationalError #importiamo un tipo di errore specifico. Se il database è spento o la password è sbagliata, questa funzione cattura l'errore senza far crashare brutalmente tutta l'app python

app = FastAPI() #creiamo l'oggetto app, che è il motore del nostro server

#La rotta che serve il sito web grafico
@app.get("/") #lo "/" rappresenta la root. Significa che questo pezzo di codice funziona solo quando l'utente digita l'indirizzo principale del sito senza aggiungere altro (es. http://miosito.local/)
def read_root():
    return FileResponse("index.html") #quando un utente bussa alla porta principale, Python prende il file index.html e glielo spedisce. A quel punto sarà il browser dell'utente (Firefox/Chrome) a leggere l'HTML, colorare la pagina e mostrare la grafica

# 1. Definiamo la "forma" dei dati (Il Modello Dati Pydantic). Diciamo a FastAPI che, quando vuole registrarsi, deve obbligatoriamente inviarci un pacchetto dati contenente un nome e un'email. Se un hacker o un programma difettoso prova a inviarci un'età al posto del nome, o omette l'email, FastAPI bloccherà la richiesta, restituendo un errore.
class Utente(BaseModel):
    nome: str
    email: str

# 2. Funzione "Centralino" per collegarsi al DB
def get_db_connection():
    try:
       conn = psycopg2.connect(
           host=os.environ.get("DB_HOST", "postgres"),
           database="postgres",
           user="postgres",
           password=os.environ.get("DB_PASSWORD", "")
       )
       return conn
    except OperationalError as e:
        print(f"Errore DB: {e}")
        return None

# 3. FastAPI: Crea la tabella in automatico all'accensione!
@app.on_event("startup") #dice a Python di eseguire questo codice una sola volta, nel momento esatto in cui il Pod si accende, prima che gli utenti entrino 
def crea_tabelle():
    conn = get_db_connection()
    if conn:
	#apriamo un cursore all'interno del database (come una finestra di terminale)
       	cursor = conn.cursor()
       	cursor.execute("""
 	    CREATE TABLE IF NOT EXISTS utenti (
	       id SERIAL PRIMARY KEY,
               nome VARCHAR(100) NOT NULL,
               email VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        conn.commit()
	#è fondamentale chiudere la finestra di comunicazione per evitare futuri blocchi
        cursor.close()
        conn.close()

# 4. Rotta GET: Leggere chi c'è nel database. GET è il verbo di internet per ottenere delle informazioni
@app.get("/utenti/")
def leggi_utenti():
    conn = get_db_connection()
    if not conn: #controlla se il Service del db ha ripsoto, altrimenti lancia HTTPException
        raise HTTPException(status_code=500, detail="Database offline")

    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email FROM utenti;")
    righe = cursor.fetchall() #prende tutte le righe del db
    cursor.close()
    conn.close()
    #il db ci restituirà i dati come (1, Mario, mario@email.it ecc.) questa riga li trasforma in un dizionario elegante che i siti web sono in grado di leggere
    lista_utenti = [{"id": r[0], "nome": r[1], "email": r[2]} for r in righe]

    return {
        "pod_che_risponde": socket.gethostname(), #il Pod che risponderà, il quale l'app python che girerà dentro un container kubernetes, il nome sarà (es. app-python-6cd98...). Quando ricarichiamo la pagina web, vedremo questo nome cambiare, dimostrando che il Load Balancer sta smistando il traffico tra i vari container
        "utenti_registrati": lista_utenti 
    }

# 5. Rotta POST: Scrivere un nuovo utente nel database. Il verbo di internet che prenderà e salverà i dati. Quando riceve il nuovo utente deve rispettare le regole del BaseModel (da Pydanitc)
@app.post("/utenti/")
def crea_utente(nuovo_utente: Utente):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database offline")

    cursor = conn.cursor()
    try:
	#non mettiamo mai i nomi degli utenti direttamente nella frase SQL, useremo %s (dei segnaposto). In questo modo si impedisce di ricevere attacchi di tipo "SQL Injection" per distruggere il db
        cursor.execute(
            	"INSERT INTO utenti (nome, email) VALUES (%s, %s) RETURNING id;",
            	(nuovo_utente.nome, nuovo_utente.email)
        )
        id_generato = cursor.fetchone()[0]
        conn.commit() #nei db le modifiche non sono salvate finché non eseguiamo il comando commit (conferma definitiva)
        return {"status": "success", "message": "Utente salvato!", "id": id_generato}
    except Exception as e:
        conn.rollback() #se un utente prova ad usare un'email già registrata, violando la regola UNIQUE, il rollback annulla la transazione, lasciando il db pulito, e restituisce l'errore 400 all'utente
        raise HTTPException(status_code=400, detail="Errore: Forse l'email esiste già?")
    #questo blocco viene eseguito sempre, sia in caso di successo che di errore, assicurandosi di chiudere le porte e non esaurire le risorse del server
    finally:
        cursor.close()
        conn.close()
