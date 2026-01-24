# Modulo di misurazione sensori
# Script: misurazione.py

import random

def leggi_temperatura():
    # Simulazione temperatura (nave da crociera)
    return round(random.uniform(18.0, 30.0), 2)

def leggi_umidita():
    # Simulazione umidità
    return round(random.uniform(40.0, 70.0), 2)

