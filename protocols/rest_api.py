import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import struct
import time
from flask import Flask, jsonify

PORT = 1
app = Flask(__name__)

def read_kg6000():
    data = iolhat.pd(PORT, 0, 2, None)
    raw = struct.unpack("!H", data)[0]
    switching_state = bool(raw & 0x01)          # bit 0
    measurement = (raw >> 1) & 0x7FFF           # bit 1-15
    return switching_state, measurement

@app.route("/sensor/1/data", methods=["GET"])
def get_sensor_data():
    state, value = read_kg6000()
    return jsonify({
        "port": PORT,
        "switching_state": state,
        "measurement": value,
        "timestamp": time.time()
    })

@app.route("/sensor/1/status", methods=["GET"])
def get_status():
    return jsonify({"status": "ok", "port": PORT})

if __name__ == "__main__":
    iolhat.power(PORT, 1)
    time.sleep(1)
    print("REST API başladı -> http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)

