pipeline {
	agent any
	
	stages {
		stage('Controllo funzionamento Jenkins') {
			steps {
				echo 'Inizio test'
				sh 'echo "Il sistema operativo dell-agente è:"'
				sh 'cat /etc/os-release'
			}
		}
		stage('Controllo sicurezza base') {
			steps {
				echo 'Nessun virus rilevato (Simulazione Trivy)'
			}
		}
	}
}
