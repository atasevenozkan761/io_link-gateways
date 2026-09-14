import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import struct
import time
from flask import Flask, jsonify

# Konfiguration
PORT = 1
app = Flask(__name__)


def read_kg6000():
    """Liest Prozessdaten vom KG6000 und gibt Schaltzustand + Messwert zurÃ¼ck."""
    data = iolhat.pd(PORT, 0, 2, None)
    raw = struct.unpack("!H", data)[0]
    switching_state = bool(raw & 0x01)      # Bit 0 = Schaltzustand
    measurement = (raw >> 1) & 0x7FFF      # Bit 1â€“15 = ADC-Rohwert
    return switching_state, measurement


@app.route("/sensor/1/data", methods=["GET"])
def get_sensor_data():
    """Gibt aktuelle Sensordaten als JSON zurÃ¼ck."""
    state, value = read_kg6000()
    return jsonify({
        "port": PORT,
        "switching_state": state,
        "measurement": value,
        "timestamp": time.time()
    })


@app.route("/sensor/1/status", methods=["GET"])
def get_status():
    """Einfacher Statuscheck â€” gibt ok zurÃ¼ck wenn der Dienst lÃ¤uft."""
    return jsonify({"status": "ok", "port": PORT})


if __name__ == "__main__":
    # Sensor einschalten, auf OPERATE-Zustand warten
    iolhat.power(PORT, 1)
    time.sleep(1)
    print("REST-API gestartet -> http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
