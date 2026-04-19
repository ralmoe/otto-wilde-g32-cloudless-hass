# OWG Home Assistant Integration

Custom Integration für den **Otto Wilde Grill (OWG)** mit direktem TCP-Empfang der Temperaturdaten.

## Funktionen

- UI-basierter Setup-Flow in Home Assistant
- TCP-Listener im Hintergrund (asynchron)
- 8 Sensoren:
  - Zone 1 Temperature
  - Zone 2 Temperature
  - Zone 3 Temperature
  - Zone 4 Temperature
  - External Probe 1 Temperature
  - External Probe 2 Temperature
  - External Probe 3 Temperature
  - External Probe 4 Temperature
- Dekodierung je Sensor mit Formel:
  - `(Byte1 * 100 + Byte2) / 10`
- Spezialfall `1500` → Sensor `unavailable`
- Globales Timeout: Wenn keine Daten innerhalb des Timeouts eintreffen, werden alle Sensoren auf `unavailable` gesetzt
- Single-Instance-Support (nur ein Grill)

## Standardwerte

- Listen IP (Grill-IP): `192.168.2.169`
- Port: `4501`
- Timeout (Sekunden): `60`

> Hinweis: Der TCP-Server bindet bewusst auf `0.0.0.0` (alle Interfaces). Die konfigurierte Listen-IP wird als erwartete Quell-IP des Grills verwendet.

## Installation über HACS (Custom Repository)

1. Öffne **HACS** in Home Assistant.
2. Gehe zu **Integrationen**.
3. Öffne das Menü (oben rechts) → **Benutzerdefinierte Repositories**.
4. Füge dein Repository als Typ **Integration** hinzu.
5. Suche nach **OWG** und installiere die Integration.
6. Starte Home Assistant neu.

## Manuelle Installation

1. Kopiere den Ordner `custom_components/owg` in dein Home-Assistant-Verzeichnis unter:
   - `<config>/custom_components/owg`
2. Starte Home Assistant neu.

## Konfiguration in Home Assistant

1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
2. Suche nach **OWG**.
3. Trage folgende Werte ein:
   - Listen IP (Grill-IP)
   - Port
   - Timeout in Sekunden
4. Speichern.

## Optionen ändern

Nach dem Einrichten kannst du Port/IP/Timeout über die Integrations-Optionen anpassen.

## Technische Details

- Plattform: `sensor`
- Device class: `temperature`
- Einheit: `°C`
- IOT class: `local_push`
- Sauberes Stoppen des TCP-Listeners beim Entladen der Integration
