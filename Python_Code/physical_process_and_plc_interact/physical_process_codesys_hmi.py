import time

import easymodbus.modbusClient

# Indirizzii IP PLC
TARGET1 = "192.168.1.219"   # PLC1 codesys
TARGET2 = "192.168.1.15"    # PLC2 openplc
TARGET3 = "192.168.1.240"   # PLC3 beckoff
TARGET4 = "192.168.1.79"    # HMI in codesys


# Connessione ai PLC
plc1 = easymodbus.modbusClient.ModbusClient(TARGET1, 502)
plc1.connect()

plc2 = easymodbus.modbusClient.ModbusClient(TARGET2, 502)
plc2.connect()

plc3 = easymodbus.modbusClient.ModbusClient(TARGET3, 502)
plc3.connect()

hmi = easymodbus.modbusClient.ModbusClient(TARGET4, 502)
hmi.connect()


# Inizializzazione variabili
count_water1 = 45
count_water2 = 0
count_water3 = 0

plc1.timeout = 500000
plc2.timeout = 500000
plc3.timeout = 500000
hmi.timeout = 500000

def initialize_variable():
    while True:
        try:
            time.sleep(1)
            print("Inizializzazione variabili...")    #inizializzazione livello dell'acqua

            # inizializzazione HMI
            hmi.write_single_register(0, count_water1)  # livello acqua vasca 1
            hmi.write_single_register(1, count_water2)  # livello acqua vasca 2
            hmi.write_single_register(2, count_water3)  # livello acqua vasca 3
            hmi.write_single_coil(0, False) # pompa 1 di feedback spenta
            hmi.write_single_coil(1, False) # valvola tra vasca 1 e 2 di feedback spenta 
            hmi.write_single_coil(2, False) # pompa 3 di feedback spenta

            # inizializzazione PLC
            plc1.write_single_register(0, count_water1) # livello acqua vasca 1
            plc2.write_single_register(0, count_water2) # livello acqua vasca 2 (registro holding %QW0 usato dal plc openplc)
            plc3.write_single_register(32768, count_water3) # livello acqua vasca 3
            plc1.write_single_coil(0, False) # Request plc 1 (la vasca 2 a start time non deve ricevere acqua dalla vasca 1, questo vale finchè non viene avviato il processo di interazione tra plc1 e plc2) 
            break
        except Exception as e:
            print(e)
            pass

        except KeyboardInterrupt:
            plc1.close()
            plc2.close()
            plc3.close()
            hmi.close()
            break


initialize_variable()
print("Inizio processo fisico...")


while True:
    try:

        time.sleep(1)

        # Aggiornamento HMI
        info_plc1 = plc1.read_discreteinputs(0, 2)   # [pompa, valvola] dati dei registri del PLC1
        pump_3 = plc3.read_discreteinputs(32768, 1)  # valore della pompa del PLC3
        hmi.write_single_coil(0, info_plc1[0])
        hmi.write_single_coil(1, info_plc1[1])
        hmi.write_single_coil(2, pump_3[0])

        print(f"Pompa1: [{info_plc1[0]}], Valvola: [{info_plc1[1]}], Pompa3: [{pump_3[0]}]")

        # Controllo pompa della terza vasca
        if pump_3[0]:
            count_water3 -= 1
            plc3.write_single_register(32768, count_water3)    # aggiornamento livello acqua su plc3
            hmi.write_single_register(2, count_water3)         # scrittura su hmi per aggiornare l'interfaccia visuale

            count_water2 += 1
            plc2.write_single_register(0, count_water2)
            hmi.write_single_register(1, count_water2)


        # Acqua che esce (clean water)
        if count_water2 >= 10:
            count_water2 -= 2
            plc2.write_single_register(0, count_water2)
            hmi.write_single_register(1, count_water2)

            count_water3 += 1
            plc3.write_single_register(32768, count_water3)
            hmi.write_single_register(2, count_water3)

        # Pompa1 aperta e valvola verso la vasca 2 aperta (livello vasca1 aumenta, livello vasca2 aumenta)
        if info_plc1[0] and info_plc1[1]:
            count_water1 += 2
            count_water2 += 2
            plc1.write_single_register(0, count_water1)
            plc2.write_single_register(0, count_water2)
            hmi.write_single_register(0, count_water1)
            hmi.write_single_register(1, count_water2)


        # Pompa1 aperta e valvola verso la vasca2 chiusa, livello vasca1 aumenta, livello vasca2 invariato
        if info_plc1[0] and (info_plc1[1] == False):
            count_water1 += 4
            plc1.write_single_register(0, count_water1)
            hmi.write_single_register(0, count_water1)


        # Pompa1 chiusa e valvola verso la vasca2 aperta, livello vasca1 diminuisce livello vasca 2 aumenta
        if (info_plc1[0] == False) and info_plc1[1]:
            count_water1 -= 2
            plc1.write_single_register(0, count_water1)
            hmi.write_single_register(0, count_water1)

            count_water2 += 2
            plc2.write_single_register(0, count_water2)
            hmi.write_single_register(1, count_water2)

    except KeyboardInterrupt:
        print("Close connection")
        if plc1.is_connected():
            plc1.close()
        if plc2.is_connected():
            plc2.close()
        if plc3.is_connected():
            plc3.close()
        if hmi.is_connected():
            hmi.close()
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
        if hmi.is_connected():
            hmi.close()
        break






