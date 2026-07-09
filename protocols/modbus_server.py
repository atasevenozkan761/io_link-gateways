import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import struct
import time
import threading

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartTcpServer

PORT = 1
MODBUS_TCP_PORT = 5020

def read_kg6000():
    data = iolhat.pd(PORT, 0, 2, None)
    raw = struct.unpack("!H", data)[0]
    switching_state = raw & 0x01
    measurement = (raw >> 1) & 0x7FFF
    return switching_state, measurement

def update_loop(store):
    while True:
        state, value = read_kg6000()
        # Holding Register 0 = switching_state, Register 1 = measurement
        store.setValues(3, 0, [state, value])
        print(f"Modbus register güncellendi: HR0={state}  HR1={value}")
        time.sleep(0.5)

def main():
    iolhat.power(PORT, 1)
    time.sleep(1)

    block = ModbusSequentialDataBlock(0, [0]*10)
    store = ModbusSlaveContext(hr=block)
    context = ModbusServerContext(slaves=store, single=True)

    t = threading.Thread(target=update_loop, args=(store,), daemon=True)
    t.start()

    print(f"Modbus TCP server başladı -> port {MODBUS_TCP_PORT}")
    StartTcpServer(context=context, address=("0.0.0.0", MODBUS_TCP_PORT))

if __name__ == "__main__":
    main()
