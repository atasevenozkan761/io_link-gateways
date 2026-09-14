import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import struct
import time
import json
import paho.mqtt.client as mqtt

# Konfiguration
PORT = 1
BROKER = "localhost"
BROKER_PORT = 1883
TOPIC = "iolink/gateway/gw01/port/1/process_data"


def read_kg6000():
    """Liest 2 Byte Prozessdaten vom KG6000 und dekodiert sie."""
    data = iolhat.pd(PORT, 0, 2, None)
    raw = struct.unpack("!H", data)[0]  # Big-Endian 16-Bit-Wert
    switching_state = bool(raw & 0x01)      # Bit 0 = Schaltzustand
    measurement = (raw >> 1) & 0x7FFF      # Bit 1â€“15 = Messwert (ADC-Rohwert)
    return switching_state, measurement


def main():
    client = mqtt.Client()
    client.connect(BROKER, BROKER_PORT, 60)
    client.loop_start()

    # Sensor einschalten, kurz warten bis IO-Link OPERATE-Zustand erreicht ist
    iolhat.power(PORT, 1)
    time.sleep(1)

    print(f"MQTT-Publisher gestartet -> Broker: {BROKER}:{BROKER_PORT}, Topic: {TOPIC}")

    try:
        while True:
            state, value = read_kg6000()

            # JSON-Payload zusammenstellen und verÃ¶ffentlichen
            payload = json.dumps({
                "switching_state": state,
                "measurement": value,
                "timestamp": time.time()
            })
            client.publish(TOPIC, payload)
            print(f"Gesendet: {payload}")

            time.sleep(0.5)  # 2 Hz Abtastrate

    except KeyboardInterrupt:
        print("\nGestoppt.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
