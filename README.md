# TI-Monitoring

Dieses Tool dient der Überwachung verschiedener Komponenten der Telematikinfrastruktur (TI).

Es ist modular aufgebaut, sodass sich je nach Bedarf und Systemleistung auch nur einzelne Funktionen nutzen lassen.

Die Funktionen lassen sich wie folgt zusammenfassen:

* ****Abruf und Archivierung****<br>

  Die Kernfunktionalität besteht in der regelmäßigen Abfrage des Verfügbarkeitsstatus zentraler TI-Komponenten über öffentliche Schnittstellen der gematik GmbH. Die Ergebnisse werden strukturiert in einer HDF5-Datei gespeichert. So können auch für längere Beobachtungszeiträume statistische Auswertungen durchgeführt werden, um beispielsweise die Einhaltung von SLAs zu beurteilen.
  
  Neben den einzelnen Komponenten werden auch Statusinformationen verschiedener TI-Anwendungen regelmäßig über die TI-Lage-Schnittstelle abgerufen und gespeichert. Die aktuellen Daten werden ebenfalls in `data_cache.json` abgelegt und von der Web-App verwendet.

  Sowohl für die Komponenten als auch für die Anwendungen werden die aktuell benötigten Daten in der Datei `data_cache.json` zwischengespeichert. Dadurch kann die Web-App aktuelle Statusinformationen anzeigen, ohne bei jedem Seitenaufruf erneut auf die externen Schnittstellen zugreifen zu müssen.

* ****Benachrichtigungen****<br>

  Bei Änderungen der Verfügbarkeit können Benachrichtigungen per E-Mail und/oder Push-Benachrichtigung versendet werden. Zur Filterung der TI-Komponenten kann wahlweise eine White- oder Blacklist definiert werden.

* ****Web-App****<br>

  Der aktuelle Status der TI-Anwendungen sowie sämtlicher TI-Komponenten lässt sich nach Produkten gruppiert in einer interaktiven Web-App einsehen. Darüber hinaus kann für die einzelnen Komponenten eine Statistik der letzten Stunden beziehungsweise der aktuellen Woche aufgerufen werden.

## Architektur

Der Abruf externer Daten erfolgt ausschließlich über `cron.py`. Die Web-App greift nicht direkt auf die externen Schnittstellen zu.

Der grundsätzliche Datenfluss sieht wie folgt aus:

```text
cron.py
  │
  ├── update_cis()
  │     ├── API v1 der gematik Gmbh
  │     ├── data.hdf5
  │     └── data_cache.json → cis
  │                │
  │                ▼
  │           Web-App / Dash
  │
  └── update_apps()
        ├── API v2 der gematik Gmbh
        ├── data.hdf5
        └── data_cache.json → app_status
                    │
                    ▼
              Web-App / Dash
```

Die HDF5-Datei dient dabei als historischer Datenspeicher. Die Datei `data_cache.json` enthält hingegen nur die aktuell von der Web-App benötigten Daten.

## Einrichtung der Python-Umgebung

Das Tool kann beispielsweise auf einem (virtuellen) Server, NAS oder einem idealerweise permanent laufenden Rechner installiert werden. Systemanforderungen und Einrichtungsaufwand variieren je nach Umfang der genutzten Funktionen.

Für die Grundfunktionalität (Abruf und Archivierung von Verfügbarkeitsinformationen) sind die Pakete erforderlich, die in `mylibrary.py` importiert werden. Für die Web-App sind zusätzliche Pakete, insbesondere `dash`, zu installieren. Außerdem werden für einen produktiven Betrieb beispielsweise ein Webserver wie nginx und gegebenenfalls ein Applikationsserver wie uWSGI benötigt.

Weitere Details zur Funktionsweise und Konfiguration finden sich weiter unten.

Allgemein empfiehlt sich die Erstellung einer virtuellen Python-Umgebung. Dies geschieht beispielsweise unter Ubuntu 24.04 LTS mit dem User `lukas` wie folgt:

```bash
sudo apt update && sudo apt upgrade
sudo apt install python3-venv

python3 -m venv /home/lukas/myenv
source /home/lukas/myenv/bin/activate
```

Die erforderlichen Pakete können daraufhin beispielsweise mit `pip3 install <module>` installiert werden:

```bash
pip3 install h5py
```

## Abruf und Archivierung

Abruf und Archivierung erfolgen durch das Skript `cron.py`, das alle fünf Minuten durch einen Cronjob ausgeführt werden sollte. Um möglichst die aktuellsten Daten abzugreifen, empfiehlt sich ein minimaler Versatz zum Bereitstellungszeitpunkt der Daten:

```cron
# m h  dom mon dow   command

2-59/5 * * * * /bin/bash -c 'source myenv/bin/activate && python cron.py'
```

