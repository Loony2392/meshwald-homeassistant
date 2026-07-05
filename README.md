# MeshWald – Home Assistant Integration

Bindet die [MeshWald](https://meshwald.de) Sensor-API (dezentrales LoRa-Mesh im
Märkischen Kreis) als Custom Integration in Home Assistant ein. Jeder Meshtastic-Node
wird als eigenes Gerät mit vier Sensoren angelegt:

- 🌡️ Temperatur (°C)
- 💧 Luftfeuchte (%)
- ⏲️ Luftdruck (hPa)
- 🍃 Luftgüte (IAQ)

## Voraussetzungen

- Ein MeshWald-Account unter [meshwald.de](https://meshwald.de) (kostenlos)
- Ein persönlicher API-Key (`mw_live_...`), erzeugt im Account-Bereich der Website

## Installation

### Über HACS (empfohlen)

1. HACS → Integrationen → Menü (⋮) → *Benutzerdefinierte Repositories*
2. Repository-URL: `https://github.com/Loony2392/meshwald-homeassistant`, Kategorie *Integration*
3. „MeshWald" installieren, Home Assistant neu starten

### Manuell

1. Ordner `custom_components/meshwald` in das `custom_components`-Verzeichnis
   deiner Home-Assistant-Konfiguration kopieren
2. Home Assistant neu starten

## Einrichtung

Einstellungen → Geräte & Dienste → Integration hinzufügen → „MeshWald" suchen.

Abgefragt werden:

| Feld | Bedeutung |
|---|---|
| Basis-URL | z. B. `https://meshwald.de` (Standardwert vorausgefüllt) |
| API-Key | Dein persönlicher Key aus dem Account-Bereich |

Die Integration ruft `GET /api/v1/data/nodes` und `GET /api/v1/data/sensors/{node}`
mit dem Header `X-API-Key` ab (Fair-Use-Limit der API: 60 Anfragen/Minute) und
aktualisiert alle 60 Sekunden.

## Sicherheit

- Der API-Key wird ausschließlich im verschlüsselten Home-Assistant-Storage
  (`config_entries`) abgelegt, niemals in Logs ausgegeben.
- Kommunikation ausschließlich über HTTPS zur konfigurierten Basis-URL.
- Bei ungültigem/widerrufenem Key markiert Home Assistant den Config-Entry
  automatisch als „Erneute Authentifizierung erforderlich".

## Projekt

Teil des [MeshWald-Projekts](https://meshwald.de) von Bastian Kolb / LOONY-TECH –
dezentrales LoRa-Mesh-Netzwerk für den Märkischen Kreis (Smart City, Bürgerfunk,
Krisenvorsorge).

## Lizenz

MIT, siehe [LICENSE](LICENSE).
