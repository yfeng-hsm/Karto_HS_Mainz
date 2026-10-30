# Kartographie · Hochschule Mainz

Interaktive Übungen für Digitale Kartographie, Prof. Dr.-Ing. Yu Feng.
Interaktive Webübungen mit offenen Bibliotheken. Ohne Anmeldung, Installation oder kostenpflichtige Karten-API.

| Übung | Thema | Stand |
|---|---|---|
| [01](01_visual_variables_color/) | Kartendesigns beurteilen und verbessern · Mainz | Zwei interaktive Webseiten, ca. 45 Minuten |
| [02](02_map_generalization/) | Map Generalization / Kartengeneralisierung | Ordner vorbereitet |
| [03](03_map_projection/) | Map Projection / Kartenprojektionen | Ordner vorbereitet |
| [04](04_3d_geovisualization/) | 3D-Geovisualisierung | Ordner vorbereitet |

## Übung 01: fünf Fälle im Browser

| Fall | Datentyp / Fokus | Datengrundlage |
|---|---|---|
| [1 · Nominal](https://yfeng-hsm.github.io/Karto_HS_Mainz/docs/bertin.html) | Einrichtungstypen ohne Rangfolge | Mainzer OSM-Einrichtungen |
| [2 · Ordinal](https://yfeng-hsm.github.io/Karto_HS_Mainz/docs/ordinal.html) | Reihenfolge von Stufen | Didaktische Windstufen aus DWD-Werten |
| [3 · Quantitativ](https://yfeng-hsm.github.io/Karto_HS_Mainz/docs/quantitativ.html) | Zahlen und Mengenvergleiche | DWD-Windgeschwindigkeit (m/s) |
| [4 · Richtung](https://yfeng-hsm.github.io/Karto_HS_Mainz/docs/richtung.html) | Orientierung und Richtungssinn | DWD-Windrichtung |
| [5 · Klassifikation und Farbe](https://yfeng-hsm.github.io/Karto_HS_Mainz/docs/farben.html) | Jenks, Quantile, Intervalle, Farbwahl | Mainzer Zensus-Bevölkerung 100 m |

Links bleibt die problematische Ausgangskarte unverändert. Rechts wird sie überarbeitet; die Bedienelemente stehen einspaltig ganz rechts. Fälle 1–3: zuerst eine von sechs Hauptvariablen wählen, dann deren Parameter einstellen. Nur passende Kombinationen sind optional verfügbar. Klassifikation und Farbpalettenvergleich sind auf Fall 5 konzentriert. SVG-/PNG-Export, keine Anmeldung erforderlich.

Die DWD-Daten stammen aus derselben Stunde: **28.10.2026, 12:00 UTC**. Es werden keine Messwerte erfunden und keine flächigen Windfelder interpoliert. Siehe [DWD-Quellen, Konventionen und Lizenz](docs/data/README_DWD.md).

[Übersicht öffnen](https://yfeng-hsm.github.io/Karto_HS_Mainz/docs/index.html). Lokal: `python -m http.server 8000 --directory docs`.

Das frühere [Colab-Notebook](01_visual_variables_color/01_Visuelle_Variablen_und_Farbe.ipynb) bleibt als optionale ältere Python-Version erhalten.

## Lizenzen und Quellen

Code: [MIT](LICENSE). Daten separat: © OpenStreetMap contributors (ODbL) und © Statistische Ämter des Bundes und der Länder, 2024, Zensus 2022 (DL-DE/BY-2.0). Siehe [Datenhinweise](01_visual_variables_color/data/). Bevölkerungsstichtag: 15.05.2022. OSM-Stand: 24.10.2026. Keine aktuellen amtlichen Einwohner- oder Einrichtungsverzeichnisse.

## Entwicklung

`python tools/build_notebook.py` aktualisiert den eingebetteten Code und die Daten nach Änderungen. `python tools/check_lab.py` prüft die Klassifikation, die Ausgangsentwürfe und die Widget-Aktionen ohne Colab-Anmeldung. Ein tatsächlicher angemeldeter Colab-Browserlauf ist zusätzlich zu prüfen.

## Vorschau: von der Diagnose zum Redesign

![Ausgangskarte und eine mögliche Überarbeitung](01_visual_variables_color/preview/Vorher_Nachher.png)

Die rechte Karte ist ein Gestaltungsbeispiel, keine einzig gültige Lösung. Im Notebook bleibt der linke Ausgangsentwurf unverändert; Studierende überarbeiten die rechte Karte.