Beim ersten Ausführen von `cron.py` wird die Datei `data.hdf5` automatisch angelegt, sofern sie noch nicht existiert.

Die HDF5-Datei enthält folgende Gruppenstruktur:

```text
.
├── availability
│   ├── CI-0000001
│   │   └── history
│   ├── CI-0000002
│   │   └── history
│   └── ...
├── configuration_items
│   ├── CI-0000001
│   ├── CI-0000002
│   └── ...
└── app_status
    ├── erezept
    │   └── history
    ├── epa
    │   └── history
    ├── kim
    │   └── history
    ├── vsdm
    │   └── history
    ├── wanda
    │   └── history
    ├── ogd
    │   └── history
    └── tianschluss
        └── history
```

### `availability`

Unter `availability` wird für jedes Konfigurationsobjekt eine eigene Gruppe angelegt. Darin befindet sich der Datensatz `history`, der die historischen Werte der Verfügbarkeit enthält.

Die Verfügbarkeit wird als Integer gespeichert:

* `0`: nicht verfügbar
* `1`: verfügbar

Jeder historische Eintrag enthält einen Zeitstempel und den zu diesem Zeitpunkt gemeldeten Verfügbarkeitswert.

### `configuration_items`

Unter `configuration_items` werden die aktuellen Eigenschaften der einzelnen Konfigurationsobjekte gespeichert.

Dazu gehören unter anderem:

* `tid`
* `bu`
* `organization`
* `pdt`
* `product`
* `name`
* `comment`
* `time`
* `current_availability`
* `availability_difference`

`current_availability` enthält den aktuell bekannten Verfügbarkeitsstatus.

`availability_difference` beschreibt die Veränderung gegenüber dem vorherigen Wert:

* `-1`: nicht mehr verfügbar
* `0`: keine Veränderung
* `1`: wieder verfügbar

Bei einer Aktualisierung werden die aktuellen Eigenschaften überschrieben, während die historischen Verfügbarkeitsdaten unter `availability` erhalten bleiben.

### `app_status`

Unter `app_status` werden die historischen Statusinformationen der überwachten TI-Anwendungen gespeichert.

Für jede Anwendung existiert eine eigene Gruppe mit dem Datensatz `history`. Jeder Eintrag enthält einen Zeitstempel und den zu diesem Zeitpunkt gemeldeten Status.

Die aktuellen Statusinformationen werden zusätzlich in `data_cache.json` gespeichert und von der Web-App verwendet.

Je nach Systemleistung kann es sinnvoll sein, die Datei `data.hdf5` von Zeit zu Zeit zu archivieren. Hierzu kann die Datei beispielsweise per Cronjob in ein Archiv-Verzeichnis verschoben werden.

## `data_cache.json`

Die Datei `data_cache.json` enthält die aktuellsten Daten, die von der Web-App benötigt werden.

Sie enthält insbesondere:

```json
{
  "cis": [],
  "app_status": {},
  "cached_at": "..."
}
```

Die Daten werden durch `cron.py` aktualisiert. Die Web-App liest ausschließlich diese Cache-Datei und führt selbst keine Abfragen der externen TI-Schnittstellen durch.

Die Datei wird atomar aktualisiert, sodass die Web-App auch während einer Aktualisierung auf eine konsistente Version der Daten zugreifen kann.

## Benachrichtigungen

### E-Mail

Auf Wunsch können bei Änderungen der Verfügbarkeit Benachrichtigungen per E-Mail versendet werden. Dies geschieht ebenfalls über das Skript `cron.py`, sofern in der Datei `myconfig.py` die Variable `notifications` den Wert `True` besitzt. Die SMTP-Verbindungsdaten werden ebenfalls in der Datei `myconfig.py` hinterlegt.

In der Datei `notifications.json` können mehrere Profile definiert werden. Ein Profil besteht aus folgenden Eigenschaften:

| Name         | Beschreibung                                                                                              |
| ------------ | --------------------------------------------------------------------------------------------------------- |
| `name`       | Name des Profils (wird in der Anrede verwendet)                                                           |
| `recipients` | Liste mit mindestens einer E-Mail-Adresse, z. B. `["mail1@example.com", "mail2@example.com"]`             |
| `ci_list`    | Liste von Konfigurationsobjekten, z. B. `["CI-000001", "CI-0000002"]`                                     |
| `type`       | entweder `blacklist` oder `whitelist` (legt fest, wie die Liste der Konfigurationsobjekte behandelt wird) |
| `push_topic` | Thema für Push-Benachrichtigungen via ntfy, z. B. `TI`                                                    |

Hier ein Beispiel für eine E-Mail-Benachrichtigung:

![E-Mail-Benachrichtigung über Störung (Beispiel)](docs/img/Mail%20Beispiel%20Störung.png "E-Mail-Benachrichtigung über Störung (Beispiel)")

