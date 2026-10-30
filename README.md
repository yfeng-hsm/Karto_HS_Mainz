# Kartographie · Hochschule Mainz

Interaktive Übungen für Digitale Kartographie, Prof. Dr.-Ing. Yu Feng.
Freie Python-Bibliotheken, direkt in Google Colab. Keine bezahlten Karten-APIs erforderlich.

| Übung | Thema | Stand |
|---|---|---|
| [01](01_visual_variables_color/) | Bertins visuelle Variablen, Farben und Klassifikation · Mainz | Interaktives Notebook, ca. 45 Minuten |
| [02](02_map_generalization/) | Map Generalization / Kartengeneralisierung | Ordner vorbereitet |
| [03](03_map_projection/) | Map Projection / Kartenprojektionen | Ordner vorbereitet |
| [04](04_3d_geovisualization/) | 3D-Geovisualisierung | Ordner vorbereitet |

## Übung 01 starten

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yfeng-hsm/Karto_HS_Mainz/blob/main/01_visual_variables_color/01_Visuelle_Variablen_und_Farbe.ipynb)

**Laufzeit → Alle ausführen**, dann mit Menüs und Schiebereglern gestalten. Beide Aufgaben unterstützen A/B-Vergleiche sowie SVG-/PNG-Export. Umfangreiche Programmierung ist nicht erforderlich. Daten und Code sind im Notebook eingebettet; ein heruntergeladenes Notebook funktioniert auch nach Upload in Colab.

- **Aufgabe 1:** sechs visuelle Variablen an Einrichtungen und Stadtflächen untersuchen.
- **Aufgabe 2:** Farben, Klassenanzahl, Equal Interval, Quantile und Fisher-Jenks an 100-m-Bevölkerungszellen vergleichen.

Lesbarer Python-Code und Daten liegen zusätzlich neben dem Notebook. Lokal: `python -m pip install -r requirements.txt`. Öffnen Sie das Notebook in Jupyter mit Widget-Unterstützung.

## Lizenzen und Quellen

Code: [MIT](LICENSE). Daten separat: © OpenStreetMap contributors (ODbL) und © Statistische Ämter des Bundes und der Länder, 2024, Zensus 2022 (DL-DE/BY-2.0). Siehe [Datenhinweise](01_visual_variables_color/data/). Bevölkerungsstichtag: 15.05.2022. OSM-Stand: 24.10.2026. Keine aktuellen amtlichen Einwohner- oder Einrichtungsverzeichnisse.

## Entwicklung

`python tools/build_notebook.py` aktualisiert den eingebetteten Code und die Daten nach Änderungen. `python tools/check_lab.py` prüft die Klassifikation, alle sechs Variablen und die Widget-Aktionen ohne Colab-Anmeldung. Ein tatsächlicher angemeldeter Colab-Browserlauf ist zusätzlich zu prüfen.
