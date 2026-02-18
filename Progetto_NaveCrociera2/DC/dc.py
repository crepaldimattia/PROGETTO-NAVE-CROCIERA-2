# Questo script simula un sensore di temperatura e umidità
# e invia i dati al DA tramite socket TCP

import socket        # modulo per la comunicazione di rete
import json          # modulo per la gestione dei dati JSON
import time          # modulo per la gestione del tempo
import misurazione   # modulo personalizzato per simulare le misurazioni del sensore

# -------------------------------
# Lettura della configurazione del DC
# -------------------------------

# open(file, mode)
# Serve per aprire un file
# Parametri:
# - file: nome del file da aprire
# - mode: modalità di apertura ("r" = lettura)
# Restituisce:
# - oggetto file
with open("configurazionedc.conf", "r") as f:

    # json.load(file)
    # Serve per leggere un file JSON e convertirlo in dizionario Python
    # Parametri:
    # - file: file JSON aperto
    # Restituisce:
    # - dizionario Python con i parametri di configurazione
    config = json.load(f)

# -------------------------------
# Creazione del socket client
# -------------------------------

# socket.socket(family, type)
# Serve per creare un socket
# Parametri:
# - family: AF_INET = IPv4
# - type: SOCK_STREAM = TCP
# Restituisce:
# - oggetto socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Indirizzo del server (DA)
IP_SERVER = "127.0.0.1"
PORTA_SERVER = 9999

# socket.connect(address)
# Serve per collegarsi a un server remoto
# Parametri:
# - address: tupla (IP_SERVER, PORTA_SERVER)
# Restituisce:
# - nulla
client_socket.connect((IP_SERVER, PORTA_SERVER))

# socket.recv(buffer_size)
# Serve per ricevere dati dal socket
# Parametri:
# - buffer_size: numero massimo di byte da ricevere
# Restituisce:
# - dati ricevuti in bytes
tempo_rilevazione = int(client_socket.recv(1024).decode())

print("Connesso al DA")
print("Tempo di rilevazione:", tempo_rilevazione, "secondi")

numero_rilevazione = 0

try:
    while True:
        numero_rilevazione += 1

        # -------------------------------
        # Lettura dei valori del sensore
        # -------------------------------

        # misurazione.leggi_temperatura()
        # Serve per simulare la lettura della temperatura
        # Parametri:
        # - nessuno
        # Restituisce:
        # - valore della temperatura (float o int)
        temperatura = misurazione.leggi_temperatura()

        # misurazione.leggi_umidita()
        # Serve per simulare la lettura dell'umidità
        # Parametri:
        # - nessuno
        # Restituisce:
        # - valore dell'umidità (float o int)
        umidita = misurazione.leggi_umidita()

        # -------------------------------
        # Creazione del Dato IoT
        # -------------------------------
        dato_iot = {
            "cabina": config["cabina"],
            "ponte": config["ponte"],
            "sensore": config["sensore"],
            "identita": config["identita"],
            "osservazione": {
                "rilevazione": numero_rilevazione,
                "temperatura": temperatura,
                "umidita": umidita
            }
        }

        # json.dumps(obj)
        # Serve per convertire un dizionario Python in una stringa JSON
        # Parametri:
        # - obj: dizionario Python
        # Restituisce:
        # - stringa JSON
        dato_json = json.dumps(dato_iot)

        # socket.sendall(data)
        # Serve per inviare dati al server tramite socket
        # Parametri:
        # - data: dati da inviare in formato bytes
        # Restituisce:
        # - nulla
        client_socket.sendall(dato_json.encode())

        # Debug
        print("Inviato:", dato_json)

        # time.sleep(seconds)
        # Serve per sospendere l'esecuzione del programma
        # Parametri:
        # - seconds: numero di secondi di pausa
        # Restituisce:
        # - nulla
        time.sleep(tempo_rilevazione)

except KeyboardInterrupt:
    # Gestione dell'interruzione manuale del programma
    print("\nDC terminato manualmente")

finally:
    # socket.close()
    # Serve per chiudere il socket e liberare le risorse
    # Parametri:
    # - nessuno
    # Restituisce:
    # - nulla
    client_socket.close()
