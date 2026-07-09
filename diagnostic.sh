#!/bin/bash
echo "===== SPI-Geräte ====="
ls -la /dev/spidev* 2>&1

echo ""
echo "===== Daemon wird neu gestartet ====="
sudo systemctl restart iol-master.service
sleep 3

echo ""
echo "===== Chip-Revision-Prüfung ====="
CHIP_ERROR=$(journalctl -u iol-master.service -n 20 --no-pager | grep -i "revision")
if [ -z "$CHIP_ERROR" ]; then
    echo "✅ Kein Chip-Revision-Fehler — HAT Pro ist elektrisch sichtbar"
else
    echo "❌ Chip-Revision-Fehler vorhanden:"
    echo "$CHIP_ERROR"
fi

echo ""
echo "===== Allgemeiner Dienststatus ====="
sudo systemctl status iol-master.service --no-pager | head -5

