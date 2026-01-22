import random   # serve per generare numeri casuali

#
# Funzioni
#

def leggi_temperatura(N):
    # genera un valore casuale di temperatura tra 10 e 40
    # N indica quante cifre decimali voglio
    TEMP = round(random.uniform(10,40), N)
    return TEMP   # restituisce la temperatura

# funzione che simula un sensore di umidità
# il valore va da 20 a 90
# N indica il numero di cifre decimali
def leggi_umidita(N):
    UMID = round(random.uniform(20,90), N)  # genera un valore casuale di umidità
    return UMID   # restituisce l'umidità
