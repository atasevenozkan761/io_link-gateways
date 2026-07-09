import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import struct
import time

PORT = 1

def read_kg6000():
    data = iolhat.pd(PORT, 0, 2, None)
    raw = struct.unpack("!H", data)[0]
    switching_state = bool(raw & 0x01)          # bit 0
    measurement = (raw >> 1) & 0x7FFF           # bit 1-15
    return switching_state, measurement

if __name__ == "__main__":
    iolhat.power(PORT, 1)
    time.sleep(1)
    try:
        while True:
            state, value = read_kg6000()
            print(f"switching_state={state}  measurement={value}")
            time.sleep(0.3)
    except KeyboardInterrupt:
      0
