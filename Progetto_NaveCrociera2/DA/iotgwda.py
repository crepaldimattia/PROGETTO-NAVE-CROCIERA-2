# Data Aggregator / IoT Gateway (DA)
# riceve i dati dai DC, li elabora e li salva su file

import socket
import json
import time
import crypta
from statistics import mean

# carico i parametri
with open("parametri.conf", "r") as f:
    parametri = json.load(f)

TEMPO_RILEVAZIONE = parametri["TEMPO_RILEVAZIONE"]
TEMPO_INVIO = parametri["TEMPO_INVIO"] * 60
N_DECIMALI = parametri["N_DECIMALI"]
IP_SERVER = parametri["IP_SERVER"]
PORTA_SERVER = parametri["PORTA_SERVER"]

# creo socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP_SERVER, PORTA_SERVER))
server_socket.listen(1)

print("DA in ascolto su", IP_SERVER, PORTA_SERVER)

connessione, indirizzo = server_socket.accept()
print("DC collegato:", indirizzo)

# invio il tempo di rilevazione al DC
connessione.sendall(str(TEMPO_RILEVAZIONE).encode())

temperature = []
umidita = []
numero_invii = 0
ultimo_invio = time.time()

try:
    while True:
        dati = connessione.recv(4096).decode()
        if not dati:
            break

        dato_dc = json.loads(dati)

        print("Ricevuto:", dato_dc)

        temperature.append(dato_dc["osservazione"]["temperatura"])
        umidita.append(dato_dc["osservazione"]["umidita"])

        # controllo se è il momento di inviare alla IOT Platform
        if time.time() - ultimo_invio >= TEMPO_INVIO:
            numero_invii += 1

            media_temp = round(mean(temperature), N_DECIMALI)
            media_umid = round(mean(umidita), N_DECIMALI)

            dato_da = {
                "identita_giot": parametri["IDENTITA_GIOT"],
                "identita_dc": dato_dc["identita"],
                "media_temperatura": media_temp,
                "media_umidita": media_umid,
                "invionumero": numero_invii
            }

            dato_json = json.dumps(dato_da)
            dato_criptato = cripta.criptazione(dato_json)

            print("Inviato criptato:", dato_criptato)

            # salvo il dato NON criptato
            #with open("../Progetto_NaveCrociera2/IOTP/iotdata.dbt", "a") as f:
            #   f.write(dato_json + "\n")

            json_dati = open("../IOTP/iotdata.dbt", "a", encoding= 'utf-8')
            json.dump(dato_da, json_dati)
            json_dati.close()

            temperature.clear()
            umidita.clear()
            ultimo_invio = time.time()

except KeyboardInterrupt:
    print("\nDA terminato manualmente")
    print("Numero invii alla IoT Platform:", numero_invii)

finally:
    connessione.close()
    server_socket.close()
