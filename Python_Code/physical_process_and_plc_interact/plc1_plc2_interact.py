import time
import easymodbus.modbusClient

TARGET1 = "192.168.1.220"   # plc1 codesys
TARGET2 = "192.168.1.16"    # plc2 openplc

plc1 = easymodbus.modbusClient.ModbusClient(TARGET1, 502)
plc1.connect()

plc2 = easymodbus.modbusClient.ModbusClient(TARGET2, 502)
plc2.connect()

# plc1.timeout = 500000
# plc2.timeout = 500000

while True:
    try:
        
        '''
        lettura request da parte di plc2 (apertura o chiusura della valvola tra vasca1 e vasca2 basandosi sul livello di acqua di vasca2)
        e inoltro a plc1
        '''
        
        req_valve_plc1 = plc2.read_coils(0, 1) # legge dal registro %QX0.0 usato dal plc openplc per scrivere la request
        if req_valve_plc1[0] is not None:      # la lettura potrebbe fallire
            plc1.write_single_coil(0, req_valve_plc1[0])

        print("Request:", req_valve_plc1)

        time.sleep(1.5)
    except KeyboardInterrupt:
        print("Close connection")
        plc1.close()
        plc2.close()
        break
    except Exception as e:
        print(e)
        pass
