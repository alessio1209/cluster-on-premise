//riga principale. Diciamo a Jenkins che stiamo usando la sintassi moderna e dichiarativa. Tutto il lavoro deve stare qui dentro
pipeline { 
	//diciamo a Jenkins di eseguire questo lavoro sul primo node/executor che ha disponibile
	agent any
	//qui troviamo tutte le fasi (stages) della pipeline
	stages {
		//diamo un nome alla prima fase (quello che vedremo apparire allo schermo)
		stage('Checkout del codice') {
			//comandi effetivi
			steps {
				//comando di Jenkins e significa di andare nel Source Control Management (SCM, ovvero git), dove ha preso questo file e scarica tutto il codice sorgente del progetto nella cartella corrente
				checkout scm
				echo 'Codice sorgente scaricato da github'
			}
		}
		stage('Installazione Trivy') {
			steps {
				echo 'Preparazione dello scanner di sicurezza Trivy'
				sh '''
					#si collega al server di Aqua Security e scarica il pacchetto compresso dell'antivirus Trivy
					curl -sfL  https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b .
				'''
			}
		}
		stage ('Scansione di sicurezza (DevSecOps)') {
			steps {
				echo 'Avvio scansione vulnerabilità del codice'
				//trivy fs= diciamo a trivy di analizzare il FileSystem (file di testo, il codice sorgente, le librerie python ecc). --format table -o risultati_sicurezza.txt= impagina i risultati in una bella tabella e li salva dentro un file di testo. il . finale significa che deve scansionare la cartella in cui si trova adesso e tutte le sottocartelle
				sh './trivy fs --format table -o risultati_sicurezza.txt .'
				//stampa a schermo il contenuto dei file 
				sh 'cat risultati_sicurezza.txt'
			}
		}
	}
}
