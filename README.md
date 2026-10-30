# Kartographie · Hochschule Mainz

Interaktive Übungen für Digitale Kartographie, Prof. Dr.-Ing. Yu Feng.

**[Übungen im Browser öffnen](https://yfeng-hsm.github.io/Karto_HS_Mainz/)**
Interaktive Webübungen mit offenen Bibliotheken. Ohne Anmeldung, Installation oder kostenpflichtige Karten-API.

| Übung | Thema | Stand |
|---|---|---|
| [01](01_visual_variables_color/) | Kartendesigns beurteilen und verbessern · Mainz | Fünf interaktive Fälle |
| [02](02_map_generalization/) | Map Generalization / Kartengeneralisierung | Ordner vorbereitet |
| [03](03_map_projection/) | Map Projection / Kartenprojektionen | Ordner vorbereitet |
| [04](04_3d_geovisualization/) | 3D-Geovisualisierung | Ordner vorbereitet |

## Übung 01: fünf Fälle im Browser

| Fall | Thema | Datengrundlage |
|---|---|---|
| [1 · Einrichtungen](https://yfeng-hsm.github.io/Karto_HS_Mainz/bertin.html) | Einrichtungstypen | Mainzer OSM-Einrichtungen |
| [2 · Rollstuhlzugang](https://yfeng-hsm.github.io/Karto_HS_Mainz/ordinal.html) | Zugangsangaben | 129 benannte Mainzer Orte mit OSM-wheelchair-Tags |
| [3 · Stadtbevölkerung](https://yfeng-hsm.github.io/Karto_HS_Mainz/quantitativ.html) | Städte vergleichen | 20 Städte, amtliche Einwohnerzahlen am 31.12.2024 |
| [4 · Wind](https://yfeng-hsm.github.io/Karto_HS_Mainz/richtung.html) | Strömungsrichtung | DWD-Windrichtung |
| [5 · Bevölkerungsraster](https://yfeng-hsm.github.io/Karto_HS_Mainz/farben.html) | Klassifikation und Farbe | Mainzer Zensus-Bevölkerung 100 m |

Links bleibt die Ausgangskarte unverändert. Rechts wird sie überarbeitet; die Bedienelemente stehen einspaltig ganz rechts. Zuerst die Informationsart selbst bestimmen, dann eine Hauptvariable und ihre Parameter wählen. Das Interface verrät keine Datenart und bewertet die Auswahl nicht automatisch. Die Orientierung wird mit einem asymmetrischen Pfeil dargestellt. Geeignete zusätzliche Kodierungen sind optional verfügbar und zeigen nach dem Aktivieren ihre eigene Parameterauswahl. Tonwerte lassen sich in Grau oder als einfarbige Blau-, Grün-, Orange- und Violettreihe darstellen und in ihrer Reihenfolge umkehren. Aufgaben erscheinen über das kleine Info-Symbol am Titel bei Hover, Tastaturfokus oder Antippen als kompakte schwebende Hinweise; die Kartenanordnung bleibt unverändert. Der Vergleich von Klassifikationen und Farbpaletten steht im Raster-Fall im Mittelpunkt.

[Quellen: Stadtbevölkerung und Rollstuhlzugang](docs/data/README_CITY_ACCESS.md). DWD wird ausschließlich im Wind-Fall verwendet: **28.10.2026, 12:00 UTC**; [Quellen und Konventionen](docs/data/README_DWD.md). Es werden keine Windfelder zwischen den Stationen interpoliert.

[Übersicht öffnen](https://yfeng-hsm.github.io/Karto_HS_Mainz/index.html). Lokal: `python -m http.server 8000 --directory docs`.

## Lizenzen und Quellen

Code: [MIT](LICENSE). Daten separat: © OpenStreetMap contributors (ODbL) und © Statistische Ämter des Bundes und der Länder, 2024, Zensus 2022 (DL-DE/BY-2.0). Siehe [Datenhinweise](01_visual_variables_color/data/). Bevölkerungsstichtag: 15.05.2022. OSM-Stand: 24.10.2026. Keine aktuellen amtlichen Einwohner- oder Einrichtungsverzeichnisse.

## Entwicklung

Die Website liegt in `docs/`; GitHub Pages veröffentlicht diesen Ordner als Hauptseite.

- Seiten erzeugen: `python tools/build_web_pages.py`
- Lokal ansehen: `python -m http.server 8000 --directory docs`
- Webinteraktionen prüfen: `NODE_PATH=/tmp/karto-test/node_modules node tools/check_web.mjs` (benötigt `jsdom`)
- Datenaufbereitung: `tools/build_web_data.py`, `tools/build_wind_data.py` und `tools/build_city_access_data.py`. Python-Abhängigkeiten stehen in `requirements.txt`.

Die Übungen laufen vollständig im Browser. Studierende benötigen keine Installation.
