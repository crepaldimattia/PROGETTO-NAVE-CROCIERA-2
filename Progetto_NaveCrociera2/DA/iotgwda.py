# Data Aggregator / IoT Gateway (DA)
# Questo programma riceve i dati dai Data Collector (DC),
# li elabora (calcolo delle medie) e li salva su file

import socket
import json
import time
import crypta
from statistics import mean

# -------------------------------
# Lettura dei parametri di configurazione
# -------------------------------
# Apro il file parametri.conf e carico tutti i parametri necessari
with open("parametri.conf", "r") as f:
    parametri = json.load(f)

# Parametri temporali e di rete
TEMPO_RILEVAZIONE = parametri["TEMPO_RILEVAZIONE"]      # tempo di rilevazione del DC
TEMPO_INVIO = parametri["TEMPO_INVIO"] * 60             # tempo di invio (convertito in secondi)
N_DECIMALI = parametri["N_DECIMALI"]                     # numero di decimali per le medie
IP_SERVER = parametri["IP_SERVER"]                      # indirizzo IP del DA
PORTA_SERVER = parametri["PORTA_SERVER"]                # porta di ascolto del DA

# -------------------------------
# Creazione del socket server
# -------------------------------
# Creo un socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associo il socket all'indirizzo IP e alla porta
server_socket.bind((IP_SERVER, PORTA_SERVER))

# Metto il server in ascolto (accetto una sola connessione)
server_socket.listen(1)

print("DA in ascolto su", IP_SERVER, PORTA_SERVER)

# Accetto la connessione del DC
connessione, indirizzo = server_socket.accept()
print("DC collegato:", indirizzo)

# Invio al DC il tempo di rilevazione
connessione.sendall(str(TEMPO_RILEVAZIONE).encode())

# -------------------------------
# Inizializzazione delle variabili
# -------------------------------
temperature = []        # lista delle temperature ricevute
umidita = []            # lista delle umidità ricevute
numero_invii = 0        # contatore degli invii alla IoT Platform
ultimo_invio = time.time()  # tempo dell'ultimo invio effettuato

try:
    while True:
        # Ricevo i dati dal DC
        dati = connessione.recv(4096).decode()
        if not dati:
            break

        # Converto la stringa JSON in dizionario Python
        dato_dc = json.loads(dati)

        print("Ricevuto:", dato_dc)

        # Salvo temperatura e umidità nelle rispettive liste
        temperature.append(dato_dc["osservazione"]["temperatura"])
        umidita.append(dato_dc["osservazione"]["umidita"])

        # -------------------------------
        # Controllo se è passato il tempo di invio
        # -------------------------------
        if time.time() - ultimo_invio >= TEMPO_INVIO:
            numero_invii += 1

            # Calcolo le medie di temperatura e umidità
            media_temp = round(mean(temperature), N_DECIMALI)
            media_umid = round(mean(umidita), N_DECIMALI)

            # Creo il dato aggregato del DA
            dato_da = {
                "identita_giot": parametri["IDENTITA_GIOT"],
                "identita_dc": dato_dc["identita"],
                "media_temperatura": media_temp,
                "media_umidita": media_umid,
                "invionumero": numero_invii
            }

            # Converto il dato in JSON e lo criptop
            dato_json = json.dumps(dato_da)
            dato_criptato = cripta.criptazione(dato_json)

            print("Inviato criptato:", dato_criptato)

            # -------------------------------
            # Salvataggio su file (dato NON criptato)
            # -------------------------------
            json_dati = open("../IOTP/iotdata.dbt", "a", encoding="utf-8")
            json.dump(dato_da, json_dati)
            json_dati.close()

            # Svuoto le liste e aggiorno il tempo dell'ultimo invio
            temperature.clear()
            umidita.clear()
            ultimo_invio = time.time()

except KeyboardInterrupt:
    # Chiusura manuale del programma
    print("\nDA terminato manualmente")
    print("Numero invii alla IoT Platform:", numero_invii)

finally:
    # Chiusura della connessione e del socket
    connessione.close()
    server_socket.close()

