"""Rebuild the self-contained Colab notebook from the readable module and data."""
from pathlib import Path
import json,io,zipfile,base64
r=Path(__file__).resolve().parents[1];exercise=r/'01_visual_variables_color'
mem=io.BytesIO()
with zipfile.ZipFile(mem,'w',zipfile.ZIP_DEFLATED) as z:
 for p in [exercise/'cartography_lab.py',*sorted((exercise/'data').iterdir())]:
  z.write(p,p.relative_to(exercise))
payload=base64.b64encode(mem.getvalue()).decode()
def md(s):return dict(cell_type='markdown',metadata={},source=s.splitlines(True))
def code(s,hidden=False):return dict(cell_type='code',metadata={'cellView':'form'} if hidden else {},execution_count=None,outputs=[],source=s.splitlines(True))
setup='''#@title 1. Installation und Daten vorbereiten – bitte ausführen
import sys, subprocess, importlib.util, pathlib, io, zipfile, base64, os
packages = {"geopandas": "geopandas>=1,<2", "matplotlib": "matplotlib>=3.8,<4", "ipywidgets": "ipywidgets>=8,<9", "mapclassify": "mapclassify>=2.8,<3"}
missing = [package for module, package in packages.items() if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *missing])
try:
    from google.colab import output
    output.enable_custom_widget_manager()
except ImportError:
    pass
work = pathlib.Path("/content/karto_lab_01") if pathlib.Path("/content").exists() else pathlib.Path.cwd()/"karto_lab_01"
work.mkdir(parents=True, exist_ok=True)
PAYLOAD = "'''+payload+'''"
with zipfile.ZipFile(io.BytesIO(base64.b64decode(PAYLOAD))) as archive:
    archive.extractall(work)
sys.path.insert(0, str(work))
import cartography_lab as lab
import importlib
importlib.reload(lab)
print("Bereit: 768 Einrichtungen, 1.012 Stadtflächen und 2.982 Bevölkerungszellen. Keine eigene Datenbeschaffung nötig.")
'''
nb={'nbformat':4,'nbformat_minor':5,'metadata':{'colab':{'name':'01_Visuelle_Variablen_und_Farbe.ipynb','toc_visible':True},'kernelspec':{'name':'python3','display_name':'Python 3'},'language_info':{'name':'python'}},'cells':[
md('''# Übung 01 · Eine Karte besser machen
**Digitale Kartographie · Hochschule Mainz · 45 Minuten**
**Version 3: Links analysieren → rechts verbessern → begründen**

Sie sind die Kartenredaktion eines Stadtmagazins. Sie bearbeiten zwei Beispiele in zwei getrennten Blöcken: eine Einrichtungen-Karte und eine Bevölkerungskarte. Links bleibt jeweils ein problematischer Entwurf sichtbar; rechts entwickeln Sie Ihre bessere Fassung mit denselben Daten.

**Ihre Aufgabe:** Benennen Sie je Beispiel zwei konkrete Probleme der linken Karte und gestalten Sie rechts eine besser lesbare Fassung. Es gibt keine einzige Musterlösung. Entscheidend ist, ob die Gestaltung zur Leserfrage passt.

**Start (5 Min.):** **Laufzeit → Alle ausführen.** Danach arbeiten Sie nur mit Menüs, Reglern und Schaltflächen. Kein eigener Code nötig, normale CPU-Laufzeit genügt. Stellen Sie die Regler ein und klicken Sie **„Rechte Karte aktualisieren“**. Nur die rechte Karte wird neu gezeichnet. Das vermeidet Verzögerungen beim Schieben. Beim Wechsel zu dieser Version bitte die Ausgaben erneut ausführen.
'''),code(setup,True),
md('''## 1 · Vier Einrichtungstypen verständlich zeigen (20 Min.)
**Leserfrage:** Wo befinden sich Schulen, Kitas, Bibliotheken und Sportzentren? Lassen sich die vier Typen schnell unterscheiden?

**A · Zuerst diskutieren:** Betrachten Sie die feste Ausgangskarte links. Welche Informationen fallen zuerst auf? Wo lassen sich Typen schwer unterscheiden? Erwecken Zeichen eine Rangfolge, die gar nicht in den Daten steht?

**B · Dann überarbeiten:** Verändern Sie mit den Reglern die rechte Karte und wenden Sie die Änderungen mit **„Rechte Karte aktualisieren“** an. Die sechs Gruppen entsprechen **Größe, Helligkeit, Farbton, Form, Orientierung und Textur**. Testen Sie jede Gruppe kurz; behalten Sie am Ende nur hilfreiche Unterschiede. Denken Sie auch an den Kontrast zwischen Thema und Hintergrund.

**C · Begründen:** Vergleichen Sie die beiden Karten direkt nebeneinander. Nennen Sie drei Änderungen und erklären Sie jeweils den Nutzen für die Leserin oder den Leser.

**Datenlogik:** Alle vier Einrichtungstypen sind **nominale Kategorien**. Unterschiedliche Größen und Helligkeiten kodieren hier versuchsweise nur den Typ – weder Kapazität noch Qualität. Die Drehung ist keine reale Bewegungsrichtung. Die Texturen unterscheiden reale Stadtflächen; sie müssen nicht in der endgültigen Karte bleiben. An Kreisen ist eine Drehung unsichtbar – testen Sie Dreiecke.
'''),code('''#@title Block 1 öffnen: links Ausgangskarte, rechts Ihre Überarbeitung
bertin = lab.bertin_lab()
''',True),
md('''## 2 · Bevölkerungszahlen klar vermitteln (18 Min.)
**Leserfrage:** Wo konzentriert sich die Wohnbevölkerung in Mainz?

**A · Zuerst diskutieren:** Untersuchen Sie die linke Ausgangskarte. Welche Karte vermittelt eine erkennbare Reihenfolge? Welche verschluckt Unterschiede? Betrachten Sie auch die Legende und die Werteverteilung.

**B · Dann überarbeiten:** Verbessern Sie die rechte Karte. Wenden Sie Ihre Einstellungen jeweils mit **„Rechte Karte aktualisieren“** an:
- Vergleichen Sie **Equal Interval, Quantile und Jenks (Fisher-Jenks)** bei **gleicher Palette und gleicher Klassenanzahl**.
- Halten Sie anschließend die Klassifikation fest und ändern Sie **Palette und Farbkontrast**. Begründen Sie, ob sequenzielle, divergierende oder qualitative Farben passen.
- Prüfen Sie **3–7 Klassen**, **Graustufen** und die Stärke der Randlinien. Wählen Sie eine lesbare Fassung für das Stadtmagazin.

**C · Begründen:** Vergleichen Sie links und rechts und erklären Sie Ihre Entscheidung für Klassifikation und Farben. Die angezeigte effektive Klassenanzahl kann bei gebundenen Werten von der Auswahl abweichen.

**Datenlogik:** Zensus 2022, **15.05.2022**, Personen je vollständiger **100 × 100-m-Zelle**. Fehlende Zellen sind keine gesicherten Nullwerte. Die Zahlen unterliegen dem amtlichen Geheimhaltungsverfahren. Dies ist kein aktuelles Melderegister.
'''),code('''#@title Block 2 öffnen: links Ausgangskarte, rechts Ihre Überarbeitung
farben = lab.color_lab()
''',True),
md('''## Abschluss (2 Min.)
Melden Sie sich per Handzeichen. Zeigen Sie dem Dozenten in beiden Aufgaben **Ausgangskarte und Überarbeitung**. Begründen Sie drei Gestaltungsentscheidungen und nennen Sie einen verbleibenden Nachteil. **Keine Datei-Abgabe erforderlich.** SVG-/PNG-Export ist freiwillig.

### Quellen und Software
- **© OpenStreetMap contributors · ODbL**, OSM-Stand 24.10.2026, BBBike-Regionalextrakt. Einrichtungen, Stadtflächen, Rhein/Main und Hauptstraßen; räumlich ausgewählt und bearbeitet. Keine vollständige Bestandsliste, Zugang nicht geprüft. [Lizenz](https://www.openstreetmap.org/copyright).
- **© Statistische Ämter des Bundes und der Länder, 2024 · Zensus 2022 · dl-de/by-2-0**. 2.982 veröffentlichte Zellen nach Mittelpunkt innerhalb Mainz; kein amtlicher Stadtsummenwert. [Originaldaten](https://www.destatis.de/static/DE/zensus/gitterdaten/Zensus2022_Bevoelkerungszahl.zip).
- Mainz-Abgrenzung: BKG-abgeleitete Gemeindegrenzen, Stand 31.12.2025, über Esri Deutschland; Auswahl und Orientierung, kein historischer Grenzstand von 2022.
- Deutschland-Übersicht: Natural Earth 1:110 Mio., Public Domain. Die Markierung zeigt die Lage von Mainz in Deutschland. [Quelle und Lizenz](https://www.naturalearthdata.com/about/terms-of-use/).
- Freie Software: GeoPandas, Matplotlib, mapclassify und ipywidgets. Darstellungscode MIT; Daten behalten ihre eigenen Lizenzen. Keine bezahlte Karten-API.

Daten und Code sind eingebettet. Nach einem Laufzeit-Neustart alle Zellen erneut ausführen. Exportierte Dateien vor dem Beenden herunterladen.
''') ]}
for i,cell in enumerate(nb['cells']):cell['id']=f'karto-01-{i:02d}'
(exercise/'01_Visuelle_Variablen_und_Farbe.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=1)+'\n')
print('Guided critique notebook built; embedded archive',len(mem.getvalue()),'bytes')
