//riga principale. Diciamo a Jenkins che stiamo usando la sintassi moderna e dichiarativa. Tutto il lavoro deve stare qui dentro
pipeline { 
	//diciamo a Jenkins di eseguire questo lavoro sul primo node/executor che ha disponibile
	agent any

	//creiamo una scatola globale per salvare l'ID della commmit 
	environment {
		//il comadno git rev-parse --short HEAD prende le prime 7 ettere della commit attuale
		//.trim() toglie eventuali spazi vuoti finali
		GIT_COMMIT_HASH = sh(script:'git rev-parse --short HEAD', returnStdout: true).trim()
	}

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

		stage ('Costruzione immagine Docker') {
			steps {
				echo "Costruzione del container per la commit ${GIT_COMMIT_HASH}"
				//usiamo l'ID della commit come tag
				sh "docker build -t alessioerco12/k8s-python-app:${GIT_COMMIT_HASH} ."
				//opzionale, ma comodo. Possiamo taggare la stessa immagine anche come "latest"
				sh "docker tag alessioerco12/k8s-python-app:latest"
			}
		} 

		stage ('Spedizione su docker hub') {
			steps {
				echo 'Apertura cassaforte e spedizione nel cloud'
				//withCredentials= legge i dati. credentialsID:'dockerhub-creds'= va a leggere esattamente la credenziale che abbiamo salvato. passwordVariable: e usernameVariable: = jenkins estrae i valori reali e li inietta in due scatole virtuali temporanee chiamate 'DOCKER_PASSWORD' e 'DOCKER_USERNAME', queste esisteranno solo finchè siamo dentro questa fase, poi verranno distrutte
				withCredentials([usernamePassword(credentialsID:'dockerhub-creds', passwordVariable:'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
					//la password viene iniettata direttamente, tramite |, in docker
					sh 'echo "$DOCKER-PASSWORD | docker login -u "$DOCKER_USERNAME" --password-stdin'
					//pusha le due etichette col nome corretto
					sh "docker push alessioerco12/k8s-python-app:${GIT_COMMIT_HASH}"
					sh "docker push alessioerco12/k8s-python-app:latest"
				}
			}		
		}
	}
}
