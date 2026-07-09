import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import struct
import time
import json
import paho.mqtt.client as mqtt

PORT = 1
BROKER = "localhost"
BROKER_PORT = 1883
TOPIC = "iolink/gateway/gw01/port/1/process_data"

def read_kg6000():
    data = iolhat.pd(PORT, 0, 2, None)
    raw = struct.unpack("!H", data)[0]
    switching_state = bool(raw & 0x01)          # bit 0
    measurement = (raw >> 1) & 0x7FFF           # bit 1-15
    return switching_state, measurement

def main():
    client = mqtt.Client()
    client.connect(BROKER, BROKER_PORT, 60)
    client.loop_start()

    iolhat.power(PORT, 1)
    time.sleep(1)

    print(f"MQTT publisher başladı -> {BROKER}:{BROKER_PORT}, topic={TOPIC}")

    try:
        while True:
            state, value = read_kg6000()
            payload = json.dumps({
                "switching_state": state,
                "measurement": value,
                "timestamp": time.time()
            })
            client.publish(TOPIC, payload)
            print(f"Yayınlandı: {payload}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nDurduruldu")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
0


