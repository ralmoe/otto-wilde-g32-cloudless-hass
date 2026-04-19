# Otto Wilde G32 Home Assistant Integration

Custom Integration für den **Otto Wilde G32** mit direktem TCP-Empfang der Temperaturdaten.

## Allgemeine Funktionsweise

Der Otto Wilde G32 sendet seine Temoperaturdaten via WLAN an die Otto-Wilde-Cloud. Um diese Daten direkt und ohne Umweg über die Cloud in Home Assistant zu nutzen muss im Router für das lokale Netzwerk ein DNS-Eintrag gesetzt werden, der den Grill dazu veranlasst die Daten an eine lokale IP-Adresse (die der Home-Assistant-Installation) zu senden.

### DNS-Eintrag

- Domain: socket.ottowildeapp.com
- IP-Adresse für A-Record: IP-Adresse der lokalen Home-Assistant-Installation

#### Beispiel aus Unifi
<img width="404" height="450" alt="Persönlich_—_UniFi_Network" src="https://github.com/user-attachments/assets/9fd277fd-bbc7-4d32-a3ce-6e3fd6b3a449" />


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

### Screenshots
<img width="796" height="994" alt="Otto-Wilde Gauges" src="https://github.com/user-attachments/assets/1a6a6c79-1c88-4a19-9856-3b7108af50c7" />

<img width="497" height="791" alt="Otto-Wilde Cloudless Sensoren" src="https://github.com/user-attachments/assets/be702f08-c734-44f9-a3e5-bf9d0c6f5752" />

