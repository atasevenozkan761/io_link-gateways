# IO-Link Multi-Protokoll-Gateway

**Reproduzierbares Open-Source-Paket — Schritt-für-Schritt-Anleitung**

Entwicklung eines Low-Cost Multi-Protokoll-Gateways für IO-Link-Sensorik

Gruppe 4 · Projekt 04 | TU Berlin — Institut für Werkzeugmaschinen und Fabrikbetrieb (IWF) | SS 2026

---

Dieses Dokument beschreibt vollständig, wie das entwickelte IO-Link Gateway nachgebaut und in Betrieb genommen werden kann. Es richtet sich auch an Personen ohne Vorkenntnisse in Linux oder Raspberry Pi.

**Quellcode (GitHub):** <https://github.com/atasevenozkan761/io_link-gateways>

---

## Inhaltsverzeichnis

1. [Hardwareliste](#1-hardwareliste)
2. [Schaltplan](#2-schaltplan)
3. [Bauanleitung](#3-bauanleitung)
   - 3.1 [Raspberry Pi Imager herunterladen](#31-raspberry-pi-imager-herunterladen)
   - 3.2 [Betriebssystem auf SD-Karte schreiben](#32-betriebssystem-auf-sd-karte-schreiben)
   - 3.3 [Raspberry Pi starten und verbinden](#33-raspberry-pi-starten-und-verbinden)
   - 3.4 [System aktualisieren](#34-system-aktualisieren)
   - 3.5 [SPI-Bus aktivieren](#35-spi-bus-aktivieren)
   - 3.6 [IOL HAT Pro montieren](#36-iol-hat-pro-montieren)
   - 3.7 [Python-Bibliotheken installieren](#37-python-bibliotheken-installieren)
   - 3.8 [Quellcode herunterladen](#38-quellcode-herunterladen)
   - 3.9 [Sensor anschließen und testen](#39-sensor-anschließen-und-testen)
4. [Dienste starten](#4-dienste-starten)
   - 4.1 [Manuell starten (zum Testen)](#41-manuell-starten-zum-testen)
   - 4.2 [Als Systemdienst (startet automatisch beim Booten)](#42-als-systemdienst-startet-automatisch-beim-booten)
5. [Protokoll-Konfiguration anpassen](#5-protokoll-konfiguration-anpassen)
   - 5.1 [MQTT — mqtt_publisher.py](#51-mqtt--mqtt_publisherpy)
   - 5.2 [Modbus TCP — modbus_server.py](#52-modbus-tcp--modbus_serverpy)
   - 5.3 [OPC UA — opcua_server.py](#53-opc-ua--opcua_serverpy)
   - 5.4 [REST API — rest_api.py](#54-rest-api--rest_apipy)
6. [Protokolle testen](#6-protokolle-testen)
   - 6.1 [MQTT](#61-mqtt)
   - 6.2 [Modbus TCP](#62-modbus-tcp)
   - 6.3 [OPC UA](#63-opc-ua)
   - 6.4 [REST API](#64-rest-api)
7. [Allgemeine Befehle — Kurzreferenz](#7-allgemeine-befehle--kurzreferenz)
8. [Quellcode](#8-quellcode)
9. [Literaturverzeichnis](#9-literaturverzeichnis)

---

## 1. Hardwareliste

| Komponente | Modell / Bezeichnung | Stückzahl |
|---|---|---|
| Einplatinenrechner | Raspberry Pi 5 (4 GB RAM) | 1 |
| IO-Link HAT | Pinetek IOL HAT Pro PT-1203 | 1 |
| 24-V-Netzteil | Pinetek PT-1320 | 1 |
| IO-Link-Sensor | ifm KG6000 (kapazitiv) | 1 |
| Verbindungskabel | M12-Kabel | 1 |
| Speicherkarte | microSD, min. 16 GB | 1 |
| Laptop / PC | Für Konfiguration und Zugriff | 1 |
| Smartphone (optional) | Als WLAN-Hotspot | 1 |

---

## 2. Schaltplan

Vollständiger Schaltplan: `Anschlusszeichnung_RaspberryPi_IOLHATPro_4Ports.pdf`

- 24 V DC: Netzteil PT-1320 → IOL HAT Pro (L+ / L-)
- 5 V DC: IOL HAT Pro interner Regler → Raspberry Pi 5 (GPIO-Header)
- SPI-Bus: RPi5 ↔ IOL HAT Pro — MOSI, MISO, SCLK, CS0
- IO-Link Port 1 (M12): Pin 1 = L+ (24 V), Pin 3 = GND, Pin 4 = C/Q
- Gemeinsame GND-Referenz für alle Komponenten zwingend erforderlich

---

## 3. Bauanleitung

### 3.1 Raspberry Pi Imager herunterladen

Vor der Installation das Programm Raspberry Pi Imager auf dem Laptop/PC installieren. Es schreibt das Betriebssystem auf die SD-Karte und ist kostenlos verfügbar:

<https://www.raspberrypi.com/software/>

Herunterladen, installieren und öffnen. Verfügbar für Windows, macOS und Linux.

### 3.2 Betriebssystem auf SD-Karte schreiben

SD-Karte in den Laptop/PC einstecken. Im Raspberry Pi Imager:

- Gerät: Raspberry Pi 5
- Betriebssystem: Raspberry Pi OS Lite (64-bit)
- Speicher: eingesteckte SD-Karte

Das Zahnrad-Symbol (Einstellungen) öffnen und eintragen:

- Hostname: `iolgateway.local`
- SSH aktivieren (Passwort-Authentifizierung)
- Benutzername: `pi`, Passwort frei wählbar
- WLAN: SSID und Passwort des Netzwerks, Ländercode: DE

> **Hinweis:** Wir haben einen Smartphone-Hotspot als WLAN-Zugangspunkt verwendet. Hotspot am Smartphone aktivieren, Passwort hier eintragen. Laptop ebenfalls mit demselben Hotspot verbinden.

Auf „Schreiben" klicken (ca. 3–5 Minuten). SD-Karte danach sicher auswerfen.

### 3.3 Raspberry Pi starten und verbinden

SD-Karte in den Raspberry Pi 5 einlegen, Stromversorgung anschließen. Das Pi verbindet sich automatisch mit dem konfigurierten WLAN.

Erreichbarkeit prüfen (Laptop-Terminal):

```bash
ping iolgateway.local
```

Per SSH verbinden:

```bash
ssh pi@iolgateway.local
```

> **Hinweis:** Falls `iolgateway.local` nicht gefunden wird: IP-Adresse im Hotspot-Menü des Smartphones nachschauen, dann `ssh pi@<IP-Adresse>` verwenden.

### 3.4 System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.5 SPI-Bus aktivieren

```bash
sudo raspi-config
```

Pfad: Interface Options → SPI → Yes → OK → Finish. Anschließend:

```bash
sudo reboot
```

Nach dem Neustart prüfen:

```bash
ls /dev/spi*
```

Erwartete Ausgabe: `/dev/spidev0.0  /dev/spidev0.1`

### 3.6 IOL HAT Pro montieren

Pi ausschalten, Strom trennen, HAT aufstecken, Strom wieder anschließen:

```bash
sudo shutdown -h now
```

### 3.7 Python-Bibliotheken installieren

```bash
pip3 install iolmaster paho-mqtt pymodbus asyncua flask --break-system-packages
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

### 3.8 Quellcode herunterladen

```bash
git clone https://github.com/atasevenozkan761/io_link-gateways.git
cd io_link-gateways
```

### 3.9 Sensor anschließen und testen

KG6000 über M12-Kabel an Port 1 anschließen, dann:

```bash
python3 sensors/connection_test.py
```

Erwartete Ausgabe: `✅ Prozessdaten gelesen — Sensor funktioniert korrekt.`

---

## 4. Dienste starten

### 4.1 Manuell starten (zum Testen)

```bash
python3 protocols/mqtt_publisher.py
python3 protocols/modbus_server.py
python3 protocols/opcua_server.py
python3 protocols/rest_api.py
```

Mit `Strg+C` stoppen.

### 4.2 Als Systemdienst (startet automatisch beim Booten)

Unit-Datei anlegen (Beispiel MQTT, für die anderen analog):

```bash
sudo nano /etc/systemd/system/mqtt-publisher.service
```

Inhalt:

```ini
[Unit]
Description=IO-Link MQTT Publisher
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/io_link-gateways/protocols/mqtt_publisher.py
WorkingDirectory=/home/pi/io_link-gateways
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Speichern: `Strg+O` → Enter → `Strg+X`. Dasselbe für `modbus-server.service`, `opcua-server.service`, `rest-api.service`.

Alle aktivieren:

```bash
sudo systemctl enable --now mqtt-publisher.service
sudo systemctl enable --now modbus-server.service
sudo systemctl enable --now opcua-server.service
sudo systemctl enable --now rest-api.service
```

---

## 5. Protokoll-Konfiguration anpassen

Alle Einstellungen befinden sich am Anfang der jeweiligen Python-Datei. Datei öffnen und bearbeiten:

```bash
nano protocols/<dateiname>.py
```

Speichern mit `Strg+O` → Enter → `Strg+X`. Danach Dienst neu starten:

```bash
sudo systemctl restart <dienstname>.service
```

### 5.1 MQTT — `mqtt_publisher.py`

Anpassbare Einstellungen:

```python
BROKER      = "localhost"   # IP-Adresse des MQTT-Brokers
BROKER_PORT = 1883          # Port des Brokers
TOPIC       = "iolink/gateway/gw01/port/1/process_data"  # Topic-Pfad
time.sleep(0.5)             # Sendeintervall — 0.5 = 2 Hz, 0.2 = 5 Hz
```

> **Hinweis:** Wenn ein externer Broker (z. B. in der Cloud) verwendet wird, die IP-Adresse des Brokers bei `BROKER` eintragen.

### 5.2 Modbus TCP — `modbus_server.py`

```python
MODBUS_TCP_PORT = 5020      # Port ändern falls nötig
store.setValues(3, 0, [state, value])  # Register-Mapping
```

Register-Belegung ändern — Beispiel: drittes Register für Zeitstempel hinzufügen:

```python
store.setValues(3, 0, [state, value, int(time.time()) % 65535])
```

> **Hinweis:** Modbus überträgt nur Integer (0–65535). Gleitkommazahlen müssen vorher umgerechnet werden.

### 5.3 OPC UA — `opcua_server.py`

```python
OPCUA_ENDPOINT = "opc.tcp://0.0.0.0:4840/gateway/server/"  # Port / Pfad
uri = "http://tu-berlin.de/iwf/iolink-gateway"              # Namespace-URI
```

Neuen Node hinzufügen — Beispiel: Zeitstempel als dritten Node:

```python
timestamp_var = await sensor_obj.add_variable(idx, "Timestamp", 0.0)
await timestamp_var.write_value(time.time())   # im Update-Loop
```

### 5.4 REST API — `rest_api.py`

```python
app.run(host="0.0.0.0", port=5000)  # Port ändern
```

Neuen Endpunkt hinzufügen — Beispiel: nur den Schaltzustand ausgeben:

```python
@app.route("/sensor/1/state", methods=["GET"])
def get_state():
    state, _ = read_kg6000()
    return jsonify({"switching_state": state})
```

---

## 6. Protokolle testen

### 6.1 MQTT

```bash
mosquitto_sub -h <IP-des-Pi> -t "iolink/gateway/gw01/port/1/process_data"
```

### 6.2 Modbus TCP

```python
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient("<IP-des-Pi>", port=5020)
client.connect()
r = client.read_holding_registers(0, 2)
print(f"HR0={r.registers[0]}  HR1={r.registers[1]}")
```

### 6.3 OPC UA

UaExpert herunterladen: <https://www.unified-automation.com/downloads/opc-ua-clients.html>

Endpunkt: `opc.tcp://<IP-des-Pi>:4840/gateway/server/`

Unter Objects → KG6000Sensor die Nodes `SwitchingState` und `Measurement` anzeigen.

### 6.4 REST API

```
http://<IP-des-Pi>:5000/sensor/1/data
http://<IP-des-Pi>:5000/sensor/1/status
```

---

## 7. Allgemeine Befehle — Kurzreferenz

**Verbindung**

| Aktion | Befehl |
|---|---|
| Pi per SSH verbinden | `ssh pi@iolgateway.local` |
| Pi per IP verbinden | `ssh pi@<IP-Adresse>` |
| SSH-Verbindung beenden | `exit` |

**Systemdienste**

| Aktion | Befehl |
|---|---|
| Dienst starten | `sudo systemctl start <dienstname>` |
| Dienst stoppen | `sudo systemctl stop <dienstname>` |
| Dienst neu starten | `sudo systemctl restart <dienstname>` |
| Status anzeigen | `sudo systemctl status <dienstname>` |
| Alle 4 Dienste Status | `sudo systemctl status mqtt-publisher modbus-server opcua-server rest-api` |
| Log live anzeigen | `journalctl -u <dienstname> -f` |
| Log der letzten Stunde | `journalctl -u <dienstname> --since "1 hour ago"` |

**System**

| Aktion | Befehl |
|---|---|
| Pi neu starten | `sudo reboot` |
| Pi herunterfahren | `sudo shutdown -h now` |
| System aktualisieren | `sudo apt update && sudo apt upgrade -y` |
| Quellcode aktualisieren (GitHub) | `git pull` |
| Aktuelle IP-Adresse anzeigen | `hostname -I` |
| Laufende Prozesse anzeigen | `htop` |

**Dateien bearbeiten**

| Aktion | Befehl |
|---|---|
| Datei öffnen | `nano <dateipfad>` |
| Speichern (in nano) | `Strg+O` → Enter |
| nano beenden | `Strg+X` |
| Dateiinhalt anzeigen | `cat <dateipfad>` |
| Verzeichnis anzeigen | `ls -la` |

**Skripte direkt ausführen**

| Skript | Befehl |
|---|---|
| Verbindungstest | `python3 sensors/connection_test.py` |
| Sensor-Leser (Live) | `python3 sensors/kg6000_reader.py` |
| MQTT manuell starten | `python3 protocols/mqtt_publisher.py` |
| Modbus manuell starten | `python3 protocols/modbus_server.py` |
| OPC UA manuell starten | `python3 protocols/opcua_server.py` |
| REST API manuell starten | `python3 protocols/rest_api.py` |
| Skript stoppen | `Strg+C` |

---

## 8. Quellcode

<https://github.com/atasevenozkan761/io_link-gateways>

```
io_link-gateways/
├── protocols/
│   ├── mqtt_publisher.py
│   ├── modbus_server.py
│   ├── opcua_server.py
│   └── rest_api.py
├── sensors/
│   ├── kg6000_reader.py
│   └── connection_test.py
└── diagnostic.sh
```

---

## 9. Literaturverzeichnis

[1] Pinetek Systems s.r.o.: IOL HAT Pro PT-1203 — IO-Link Master HAT für Raspberry Pi. Produktdatenblatt und technische Dokumentation. Online: <https://www.pinetek-networks.com/iol-hat-pro/>, abgerufen: 2026.

[2] ifm electronic gmbh: Kapazitiver Sensor KG6000 — Technische Daten und IODD-Beschreibung. Artikelnummer: KG6002. Online: <https://www.ifm.com/de/de/products/KG6002.html>, abgerufen: 2026.

[3] Raspberry Pi Ltd.: Raspberry Pi 5 — Produktdatenblatt und Hardwaredokumentation. Online: <https://www.raspberrypi.com/products/raspberry-pi-5/>, abgerufen: 2026.

[4] Eclipse Foundation: Eclipse Paho MQTT Python Client (paho-mqtt). Online: <https://eclipse.dev/paho/index.php?page=clients/python/index.php>, abgerufen: 2026.

[5] Automattic / pymodbus: PyModbus — A full modbus protocol written in python. Online: <https://pymodbus.readthedocs.io/>, abgerufen: 2026.

[6] python-asyncua Contributors: asyncua — Pure Python OPC UA Server and Client. Online: <https://github.com/FreeOpcUa/opcua-asyncio>, abgerufen: 2026.

[7] Pallets Projects: Flask — The Python micro framework for building web applications. Online: <https://flask.palletsprojects.com/>, abgerufen: 2026.

[8] IEC (International Electrotechnical Commission): IEC 61131-9 — Programmable controllers — Part 9: Single-drop digital communication interface for small sensors and actuators (SDCI). Genf: IEC, 2013.

[9] Ataseven, Ö. et al.: io_link-gateways — Quellcode des IO-Link Multi-Protokoll-Gateways. GitHub-Repository: <https://github.com/atasevenozkan761/io_link-gateways>, 2026.
