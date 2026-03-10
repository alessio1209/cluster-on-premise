#!/bin/bash

# --- Monitoraggio di rete per nodo worker 

TARGET="192.168.0.234"

echo "Inizio monitoraggio verso $TARGET ... (Premi Ctrl+C per fermare)"
echo "---------------" 

while true; do
	DATA=$(date '+%Y-%m-%d %H:%M:%S')
	if ping -c 1 -W 1 $TARGET &> /dev/null; then #ping -c 2 -W 1 (-W 1= aspetta massimo 1 secondo) $TARGET &> /dev/null; then 
		echo "[$DATA] rete OK: Il nodo $TARGET è online."

	else
		echo "[$DATA] allarme: Il nodo $TARGET non risponde."
	fi

	sleep 2 #dice a Linux di aspettare 2 secondi esatti prima di ricominciare il ciclo. Senza questo, inoderemmo la rete di migliaia di pacchetti al secondo, creando un attacco informatico involontario a te stesso
done
