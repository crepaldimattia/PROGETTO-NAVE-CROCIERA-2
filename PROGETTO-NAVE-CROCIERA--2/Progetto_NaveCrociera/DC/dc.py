# Device Client (DC)
# questo script simula un sensore di temperatura e umidità
# e invia i dati al DA tramite socket TCP

import socket
import json
import time
import misurazione

# carico la configurazione del DC
with open("configurazionedc.conf", "r") as f:
    config = json.load(f)

# creo il socket TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# indirizzo del server (DA)
IP_SERVER = "127.0.0.1"
PORTA_SERVER = 9999

# mi collego al DA
client_socket.connect((IP_SERVER, PORTA_SERVER))

# ricevo il tempo di rilevazione dal DA
tempo_rilevazione = int(client_socket.recv(1024).decode())

print("Connesso al DA")
print("Tempo di rilevazione:", tempo_rilevazione, "secondi")

numero_rilevazione = 0

try:
    while True:
        numero_rilevazione += 1

        # leggo temperatura e umidità
        temperatura = misurazione.leggi_temperatura()
        umidita = misurazione.leggi_umidita()

        # creo il DatoIoT
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

        # converto in JSON
        dato_json = json.dumps(dato_iot)

        # invio il dato al DA
        client_socket.sendall(dato_json.encode())

        # debug
        print("Inviato:", dato_json)

        time.sleep(tempo_rilevazione)

except KeyboardInterrupt:
    print("\nDC terminato manualmente")

finally:
    client_socket.close()
