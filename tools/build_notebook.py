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
print("Bereit: 768 Einrichtungen, 1.012 Stadtflächen und 2.982 Bevölkerungszellen. Keine eigene Datenbeschaffung nötig.")
'''
nb={'nbformat':4,'nbformat_minor':5,'metadata':{'colab':{'name':'01_Visuelle_Variablen_und_Farbe.ipynb','toc_visible':True},'kernelspec':{'name':'python3','display_name':'Python 3'},'language_info':{'name':'python'}},'cells':[
md('''# Übung 01 · Von Daten zur Magazin-Karte
**Digitale Kartographie · Hochschule Mainz · Prof. Dr.-Ing. Yu Feng**

**45 Minuten · zwei Aufgaben · keine umfangreiche Programmierung**

Wir verwenden freie Python-Bibliotheken und reale Mainzer Daten. Sie gestalten durch Auswahlmenüs und Schieberegler: Karten sollen Informationen verständlich vermitteln und zugleich wie eine sorgfältig gestaltete Magazin-Grafik wirken.

**Start (ca. 5 Minuten):** Wählen Sie **Laufzeit → Alle ausführen**. Eine normale CPU-Laufzeit genügt. Warten Sie, bis beide Bedienfelder erscheinen; danach ändern Sie Einstellungen direkt unter den Aufgaben. Für größere Darstellungen können Sie die linke Colab-Seitenleiste schließen. Schieberegler aktualisieren nach dem Loslassen.

Daten und Darstellungscode sind eingebettet. Internet ist für die Erstinstallation nötig, nicht für das Nachladen einer kostenpflichtigen Hintergrundkarte. Alle Koordinaten und Größenberechnungen der Karte verwenden ETRS89/UTM32.
'''),code(setup,True),
md('''## Aufgabe 1 · Bertins sechs visuelle Variablen (ca. 20 Minuten)
**Thema: Einrichtungen und Stadtraum in Mainz.**

1. Lassen Sie zunächst die vier ausgewählten POI-Kategorien unverändert. Wählen Sie nacheinander **Größe, Helligkeit, Farbton, Form, Orientierung und Textur**. Verändern Sie jeweils mindestens eine Einstellung. Die passenden Regler erscheinen automatisch.
2. Achten Sie darauf, **welche Daten** dargestellt werden: Kategorien oder Zahlen? Größe und Helligkeit verwenden das gewählte Zahlenmerkmal. Farbton, Form und Symbolrichtung unterscheiden Einrichtungstypen. Texturen unterscheiden Stadtflächen.
3. Merken Sie eine Variante mit **„A merken“**, verändern Sie eine Einstellung und wählen Sie **„A/B vergleichen“**. Welche Variante lässt sich leichter lesen? Weshalb?
4. Probieren Sie **„Kombination“** aus. Werden zusätzliche Variablen hilfreich oder überladen sie die Karte? Entscheiden Sie sich für eine gut lesbare Darstellung.

**Diskussion:** Welche Variablen zeigen Unterschiede, welche eine Rangfolge und welche Mengen? Welche Zuordnungen passen nicht zur Aufgabe?

**Wichtig:** „POI im 500-m-Radius“ ist eine selbst berechnete Anzahl benachbarter Objekte dieser Auswahl, keine amtliche Versorgungskennzahl. Kartierte Fläche ist keine Kapazität. Die Symbolrichtung ist eine experimentelle Kategoriekodierung, keine reale Bewegungsrichtung. OSM-Daten sind unvollständig; Zugang und Trägerschaft sind nicht pauschal öffentlich.
'''),code('bertin = lab.bertin_lab()\n'),
md('''## Aufgabe 2 · Farben und Klassifikation (ca. 18 Minuten)
**Thema: Bevölkerung in Mainz, Zensus 2022.**

1. Vergleichen Sie **Equal Interval, Quantile und Jenks (Fisher-Jenks)** mit **5 Klassen und derselben Palette**. Nutzen Sie A/B. Betrachten Sie Karte, Legende und Histogramm: Welche Unterschiede werden betont oder verborgen?
2. Halten Sie nun die Klassifikation konstant. Vergleichen Sie eine **sequenzielle**, eine **divergierende** und eine **qualitative** Farbpalette. Welche passt zu positiven Bevölkerungszahlen? Hat eine divergierende Palette hier einen sinnvollen Bezugspunkt?
3. Verändern Sie die Klassenanzahl zwischen **3 und 7** und prüfen Sie die Karte in **Graustufen**. Achten Sie auf Reihenfolge und Unterscheidbarkeit.
4. Wählen Sie Ihre bevorzugte Kombination. Stimmen Sie Randlinien, Papierfarbe und Beschriftung ab. Exportieren Sie Ihre fertige Karte bei Bedarf als **SVG** oder **PNG**.

**Datenhinweis:** Personen je vollständiger 100 × 100-m-Zelle, Stichtag **15.05.2022**, keine aktuellen Einwohnerzahlen. Fehlende Zellen sind nicht mit Null gleichzusetzen. Die veröffentlichten Zahlen unterliegen dem amtlichen Geheimhaltungsverfahren. Bei gebundenen Werten können Quantile weniger als die gewünschte Klassenanzahl ergeben; die tatsächliche Zahl steht im Untertitel.
'''),code('farben = lab.color_lab()\n'),
md('''## Abschluss (ca. 2 Minuten)
Melden Sie sich per Handzeichen und zeigen Sie dem Dozenten Ihre bevorzugten Einstellungen aus beiden Aufgaben. Begründen Sie kurz Ihre Wahl der visuellen Variablen sowie von Farben und Klassifikation. **Keine Datei-Abgabe und kein selbst geschriebener Code erforderlich.**

### Quellen und offene Software
- Öffentliche Einrichtungen und Stadtflächen: **© OpenStreetMap contributors · ODbL**, regionaler BBBike-Extrakt, OSM-Stand **24.10.2026**; räumlicher Ausschnitt, Punktrepräsentation und Nachbarschaftszählung bearbeitet. [OSM-Lizenz](https://www.openstreetmap.org/copyright).
- Bevölkerung: **© Statistische Ämter des Bundes und der Länder, 2024 · Zensus 2022 · dl-de/by-2-0**. Vollständige Zellen mit Mittelpunkt innerhalb Mainz; kein amtlicher Stadtsummenwert. [Originaldaten](https://www.destatis.de/static/DE/zensus/gitterdaten/Zensus2022_Bevoelkerungszahl.zip).
- Mainz-Abgrenzung: BKG-abgeleitete Gemeindegrenzen, Stand 31.12.2025, über Esri Deutschland; nur für Auswahl und Orientierung, kein historischer Grenzstand von 2022.
- Software: GeoPandas, Matplotlib, mapclassify, ipywidgets. Darstellungscode dieses Repositories: MIT; Daten behalten ihre eigenen Lizenzen.

**Neustart oder leere Ausgabe?** Verbinden Sie die Laufzeit und führen Sie alle Zellen erneut aus. A wird im Arbeitsspeicher gehalten und geht beim Neustart verloren; exportierte Karten vorher herunterladen. Nach Änderungen am Paket müssen die eingebetteten Dateien mit `tools/build_notebook.py` neu gebaut werden.
''') ]}
for i, cell in enumerate(nb['cells']): cell['id'] = f'karto-01-{i:02d}'
(exercise/'01_Visuelle_Variablen_und_Farbe.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=1)+'\n')
print('Notebook written; embedded archive',len(mem.getvalue()),'bytes')
