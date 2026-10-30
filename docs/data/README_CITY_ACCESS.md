# Stadtbevölkerung und Rollstuhlzugang

## Stadtbevölkerung

20 ausgewählte Städte im weiteren Mainzer Umfeld. Einwohnerzahl: **31.12.2024**, auf Grundlage des Zensus 2022. Gebietsstand: **31.03.2026**. Die Übersicht verwendet Gemeindemittelpunkte; die Zahlen betreffen das gesamte Gemeindegebiet, keine Ballungsräume.

Quelle: Statistische Ämter des Bundes und der Länder / Statistisches Bundesamt (Destatis), 2026, GV-ISys, *Gemeinden in Deutschland nach Fläche, Bevölkerung und Postleitzahl am 31.03.2026*. Im Tabellenblatt sind die Bevölkerungszahlen ausdrücklich mit 31.12.2024 beschriftet.

- [Originaldatei XLSX](https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/Archiv/GVAuszugQ/AuszugGV1QAktuell.xlsx?__blob=publicationFile)
- [Gemeindeverzeichnis](https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/_inhalt.html)
- Abruf: 30.10.2026. Die Originaldatei kann später aktualisiert werden; `cities.json` und `city_population.csv` bewahren den verwendeten Snapshot.
- Laut Tabellenblatt „Inhalt“ ist die Weiterverbreitung mit Quellenangabe gestattet. Quellenangabe ist auf der Karte und in den Datenhinweisen enthalten.

Das Skript `tools/build_city_access_data.py` wählt die Gemeinden anhand ihrer Namen aus den Gemeindezeilen (Satzart 60), übernimmt die Originalzahlen und Koordinaten und prüft die Anzahl der Gemeinden. Es schätzt keine Bevölkerung.

## Rollstuhlzugang

Quelle: © OpenStreetMap contributors, ODbL, abgerufen am 30.10.2026 über die Overpass API. Snapshot: `accessibility.json`.

Abfrage: Elemente mit `amenity` und `wheelchair=yes|limited|no` in der Bounding Box 49.88,8.16,50.06,8.36. Anschließend Auswahl benannter Apotheken, Bibliotheken, Rathäuser, Banken, Poststellen, Toiletten, Krankenhäuser, Gemeinschaftszentren, Theater und Kinos innerhalb der Mainzer Gemeindegrenze. Es verbleiben 129 Einträge. ID, Name, Kategorie, Original-Zugangscode und OSM-Quelllink bleiben erhalten. Die Karte verwendet denselben Innenstadt-Ausschnitt wie der Einrichtungen-Fall; Orte außerhalb des Kartenausschnitts bleiben in der Datentabelle.

Legende: `no` → nicht zugänglich; `limited` → eingeschränkt; `yes` → zugänglich. Die Begriffe beziehen sich ausschließlich auf den gemeldeten Rollstuhlzugang. Fehlende Angaben werden ausgeschlossen, nicht als `no` interpretiert. Die Angaben sind Community-Daten und beschreiben nicht sämtliche Aspekte von Barrierefreiheit.

Die Lernenden sollen die Informationsart selbst bestimmen. Es gibt keine automatische Eignungsbewertung oder Musterlösung im Interface.

## Hintergrund

Mainz: mitgelieferter OSM-Hintergrund. Regionale Karte: Natural Earth (Public Domain), Bundesländer und Flüsse; siehe `README_DWD.md` für die Geometriequellen. Die regionale Geometrie enthält keine neu geschätzten Messwerte.
