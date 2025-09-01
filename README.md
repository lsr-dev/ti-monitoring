# TI-Monitoring

Dieses Tool dient der Überwachung verschiedener Komponenten der Telematikinfrastruktur (TI).
Es ist modular aufgebaut, sodass sich je nach Bedarf und Systemleistung auch nur einzelne Funktionen nutzen lassen.

Die Funktionen lassen sich wie folgt zusammenfassen:

* __Abruf und Archivierung__<br>
Die Kernfunktionalität besteht in der regelmäßigen Abfrage des Verfügbarkeitsstatus sämtlicher zentraler TI-Komponenten über eine öffentliche Schnittstelle der gematik GmbH. Die Ergebnisse werden strukturiert in einer hdf5-Datei gespeichert. So können auch für längere Beobachtungszeiträume statistische Auswertungen durchgeführt werden, um beispielsweise die Einhaltung von SLAs zu beurteilen.
* __Benachrichtigungen__<br>
Bei Änderungen der Verfügbarkeit können Benachrichtigungen per E-Mail und/oder Push-Benachrichtigung versendet werden. Zur Filterung der TI-Komponenten kann wahlweise eine White- oder Blacklist definiert werden.
* __Web-App__<br>
Der aktuelle Status sämtlicher TI-Komponenten lässt sich nach Produkten gruppiert in einer interaktiven Web-App einsehen. Darüber hinaus kann für die einzelnen Komponenten eine Statistik der letzten Stunden aufgerufen werden.

## Einrichtung der Python-Umgebung
Das Tool kann beispielweise auf einem (virtuellen) Server, NAS oder (idealerweise permanent laufenden) Rechner installiert werden. Systemanforderungen und Einrichtungsaufwand variieren je nach Umfang der genutzten Funktionen. Für die 
Grundfunktionalität (Abruf und Archivierung von Verfügbarkeitsinformationen) sind lediglich die Pakete erforderlich, die in der Datei `mylibrary.py` importiert werden. Nur im Falle der App sind weitere Pakete (z.B. `dash`) zu installieren sowie ein Webserver (z.B. nginx) und ggf. ein Applikationsserver (z.B. uWSGi). Weitere Details zur Funktionsweise und Konfiguration finden sich weiter unten. Allgemein empfiehlt sich die Erstellung einer virtuellen Python-Umgebung. Dies geschieht beispielsweise unter Ubuntu 24.04 LTS mit dem User `lukas` wie folgt:

```
sudo apt update && sudo apt upgrade
sudo apt install python3-venv
python3 -m venv /home/lukas/myenv
source /home/lukas/myenv/bin/activate
```
Die erforderlichen Pakete (z.B. `h5py`) können daraufhin mit dem Befehl `pip3 install <module>` installiert werden, z.B. `pip3 install h5py`.

## Abruf und Archivierung
Abruf und Archivierung erfolgen durch das Skript `cron.py`, das alle fünf Minuten durch einen Cronjob ausgeführt werden sollte. Um möglichst die aktuellsten Daten abzugreifen,  empfiehlt sich ein minimaler Versatz zum Bereitstellungszeitpunkt der Daten:
```
# m h  dom mon dow   command
2-59/5 * * * * /bin/bash -c 'source myenv/bin/activate && python cron.py'
```
Die Daten werden aufbereitet und in der Datei `data.hdf5` gespeichert. Existiert diese noch nicht, wird sie beim ersten Ausführen des Skriptes `cron.py` automatisch erzeugt.

Innerhalb der Datei wird folgende Gruppenstruktur aufgebaut:

```
.
+-- availability
|   +-- CI-0000001
|   +-- CI-0000002
|   +-- ...
+-- configuration_items
    +-- CI-0000001
    +-- CI-0000002
    +-- ...
```

Die Gruppen `availability` und `configuration_items` enthalten jeweils für jedes Konfigurationsobjekt (z.B. `CI-0000001`) eine gleichnamige Untergruppe.

Die Untergruppe des Konfigurationsobjektes in der Gruppe `availability` enthält Datensätze mit der Verfügbarkeit als Integer (0: nicht verfügbar, 1: verfügbar). Der Name des Datensatzes entspricht der Unix-Zeit des Datenpunktes. Bei Aktualisierungen wird ein neuer Datensatz hinzugefügt.

Die Untergruppe des Konfigurationsobjektes in der Gruppe `configuration_items` enthält mehrere Datensätze mit allegemeinen Eigenschaften wie `name`, `product` und `organization`. Außerdem die aktuelle Verfügbarkeit `current_availability` sowie die Veränderung der Verfügbarkeit `availability_difference` in Bezug auf den vorherigen Wert (-1: nicht mehr verfügbar, 0: keine Veränderung, 1: wieder verfügbar). Bei Aktualisierungen werden die vorhandenen Datensätze überschrieben.

Je nach Systemleistung kann es sinnvoll sein, die Datei `data.hdf5` von Zeit zu Zeit archivieren. Hierzu kann die Datei beispielsweise per Cronjob in ein Archiv-Verzeichnis verschoben werden.

## Benachrichtigungen

### E-Mail
Auf Wunsch können bei Änderungen der Verfügbarkeit Benachrichtigungen per E-Mail versendet werden. Dies geschieht ebenfalls über das Skrip `cron.py`, sofern in der Datei `myconfig.py` die Variable `notifications` den Wert `True` besitzt. Die SMTP-Verbindungsdaten werden ebenfalls in der Datei `myconfig.py` hinterlegt.

