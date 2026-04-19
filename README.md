# Otto Wilde G32 Home Assistant Integration

Custom Integration für den **Otto Wilde G32** mit direktem TCP-Empfang der Temperaturdaten.

## Funktionen

- UI-basierter Setup-Flow in Home Assistant
- TCP-Listener im Hintergrund (asynchron)
- 8 Temperatur-Sensoren:
  - Zone 1
  - Zone 2 
  - Zone 3 
  - Zone 4
  - Kerntemperaturfühler 1
  - Kerntemperaturfühler 2
  - Kerntemperaturfühler 3
  - Kerntemperaturfühler 4

## Installation über HACS (Custom Repository)

1. Öffne **HACS** in Home Assistant.
2. Gehe zu **Integrationen**.
3. Öffne das Menü (oben rechts) → **Benutzerdefinierte Repositories**.
4. Füge dein Repository als Typ **Integration** hinzu.
5. Suche nach **Otto Wilde Cloudless** und installiere die Integration.
6. Starte Home Assistant neu.

## Manuelle Installation

1. Kopiere den Ordner `custom_components/owg` in dein Home-Assistant-Verzeichnis unter:
   - `<config>/custom_components/owg`
2. Starte Home Assistant neu.

## Konfiguration in Home Assistant

1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
2. Suche nach **Otto Wilde Cloudless**.
3. Trage folgende Werte ein:
   - IP-Adresse deines Ports
   - Port (Standard muss nicht verändert werden)
   - Timeout in Sekunden
4. Speichern.

## Optionen ändern

Nach dem Einrichten kannst du Port/IP/Timeout über die Integrations-Optionen anpassen.
