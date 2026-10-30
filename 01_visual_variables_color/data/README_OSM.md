# Mainz: Öffentliche Einrichtungen und Stadtraum

Lehrdatensatz für Bertins visuelle Variablen. Reale OpenStreetMap-Daten; keine erfundenen Kapazitäten oder Kategorien. Abruf: 30.10.2026.

## GeoJSON
`facilities.geojson` enthält zwei Geometrietypen in einer FeatureCollection:
- `layer = poi`: Einrichtungen als Punkte. Flächig erfasste Einrichtungen wurden auf einen Punkt innerhalb ihrer Fläche reduziert.
- `layer = landuse`: Stadtflächen als Polygon/MultiPolygon.
In GeoPandas/Colab vor dem Zeichnen nach `layer` trennen.

## Felder
- `category`, `category_de`: OSM-Kategorie und deutsche Bezeichnung; nominale Attribute für Farbton und Form.
- `name`: Name, soweit in OSM vorhanden; fehlende Namen bleiben null.
- `nearby_poi_500m`: Zahl anderer in diesem Lehrdatensatz enthaltener POI im 500-m-Luftlinienradius; selbst berechnet, keine amtliche Versorgungskennzahl. Geeignet für Größen- und Helligkeitsexperimente; nicht alle Einrichtungen der Stadt sind vollständig erfasst.
- `area_m2`: POI: ursprüngliche kartierte Fläche, falls vorhanden; bei punktförmiger Quelle null. Stadtflächen: Fläche des ausgeschnittenen Polygons. Keine Besucherzahl oder Kapazität.
- `capacity`, `capacity_raw`: nur aus OSM übernommen, wenn vorhanden; unterschiedliche Einrichtungen können unterschiedliche Kapazitätseinheiten haben. Kein einheitlicher Größenindikator.
- `access`, `operator`: originale Angaben, falls vorhanden. Fehlende Angaben bedeuten nicht automatisch öffentlichen Zugang.
- `osm_type`, `osm_id`, `osm_url`, `tag_key`, `tag_value`: Herkunft und Rückverfolgung.
- `retrieved_on`, `source`: Abrufdatum und Quelle.

## Hinweise
Die Auswahl umfasst Einrichtungen von öffentlichem Interesse; private Trägerschaft oder eingeschränkter Zugang sind möglich. Kein amtliches oder vollständiges Verzeichnis, keine vollständige Landbedeckungskarte. OSM-Objekte können verschachtelt sein oder dieselbe reale Einrichtung mehrfach repräsentieren. Flächen können sich überlagern. Die Fläche einer Einrichtung ist nicht ihre Qualität oder Bedeutung.

Stadtflächen wurden an der Mainz-Abgrenzung ausgeschnitten. Auswahlgrenze: BKG-abgeleitete Gemeindegrenzen, Stand 31.12.2025, Esri Deutschland. EPSG:4326, Koordinatenfolge Länge/Breite; Fläche und Distanz in EPSG:25832 berechnet.

## Lizenz
© OpenStreetMap contributors. Open Database License (ODbL) 1.0.
https://www.openstreetmap.org/copyright
https://opendatacommons.org/licenses/odbl/1-0/
Bearbeitung: räumliche Auswahl, Kategorienbeschriftung, Flächenausschnitt, repräsentative Punkte und Nachbarschaftszählung. Bei Veröffentlichung der Daten ODbL-Bedingungen beachten; Attribution auf Karten beibehalten.

`metadata_osm.json` enthält Objektzahlen und Datenzeitstempel. Quelle: https://download.bbbike.org/osm/bbbike/Mainz/Mainz.osm.pbf (regionaler OSM-Extrakt von BBBike; siehe Zeitstempel in metadata.json). Der regionale BBBike-Download wurde verwendet, da der Online-Abfrage-Endpunkt beim Abruf nicht erreichbar war.

## Zusätzlicher Kartenkontext (Version 2)
`context.geojson`: Rhein/Main-Flächen und Hauptstraßen (primary, secondary, tertiary), aus demselben BBBike-PBF mit Stand 24.10.2026. Räumlich auf den Mainzer Umgebungsrahmen beschränkt. Ausschließlich zur Orientierung, keine vollständige Straßen- oder Gewässerkarte. © OpenStreetMap contributors · ODbL.

## Deutschland-Locator (Version 3)
`germany.geojson`: Deutschland aus Natural Earth 1:110 Mio., Public Domain. Quelle: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson ; Lizenz: https://www.naturalearthdata.com/about/terms-of-use/ . Nur zur Lokalisierung von Mainz, keine genaue Grenzkarte.
