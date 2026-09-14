import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import struct
import time
import threading

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartTcpServer

# Konfiguration
PORT = 1
MODBUS_TCP_PORT = 5020  # Port 502 erfordert root-Rechte, daher 5020


def read_kg6000():
    """Liest Prozessdaten vom KG6000 und gibt Schaltzustand + Messwert zurÃ¼ck."""
    data = iolhat.pd(PORT, 0, 2, None)
    raw = struct.unpack("!H", data)[0]
    switching_state = raw & 0x01            # Bit 0 = Schaltzustand (0 oder 1)
    measurement = (raw >> 1) & 0x7FFF      # Bit 1â€“15 = ADC-Rohwert
    return switching_state, measurement


def update_loop(store):
    """LÃ¤uft als Daemon-Thread und aktualisiert die Holding Register alle 500 ms."""
    while True:
        state, value = read_kg6000()
        # HR0 = Schaltzustand, HR1 = Messwert
        store.setValues(3, 0, [state, value])
        print(f"HR0={state}  HR1={value}")
        time.sleep(0.5)


def main():
    # Sensor einschalten
    iolhat.power(PORT, 1)
    time.sleep(1)

    # Modbus-Datenspeicher initialisieren (10 Register, alle mit 0 vorbelegt)
    block = ModbusSequentialDataBlock(0, [0] * 10)
    store = ModbusSlaveContext(hr=block)
    context = ModbusServerContext(slaves=store, single=True)

    # Aktualisierungs-Thread starten (daemon=True -> wird mit Hauptprozess beendet)
    t = threading.Thread(target=update_loop, args=(store,), daemon=True)
    t.start()

    print(f"Modbus-TCP-Server gestartet -> Port {MODBUS_TCP_PORT}")
    StartTcpServer(context=context, address=("0.0.0.0", MODBUS_TCP_PORT))


if __name__ == "__main__":
    main()
