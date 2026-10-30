# Mainz · Bevölkerung im 100-m-Gitter

Zensus 2022, Stichtag **15.05.2022**. 2,982 veröffentlichte Gitterzellen.

## Dateien und Nutzung
- `population.geojson`: vollständige 100 × 100 m Gitterzellen; für Flächenkarten. In kepler.gl die GeoJSON-Flächenebene verwenden und `population` als Farbmerkmal wählen.
- `metadata_population.json`: Quellen, Auswahlregel, Felder und Prüfsummen.

Die GeoJSON-Datei verwendet WGS84 (EPSG:4326). GeoJSON-Koordinaten: Länge, Breite. Die Quadrate wurden in EPSG:3035 rekonstruiert und anschließend transformiert.

## Auswahl und Grenzen
Ausgewählt wurden nur veröffentlichte Zellen, deren Mittelpunkt innerhalb der Stadtgrenze Mainz liegt (AGS 07315000). Die vollständigen Zellen wurden beibehalten; Randzellen können über die Grenze hinausragen. Keine anteilige Bevölkerungsverteilung und keine Ergänzung fehlender Zellen mit Null. Die Abgrenzung basiert auf BKG-abgeleiteten Gemeindegrenzen, Stand 31.12.2025, über den Esri-Deutschland-Dienst; sie ist kein historischer Grenzstand von 2022.

Die Bevölkerung wurde durch das amtliche Geheimhaltungsverfahren (Cell-Key-Methode) geringfügig verändert veröffentlicht. Fehlende Zellen bedeuten nicht zwingend einen exakt bekannten Nullwert. Die Summe dieses Ausschnitts ist keine amtliche Einwohnerzahl von Mainz. Dies sind historische Daten von 2022, keine aktuellen Melderegisterzahlen.

## Quelle und Lizenz
© Statistische Ämter des Bundes und der Länder, 2024 · Zensus 2022 · Datenlizenz Deutschland – Namensnennung – Version 2.0 (dl-de/by-2-0). Bearbeitung: räumlicher Ausschnitt, Feldnamen, Koordinatentransformation und abgeleitete Dichte.

Original: https://www.destatis.de/static/DE/zensus/gitterdaten/Zensus2022_Bevoelkerungszahl.zip
Lizenz: https://www.govdata.de/dl-de/by-2-0
Grenzdienst: https://services2.arcgis.com/jUpNdisbWqRpMo35/ArcGIS/rest/services/Gemeindegrenzen_2026/FeatureServer/1
Abruf: 30.10.2026
