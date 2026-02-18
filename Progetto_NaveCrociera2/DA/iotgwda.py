# Data Aggregator / IoT Gateway (DA)
# Questo programma riceve i dati dai Data Collector (DC),
# li elabora (calcolo delle medie) e li salva su file

import socket      # modulo per la comunicazione di rete (TCP/IP)
import json        # modulo per la gestione dei dati in formato JSON
import time        # modulo per la gestione del tempo
import crypta      # modulo personalizzato per la crittografia dei dati
from statistics import mean  # funzione mean() per calcolare la media aritmetica

# -------------------------------
# Lettura dei parametri di configurazione
# -------------------------------

# open(file, mode)
# Serve per aprire un file
# Parametri:
# - file: nome del file da aprire
# - mode: modalità di apertura ("r" = lettura)
# Restituisce:
# - un oggetto file
with open("parametri.conf", "r") as f:

    # json.load(file)
    # Serve per caricare un file JSON e convertirlo in un dizionario Python
    # Parametri:
    # - file: file JSON aperto
    # Restituisce:
    # - dizionario Python con i dati del file
    parametri = json.load(f)

# Parametri temporali e di rete letti dal file di configurazione
TEMPO_RILEVAZIONE = parametri["TEMPO_RILEVAZIONE"]      # tempo di rilevazione del DC
TEMPO_INVIO = parametri["TEMPO_INVIO"] * 60             # tempo di invio in secondi
N_DECIMALI = parametri["N_DECIMALI"]                     # numero di decimali per le medie
IP_SERVER = parametri["IP_SERVER"]                      # indirizzo IP del DA
PORTA_SERVER = parametri["PORTA_SERVER"]                # porta di ascolto del DA

# -------------------------------
# Creazione del socket server
# -------------------------------

# socket.socket(family, type)
# Serve per creare un socket
# Parametri:
# - family: tipo di indirizzo (AF_INET = IPv4)
# - type: tipo di socket (SOCK_STREAM = TCP)
# Restituisce:
# - un oggetto socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# socket.bind(address)
# Serve per associare il socket a un indirizzo IP e a una porta
# Parametri:
# - address: tupla (IP, PORTA)
# Restituisce:
# - nulla
server_socket.bind((IP_SERVER, PORTA_SERVER))

# socket.listen(backlog)
# Serve per mettere il socket in ascolto
# Parametri:
# - backlog: numero massimo di connessioni in coda
# Restituisce:
# - nulla
server_socket.listen(1)

print("DA in ascolto su", IP_SERVER, PORTA_SERVER)

# socket.accept()
# Serve per accettare una connessione in ingresso
# Parametri:
# - nessuno
# Restituisce:
# - connessione: nuovo socket per comunicare con il client
# - indirizzo: indirizzo del client
connessione, indirizzo = server_socket.accept()
print("DC collegato:", indirizzo)

# socket.sendall(data)
# Serve per inviare dati attraverso il socket
# Parametri:
# - data: dati da inviare in formato bytes
# Restituisce:
# - nulla
connessione.sendall(str(TEMPO_RILEVAZIONE).encode())

# -------------------------------
# Inizializzazione delle variabili
# -------------------------------

temperature = []        # lista delle temperature ricevute
umidita = []            # lista delle umidità ricevute
numero_invii = 0        # contatore degli invii alla IoT Platform

# time.time()
# Serve per ottenere il tempo corrente in secondi dal 1/1/1970
# Parametri:
# - nessuno
# Restituisce:
# - tempo corrente in secondi (float)
ultimo_invio = time.time()

try:
    while True:

        # socket.recv(buffer_size)
        # Serve per ricevere dati dal socket
        # Parametri:
        # - buffer_size: numero massimo di byte da ricevere
        # Restituisce:
        # - dati ricevuti in bytes
        dati = connessione.recv(4096).decode()

        if not dati:
            break

        # json.loads(string)
        # Serve per convertire una stringa JSON in un dizionario Python
        # Parametri:
        # - string: stringa JSON
        # Restituisce:
        # - dizionario Python
        dato_dc = json.loads(dati)

        print("Ricevuto:", dato_dc)

        # Salvataggio dei valori ricevuti
        temperature.append(dato_dc["osservazione"]["temperatura"])
        umidita.append(dato_dc["osservazione"]["umidita"])

        # -------------------------------
        # Controllo se è passato il tempo di invio
        # -------------------------------
        if time.time() - ultimo_invio >= TEMPO_INVIO:
            numero_invii += 1

            # mean(lista)
            # Serve per calcolare la media aritmetica
            # Parametri:
            # - lista di numeri
            # Restituisce:
            # - valore medio (float)
            media_temp = round(mean(temperature), N_DECIMALI)
            media_umid = round(mean(umidita), N_DECIMALI)

            # Creazione del dato aggregato
            dato_da = {
                "identita_giot": parametri["IDENTITA_GIOT"],
                "identita_dc": dato_dc["identita"],
                "media_temperatura": media_temp,
                "media_umidita": media_umid,
                "invionumero": numero_invii
            }

            # json.dumps(obj)
            # Serve per convertire un dizionario Python in stringa JSON
            # Parametri:
            # - obj: dizionario Python
            # Restituisce:
            # - stringa JSON
            dato_json = json.dumps(dato_da)

            # cripta.criptazione(dato)
            # Serve per criptare una stringa
            # Parametri:
            # - dato: stringa da criptare
            # Restituisce:
            # - stringa criptata
            dato_criptato = cripta.criptazione(dato_json)

            print("Inviato criptato:", dato_criptato)

            # -------------------------------
            # Salvataggio su file (dato NON criptato)
            # -------------------------------

            # open(file, mode, encoding)
            # Serve per aprire un file in modalità append
            # Parametri:
            # - file: percorso del file
            # - mode: "a" = aggiunta
            # - encoding: codifica dei caratteri
            # Restituisce:
            # - oggetto file
            json_dati = open("../IOTP/iotdata.dbt", "a", encoding="utf-8")

            # json.dump(obj, file)
            # Serve per scrivere un dizionario Python in un file JSON
            # Parametri:
            # - obj: dizionario Python
            # - file: file aperto
            # Restituisce:
            # - nulla
            json.dump(dato_da, json_dati)

            json_dati.close()

            # Pulizia delle liste e aggiornamento del tempo
            temperature.clear()
            umidita.clear()
            ultimo_invio = time.time()

except KeyboardInterrupt:
    # Gestione dell'interruzione manuale del programma
    print("\nDA terminato manualmente")
    print("Numero invii alla IoT Platform:", numero_invii)

finally:
    # socket.close()
    # Serve per chiudere il socket e liberare le risorse
    # Parametri:
    # - nessuno
    # Restituisce:
    # - nulla
    connessione.close()
    server_socket.close()
