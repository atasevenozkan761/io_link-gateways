import sys
sys.path.insert(0, '/home/pmf04/iol-hat/examples/python')
import iolhat
import time

PORT = 1

print("Sensor-Verbindungstest wird gestartet...")
try:
    iolhat.power(PORT, 1)
    print("✅ Power-Befehl erfolgreich — Daemon und TCP-Verbindung funktionieren")
    time.sleep(1)
    data = iolhat.pd(PORT, 0, 2, None)
    print(f"✅ Prozessdaten gelesen: {data.hex()}")
    print("SENSOR FUNKTIONIERT VOLLSTÄNDIG")
except Exception as e:
    print(f"❌ Fehler: {e}")
    print("Sensor/HAT Pro funktioniert noch nicht korrekt")

