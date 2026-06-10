# ISTRUZIONI HUBBLE

#### --- REQUISITI ---

- **PYTHON** (il programma è stato testato su versione 3.11, ma dovrebbe funzionare a partire dalla 3.8)
- **PAHO.MQTT** da installare attraverso il comando `pip install paho.mqtt`
- **BLEAK** da installare attraverso il comando `pip install bleak`

## AVVIO

Utilizzare il comando `python .\ble.py -d` per effettuare il discovery di tutti i dispositivi bluetooth presenti nelle vicinanze. In questo modo è possibile individuare il dispositivo "BERTA" per visualizzarne il MAC_ADDRESS
Utilizzare il comando `python .\ble.py -a MAC_ADDRESS` *(es. "python .\ble.py -a EF:29:AB:DF:6E:C0")* per iniziare a ricevere i pacchetti dal dispositivo ed inviarli attraverso MQTT sugli appositi topic