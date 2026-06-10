import asyncio
import argparse
import config
import datastream
from bleak import BleakScanner, BleakClient

blestream = datastream.BleDataStream()

def notify_callback(uuid, data):
    blestream.push_data(data)

async def discovery():
    devices = await BleakScanner.discover(return_adv=True, cb=dict(use_bdaddr=args.macos_use_bdaddr))
    for d, a in devices.values():
        print()
        print(d)
        print("-" * len(str(d)))
        print(a)

async def list_services(address):
    async with BleakClient(args.address) as client:
        for service in client.services:
            print(f"[Service: {service}]")
            for char in service.characteristics:
                properties = ",".join(char.properties)
                print(f"\t[Characteristic] {char} ({properties})")

async def send_configuration(address):
    #il nome del comando deve essere separato dal valore tramite lo spazio
    async with BleakClient(address) as client:
        for command in config.DEVICE_CONFIG:
            data = bytes(command, 'utf-8')
            await client.write_gatt_char(config.CONFIG_CHAR[1], data)

#comando non aggiunto nella lista
async def send_datetime(address, time):
    async with BleakClient(address) as client:
        #convertire la data in un bytearray su 7 byte (con anno (2 bytes little endian) mese, giorno, ore, minuti e secondi)
        date = []
        await client.write_gatt_char(config.DATE_CHAR[1], date)

async def read_char(client, uuid, byteorder='big'):
    try:
        value = await client.read_gatt_char(uuid)
        if value.isdigit():
            value = int.from_bytes(value, byteorder='big', signed=False)
        elif value.isascii():
            value = str(value.decode('utf-8'))
        else:
            print("Invalid type for characteristic data, cannot cast")
        return value
    except Exception as e:
        print(f"\t[Characteristic]{uuid}, Error: {e}") 

async def read(address, uuid, byteorder='big'):
    async with BleakClient(address) as client:
        print(uuid)
        value = await read_char(client, uuid, type)
        print(f"\t[Characteristic]{uuid}: {value}") 

async def read_chars(address):
    async with BleakClient(address) as client:
        while True:
            for char in config.READ_CHAR_DICT.values():
                value = await read_char(client, char[1])
                print(f"Reading {char[0]} Value: {value}")
                print(config.READ_CHAR_DICT[:-5])

async def read_data_stream(address):
    async with BleakClient(address) as client:
        try:
            await client.start_notify(config.STREAM_CHAR[1], notify_callback)
        except Exception as e:
            print(f"\t[Characteristic]{config.STREAM_CHAR[0]}, Error: {e}") 
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d", "--discover", action="store_true", help="Discover BLE devices")
    parser.add_argument("-l", "--list", action="store_true", help="List services of a given address")
    parser.add_argument("-c", "--configure", action="store_true", help="Send the configuration to the device")
    parser.add_argument("-r", "--read", help="Read data from a characteristic", default=None)
    parser.add_argument("--macos-use-bdaddr", action="store_true",help="when true use Bluetooth address instead of UUID on macOS")
    parser.add_argument("-a", "--address", metavar="<address>", help="the address of the bluetooth device to connect to", default=None)
    
    args = parser.parse_args()

    if args.discover:
        asyncio.run(discovery())
    
    elif args.list:
        if args.address is None:
            print("Device address must be specified")
            parser.print_help()
            exit(-1)
        else:
            asyncio.run(list_services(args.address))
    
    elif args.configure:
        if args.address is None:
            print("Device address must be specified")
            parser.print_help()
            exit(-1)
        else:
            asyncio.run(send_configuration(args.address))

    elif args.read is not None:
        if args.address is None:
            print("Device address must be specified")
            parser.print_help()
            exit(-1)
        else:
            if args.read in config.READ_CHAR_DICT:
                asyncio.run(read(args.address, config.READ_CHAR_DICT[args.read][1]))
            else:
                print("Characteristic not accepted")

    else:
        if args.address is None:
            print("Device address must be specified")
            parser.print_help()
            exit(-1)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            blestream.start_stream_processing()
            asyncio.ensure_future(read_data_stream(args.address))
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            print("Exiting...")
            loop.close()