### Push-Benachrichtigungen via ntfy

Sofern eine [ntfy-Instanz](https://github.com/binwiederhier/ntfy) vorhanden ist, lassen sich optional Push-Benachrichtigungen versenden. Hierfür muss im Benachrichtigungsprofil ein Thema (`push_topic`) angegeben werden.

Zudem sind in der Datei `myconfig.py` die URL zur ntfy-Instanz (`ntfy_url`) sowie ein gültiger Access-Token (`ntfy_token`) eines Users mit schreibendem Zugriff auf dieses Thema zu hinterlegen.

Sofern die Variable `push_notifications` den Wert `True` besitzt, wird der Versand von Push-Benachrichtigungen über das Skript `cron.py` angestoßen.

Die Benachrichtigungen können über die mobilen ntfy-Apps ([Apple App Store](https://apps.apple.com/de/app/ntfy/id1625396347), [Google Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)) oder über kompatible Browser empfangen werden.

![Push-Benachrichtigungen (Beispiel)](docs/img/Push-Benachrichtigungen%20Beispiel.png "Push-Benachrichtigungen (Beispiel)")

**Hinweise:**

* Um Push-Benachrichtigungen im Browser auch dann anzuzeigen, wenn lediglich die Seiten des TI-Monitorings geöffnet sind, ist die Adresse der ntfy-Instanz (`ntfy_url`) als unsichtbares Iframe in den Footer integriert.

* Push-Benachrichtigungen beinhalten standardmäßig einen Action-Button, der zur Startseite der Web-App führt. Soll das TI-Monitoring ohne Web-App genutzt werden, kann in der Datei `myconfig.py` als `home_url` die Adresse einer öffentlichen TI-Monitoring-Instanz angegeben werden. Alternativ sollte der entsprechende Button aus der Funktion `send_push_notifications()` angepasst bzw. entfernt werden.

* Soll die Web-App ohne Push-Benachrichtigungen genutzt werden, ist die Datei `pages/alerts.py` obsolet. Außerdem sollten der entsprechende Link und das Iframe aus dem Footer (siehe `app.py`) entfernt werden.

## Web-App

Der aktuelle Status verschiedener Komponenten kann optional auch in Form einer Web-App auf Basis des [Dash-Frameworks](https://dash.plotly.com) bereitgestellt werden. Die App kann z. B. in Kombination mit uWSGI und nginx veröffentlicht werden.

Auf der Startseite der App werden die Komponenten nach Produkt gruppiert dargestellt. Durch Anklicken der Gruppen lassen sich die jeweiligen Komponenten einblenden.

![Mockup der App (Beispiel)](docs/img/TI-Monitoring%20Mockup.png "Mockup der App (Beispiel)")

![Screenshot aus der App: Startseite der App (Beispiel)](docs/img/App%20Home%20Beispiel.png "Startseite der App (Beispiel)")

![Screenshot aus der App: Startseite der App mit Störung (Beispiel)](docs/img/App%20Home%20Beispiel%20Störung.png "Startseite der App mit Störung (Beispiel)")

Per Klick auf die ID einer Komponente lässt sich eine Statistik der letzten Stunden beziehungsweise der aktuellen Woche aufrufen.

![Screenshot aus der App: Statistik für eine Komponente (Beispiel)](docs/img/App%20Statistik%20Beispiel.png "Statistik für eine Komponente (Beispiel)")

Um eine gute Performance zu gewährleisten, kann das Zeitfenster der Statistik über die Variable `stats_delta_hours` in der Datei `myconfig.py` reduziert werden. Zudem kann es ratsam sein, die Datei `data.hdf5` regelmäßig zu archivieren.

Soll die Web-App überhaupt nicht genutzt werden, sind folgende Ordner bzw. Dateien irrelevant und können entfernt werden:

* `assets`
* `pages`
* `app.py`

---

## Entwicklung mit Unterstützung durch KI

Bei der Weiterentwicklung dieses Projekts wurden teilweise KI-basierte Werkzeuge zur Unterstützung eingesetzt. Dies betrifft insbesondere die Unterstützung bei Programmierung, Refactoring, Fehlersuche, Dokumentation und Formulierung von Texten.

Die technische Verantwortung, Prüfung und Entscheidung über die Übernahme der vorgeschlagenen Änderungen verbleibt beim Projektautor.

---

## DISCLAIMER

Es handelt sich um ein privates Projekt ohne offiziellen Support. Jegliche Nutzung erfolgt auf eigene Verantwortung.

Die Daten werden über öffentlich erreichbare Schnittstellen der gematik GmbH abgerufen. Eine ausführliche Beschreibung der TI-Lage-Schnittstelle ist öffentlich auf GitHub verfügbar.