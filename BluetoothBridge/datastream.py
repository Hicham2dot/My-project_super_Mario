from enum import Enum
import threading
import queue
import datapacket
import paho.mqtt.client as mqtt

#Configurazione mqtt client
client = mqtt.Client()

# Connessione al broker mqtt locale
if client.connect('localhost', 1883, 60) != 0:
    print("Impossible to connect")
    exit(-1)

# Connessione al broker mqtt pubblico
#if client.connect('broker.hivemq.com', 1883, 8000) != 0:
#    print("Impossible to connect")
#    exit(-1)

#Dimensione massima del payload
MAX_LEN = 2148
PCK_OVERHEAD_LEN = 8 #2 start bytes + 2 stop bytes + 2 bytes len + 2 byte checksum

class BleDataStream():
    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None

    def __process_payload(self, data):
        length = int.from_bytes(data[2:4], byteorder='big')
        # i dati nel payload sono little endian
        payload = data[4:length+4]
        ptype = payload[0]
        if ptype in datapacket.handler_factory_table:
            packet_handler = datapacket.handler_factory_table[ptype]()
            packet_handler(payload)
            jsondata = packet_handler.to_json()
            print(packet_handler.ID)
            print(jsondata)
            #Qui invio con mqtt solo dei pacchetti che ci interessa trasmettere
            client.publish("unisadiem/dmcs/sensor/" + packet_handler.ID, jsondata)
        else:
            print(f"Handler not found for type {ptype}")

    def __verify_checksum(self, data):
        '''checkSumValue = int.from_bytes(data[-4:-2], byteorder='big')
        checkSum = 0
        count = 0
        while count < len(data)-2:
            checkSum += int.from_bytes(data[count:count+2], byteorder='little')
            #checkSum = checkSum and (215 - 1)
            count += 2

        if checkSumValue == checkSum:
            return True'''

        # per ora ritorniamo sempre True, va verificato se il calcolo della checksum è corretto
        return True

    def __verify(self, data):
        datalen = len(data) - PCK_OVERHEAD_LEN

        if not data.startswith(b'\xa0\xa2'):
            return False

        if not data.endswith(b'\xb0\xb3'):
            return False

        datalenfrompk = int.from_bytes(data[2:4], byteorder='big')
        if datalenfrompk > MAX_LEN or datalenfrompk != datalen:
            return False

        return self.__verify_checksum(data)

    def __process_queue(self):
        bytebuffer = bytearray()
        getnew = True
        while True:
            try:
                data = self._queue.get()
                bytebuffer.extend(data)
                #searching for a packet
                start = bytebuffer.find(b'\xa0\xa2')
                stop = bytebuffer.find(b'\xb0\xb3', start)

                if start != -1 and stop != -1:
                    candidate = bytebuffer[start:stop+2]
                    if self.__verify(candidate):
                        self.__process_payload(candidate)

                    #removing from the buffer
                    del bytebuffer[:stop+2]
                else:
                    continue

            except queue.Empty:
                pass

            except NotImplementedError as e:
                print(e)

            except Exception as e:
                print(e)

    def start_stream_processing(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self.__process_queue).start()

    # da usare come callback per il datastream
    def push_data(self, data):
        self._queue.put(data)
