import json
import time
import random
import os

# Importo le funzioni che simulano il sensore
from misurazione import leggi_temperatura, leggi_umidita


# ===== LETTURA PARAMETRI DAL FILE =====
# Apro il file di configurazione e leggo i parametri
with open("configurazione/parametri.conf", "r") as file:
    parametri = json.load(file)

# Salvo i parametri in variabili più comode
TEMPO = parametri["TEMPO_RILEVAZIONE"]     # tempo tra una rilevazione e l'altra
DECIMALI = parametri["N_DECIMALI"]         # numero di cifre decimali
CABINE = parametri["N_CABINE"]             # numero totale di cabine
PONTI = parametri["N_PONTI"]               # numero totale di ponti


# ===== PREPARAZIONE FILE DI OUTPUT =====
# Creo la cartella "dati" se non esiste
os.makedirs("dati", exist_ok=True)

# Apro il file in modalità append per aggiungere nuovi dati
file_dati = open("dati/iotdata.dbt", "a")


# ===== VARIABILI PER STATISTICHE =====
numero_rilevazioni = 0     # contatore delle rilevazioni
somma_temperatura = 0     # somma delle temperature
somma_umidita = 0         # somma delle umidità

print("Simulazione avviata (CTRL+C per terminare)")


# ===== CICLO PRINCIPALE =====
try:
    while True:
        numero_rilevazioni += 1

        # Scelgo una cabina e un ponte in modo casuale
        cabina = random.randint(1, CABINE)
        ponte = random.randint(1, PONTI)

        # Leggo i valori dal sensore simulato
        temperatura = leggi_temperatura(DECIMALI)
        umidita = leggi_umidita(DECIMALI)

        # Prendo il timestamp corrente
        tempo_corrente = time.time()

        # Creo il dato IoT sotto forma di dizionario
        dato = {
            "cabina": cabina,
            "ponte": ponte,
            "rilevazione": numero_rilevazioni,
            "dataeora": tempo_corrente,
            "temperatura": temperatura,
            "umidita": umidita
        }

        # Stampo il dato a video per controllo
        print(json.dumps(dato, indent=4))

        # Scrivo il dato nel file
        file_dati.write(json.dumps(dato) + "\n")

        # Aggiorno le somme per calcolare le medie
        somma_temperatura += temperatura
        somma_umidita += umidita

        # Aspetto prima della prossima rilevazione
        time.sleep(TEMPO)


# ===== GESTIONE CTRL+C =====
except KeyboardInterrupt:
    print("\nSimulazione terminata")

    # Calcolo le medie finali
    media_temp = round(somma_temperatura / numero_rilevazioni, DECIMALI)
    media_umid = round(somma_umidita / numero_rilevazioni, DECIMALI)

    # Stampo le statistiche finali
    print("Rilevazioni totali:", numero_rilevazioni)
    print("Temperatura media:", media_temp, "°C")
    print("Umidità media:", media_umid, "%")

    # Chiudo il file
    file_dati.close()