In der Datei `notifications.json` können mehrere Profile definiert werden. Ein Profil besteht aus folgenden Eigenschaften:

| Name | Beschreibung |
| ----------- | ----------- |
| name | Name des Profils (wird in der Anrede verwendet) |
| recipients | Liste mit mindestens einer E-Mail-Adresse (z.B. `["mail1@example.com", "mail2@example.com"]`) |
| ci_list | Liste von Konfigurationsobjekten (z.B. `["CI-000001", "CI-0000002"]`) |
| type | entweder `blacklist` oder `whitelist` (legt fest, wie die Liste der Konfigurationsobjekte behandelt wird) |
| push_topic | Thema für Push-Benachrichtigungen via ntfy (z.B. `TI`)|  

Hier ein Beispiel für eine E-Mail-Benachrichtigung:
![E-Mail-Benachrichtigung über Störung (Beispiel)](docs/img/Mail%20Beispiel%20Störung.png "E-Mail-Benachrichtigung über Störung (Beispiel)")

### Push-Benachrichtigungen voa ntfy
Sofern eine [ntfy](https://github.com/binwiederhier/ntfy)-Instanz vorhanden ist, lassen sich optional Push-Benachrichtigungen versenden. Hierfür muss im Benachrichtigungsprofil ein Thema (`push_topic`) angegeben werden. Zudem sind in der Datei `myconfig.py` die URL zur ntfy-Instanz (`ntfy_url`) sowie ein gültiger Access-Token (`ntfy_token`) eines Users mit schreibenden Zugriff auf dieses Thema zu hinterlegen. Sofern die Variable `push_notifications` den Wert `True` besitzt, wird der Versand von Push-Benachrichtigungen über das Skrip `cron.py` angestoßen. Die Benachrichtigungen können über die mobilen ntfy-Apps ([Apple App Store](https://apps.apple.com/de/app/ntfy/id1625396347), [Google Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy)) oder über kompatible Browser ausgespielt werden.

**Hinweise:**

* Um Push-Benachrichtigungen im Browser auch dann anzuzeigen, wenn lediglich die Seiten des TI-Monitorings geöffnet sind, ist die Adresse der ntfy-Instanz (`ntfy_url`) als unsichtbares Iframe in den Footer integriert.

* Push-Benachrichtigungen beinhalten standardmäßig einen Action-Button, der zur Startseite der Web-App führt. Soll das TI-Monitoring ohne Web-App genutzt werden, kann in der Datei `myconfig.py` als `home_url` die Adresse einer öffentlichen TI-Monitoring-Instanz angegeben werden. Alternativ sollte der entsprechende Button aus der Funktion `send_push_notifications()` angepasst bzw. entfernt werden.

* Soll die Web-App ohne Push-Benachrichtigungen genutzt werden, ist die Datei `pages/alerts.py` obsolet. Außerdem sollten der entsprechende Link und das Iframe aus dem Footer (siehe `app.py`) entfernt werden.

## Web-App

Der aktuelle Status verschiedener Komponenten kann optional auch in Form einer Web-App auf Basis des [Dash-Frameworks](https://dash.plotly.com) bereitgestellt werden. Die App kann z.B. in Kombination mit uWSGi und nginx (ähnlich [wie hier beschrieben](https://carpiero.medium.com/host-a-dashboard-using-python-dash-and-linux-in-your-own-linux-server-85d891e960bc) veröffentlicht werden.

Auf der Startseite der App werden die Komponenten nach Produkt gruppiert dargestellt. Durch Anklicken der Gruppen lassen sich die jeweiligen Komponenten einblenden.
![Screenshot aus der App: Startseite der App (Beispiel)](docs/img/App%20Home%20Beispiel.png "Startseite der App (Beispiel)")
![Screenshot aus der App: Startseite der App mit Störung (Beispiel)](docs/img/App%20Home%20Beispiel%20Störung.png "Startseite der App mit Störung (Beispiel)")
Per Klick auf die ID einer Komponente lässt sich eine Statistik der letzten Stunden aufrufen.
![Screenshot aus der App: Statistik für eine Komponente (Beispiel)](docs/img/App%20Statistik%20Beispiel.png "Statistik für eine Komponente (Beispiel)")
Um eine gute Performance zu gewährleisten, kann das Zeitfenster der Statistik über die Variable `stats_delta_hours` in der Datei `myconfig.py` reduziert werden. Zudem kann es ratsam sein, die Datei `data.hdf5` regelmäßig zu archivieren bzw. zu leeren.

Soll die Web-App überhaupt nicht genutzt werden, sind folgende Ordner bzw. Dateien irrelevant und können entfernt werden:

* assets
* pages
* app.py

---
**DISCLAIMER**

Es handelt sich um ein privates Projekt ohne offiziellen Support. Jegliche Nutzung erfolgt auf eigene Verantwortung. 

Die Daten werden über eine öffentlich erreichbare Schnittstelle der gematik GmbH abgerufen. Eine ausführliche Beschreibung diser Schnittstelle ist öffentlich auf GitHub verfügbar: [https://github.com/gematik/api-tilage](https://github.com/gematik/api-tilage).

---