pipeline {
	//1. spazio temporaneo dove chiediamo a kubernetes di prepararci i pod
	agent {
            kubernetes {
                //di solito Jenkins gira in un solo container. Con questo blocco, chiediamo a kubernetes di costruire un Pod speciale a due stanze. Nella prima c'è Jenkins, nella seconda mettiamo un container chiamato kaniko (scaricato direttamente dai server di google:gcr.io)
                //diciamo a kaniko di mettersi in modalità sleep 9999999 secondi, se non lo facessimo, il container si spegnerebbe subito dopo essersi acceso, invece noi vogliamo che resti vivo, in attesa che Jenkins lo svegli.
                yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: kaniko
                    image: gcr.io/kaniko-project/executor:debug
                    command:
                    - sleep
                    args:
                    - 9999999
                '''
            }
	}
	
	//2. variabili di sistema
	environment {
		//.trim cancella gli spazi vuoti o gli a capo invisibili di Linux che a volte aggiunge alla fine delle parole
		GIT_COMMIT_HASH = sh(script:'git rev-parse --short HEAD', returnStdout: true).trim()
	}

	stages {
		stage ('Checkout del codice') {
			steps {
				checkout scm
				echo 'Codice sorgente scaricato da git'
			}
		}

		stage ('Installazione di Trivy') {
			steps {
				echo 'Preparazione dello scanner di sicurezza Trivy'
				sh '''
					curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b .
				'''
			}
		}

		stage ('Scansione sicurezza') {
			steps {
				echo 'Avvio scansione vulnerabilità del codice'
				sh './trivy fs --format table -o risultati_sicurezza.txt .'
				sh 'cat risultati_sicurezza.txt'
			}
		}

		//3. costruzione e spedizione
		stage ('Costruzione e spedizione Kaniko') {
			steps {
				//entriamo nel container di Kaniko. Da questo momento Jenkins chiede aiuto a kaniko. Da questa riga in poi tutti i comandi vengono eseguiti dentro il container di kaniko
				container('kaniko') {
					echo 'Cloud-Native pronto per la commit ${GIT_COMMIT_HASH}'
					//prendiamo le credenziali e riempiamo temporaneamente $USER e $PASS
					withCredentials ([usernamePassword(credentialsId: 'dockerhub-creds', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
						sh '''
							#kaniko non usa il comando docker login (perchè non ha docker installato). Per autenticarsi su Docker hub ha bisogno di un file di configurazione chiamato config.json. I server web non ammettono password in chiaro, per questo motivo abbiamo usato il comando base64 che prende user:password e lo nasconde in una stringa incomprensibile 
							mkdir -p /kaniko/.docker
							AUTH=$(echo -n "$USER:$PASS" | base64 | tr -d '\n')
							echo "{\\"auths\\":{\\"https://index.docker.io/v1/\\":{\\"auth\\":\\"$AUTH\\"}}}" > /kaniko/.docker/config.json
							#kaniko/executor= invochiamo il programma  --context 'pwd'= diciamo a kaniko dove si trovano i file el nostro codice, --destiantion= diciamo a kaniko dove spedire il pacchetto finito. Mettiamo due destinazioni, la prima usa la variabile ${GIT_COMMIT_HASH}, la seconda lo tagga come latest. Kaniko fa build e push insieme
							/kaniko/executor --context $WORKSPACE --destination alessioerco12/k8s-python-app:$GIT_COMMIT_HASH --destination alessioerco12/k8s-python-app:latest
						'''
					}
				}
			}
		}
	}
}
