import time
import easymodbus.modbusClient

# Indirizzii IP PLC
TARGET1 = "192.168.1.219"   # PLC1 CODESYS
TARGET2 = "192.168.1.15"    # PLC2 OpenPLC
TARGET3 = "192.168.1.240"   # PLC3 BECKHOFF TwinCAT/BSD
TARGET4 = "192.168.1.79"    # hmi1 in CODESYS
TARGET5 = "192.168.1.175"   # hmi1 in BECKHOFF TwinCAT/BSD


# Connessione ai PLC
plc1 = easymodbus.modbusClient.ModbusClient(TARGET1, 502)
plc1.connect()

plc2 = easymodbus.modbusClient.ModbusClient(TARGET2, 502)
plc2.connect()

plc3 = easymodbus.modbusClient.ModbusClient(TARGET3, 502)
plc3.connect()

hmi1 = easymodbus.modbusClient.ModbusClient(TARGET4, 502)
hmi1.connect()

hmi2 = easymodbus.modbusClient.ModbusClient(TARGET5, 502)
hmi2.connect()


# Inizializzazione variabili
count_water1 = 45
count_water2 = 0
count_water3 = 0

plc1.timeout = 500000
plc2.timeout = 500000
plc3.timeout = 500000
hmi1.timeout = 500000
hmi2.timeout = 500000


def hmi_write_coil(index: int, value: bool):
    '''Passa all'HMI i valori di pompa e valvola tramita coil'''
    hmi1.write_single_coil(index, value)
    hmi2.write_single_coil(32768 + index, value)

def hmi_write_register(index: int, value: int):
    '''Passa all'HMI il livello dell'acqua tramite Holding register'''
    hmi1.write_single_register(index, value)
    hmi2.write_single_register(32768 + index, value)

def initialize_variable():
    while True:
        try:
            time.sleep(1)
            print("Inizializzazione variabili...")

            # inizializzazione HMI
            hmi_write_register(0, count_water1)     # livello acqua vasca 1
            hmi_write_register(1, count_water2)     # livello acqua vasca 2
            hmi_write_register(2, count_water3)     # livello acqua vasca 3
            hmi_write_coil(0, False)    # pompa 1 di feedback spenta
            hmi_write_coil(1, False)    # valvola tra vasca 1 e 2 di feedback spenta 
            hmi_write_coil(2, False)    # pompa 3 di feedback spenta

            # inizializzazione PLC
            plc1.write_single_register(0, count_water1)     # livello acqua vasca 1
            plc2.write_single_register(0, count_water2)     # livello acqua vasca 2 (registro holding %QW0 usato dal plc openplc)
            plc3.write_single_register(32768, count_water3) # livello acqua vasca 3
            plc1.write_single_coil(0, False)                # Request plc 1 (la vasca 2 a start time non deve ricevere acqua dalla vasca 1, questo vale finchè non viene avviato il processo di interazione tra plc1 e plc2) 
            break
        except Exception as e:
            print(e)
            pass

        except KeyboardInterrupt:
            plc1.close()
            plc2.close()
            plc3.close()
            hmi1.close()
            hmi2.close()
            break


initialize_variable()
print("Inizio processo fisico...")

while True:
    try:

        time.sleep(1)

        # Lettura valori
        info_plc1 = plc1.read_discreteinputs(0, 2)   # [pompa, valvola] dati dei registri del PLC1
        pump_3 = plc3.read_discreteinputs(32768, 1)  # valore della pompa del PLC3

        # Aggiornamento HMI
        hmi_write_coil(0, info_plc1[0])
        hmi_write_coil(1, info_plc1[1])
        hmi_write_coil(2, pump_3[0])

        print(f"Pompa1: [{info_plc1[0]}], \tValvola: [{info_plc1[1]}], \tPompa3: {pump_3}")

        # Controllo pompa della terza vasca
        if pump_3[0]:
            count_water3 -= 1
            plc3.write_single_register(32768, count_water3)     # aggiornamento livello acqua su plc3
            hmi_write_register(2, count_water3)                 # scrittura su HMI per aggiornare l'interfaccia visuale

            count_water2 += 1
            plc2.write_single_register(0, count_water2)
            hmi_write_register(1, count_water2)


        # Acqua che esce (clean water)
        if count_water2 >= 10:
            count_water2 -= 2
            plc2.write_single_register(0, count_water2)
            hmi_write_register(1, count_water2)

            count_water3 += 1
            plc3.write_single_register(32768, count_water3)
            hmi_write_register(2, count_water3)

        # Pompa1 aperta e valvola verso la vasca 2 aperta (livello vasca1 aumenta, livello vasca2 aumenta)
        if info_plc1[0] and info_plc1[1]:
            count_water1 += 2
            count_water2 += 2
            plc1.write_single_register(0, count_water1)
            plc2.write_single_register(0, count_water2)
            hmi_write_register(0, count_water1)
            hmi_write_register(1, count_water2)


        # Pompa1 aperta e valvola verso la vasca2 chiusa, livello vasca1 aumenta, livello vasca2 invariato
        if info_plc1[0] and (info_plc1[1] == False):
            count_water1 += 4
            plc1.write_single_register(0, count_water1)
            hmi_write_register(0, count_water1)


        # Pompa1 chiusa e valvola verso la vasca2 aperta, livello vasca1 diminuisce livello vasca 2 aumenta
        if (info_plc1[0] == False) and info_plc1[1]:
            count_water1 -= 2
            plc1.write_single_register(0, count_water1)
            hmi_write_register(0, count_water1)

            count_water2 += 2
            plc2.write_single_register(0, count_water2)
            hmi_write_register(1, count_water2)

    except KeyboardInterrupt:
        print("Close connection")
        if plc1.is_connected():
            plc1.close()
        if plc2.is_connected():
            plc2.close()
        if plc3.is_connected():
            plc3.close()
        if hmi1.is_connected():
            hmi1.close()
        if hmi2.is_connected():
            hmi2.close()
        break
    except Exception as e:
        print("Close connection")
        print(e)
        if plc1.is_connected():
            plc1.close()
        if plc2.is_connected():
            plc2.close()
        if plc3.is_connected():
            plc3.close()
        if hmi1.is_connected():
            hmi1.close()
        if hmi2.is_connected():
            hmi2.close()
        break






