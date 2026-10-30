"""Build teaching snapshots from Destatis GV-ISys and OSM wheelchair tags.
Usage: python tools/build_city_access_data.py --gv /path/source.xlsx --osm /path/overpass.json
Requires openpyxl, pyproj and shapely. Data snapshots stay fixed after publication.
"""
from pathlib import Path
import argparse,json,csv,io
import openpyxl
from shapely.geometry import shape,Point
from pyproj import Transformer
p=argparse.ArgumentParser();p.add_argument('--gv',required=True);p.add_argument('--osm',required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];out=root/'docs/data'
source='https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/Archiv/GVAuszugQ/AuszugGV1QAktuell.xlsx?__blob=publicationFile'
want=['Mainz','Wiesbaden','Frankfurt am Main','Offenbach am Main','Darmstadt','Worms','Mannheim','Heidelberg','Koblenz','Trier','Bad Kreuznach','Bingen am Rhein','Ingelheim am Rhein','Rüsselsheim am Main','Hanau','Aschaffenburg','Ludwigshafen am Rhein','Neustadt an der Weinstraße','Speyer','Kaiserslautern']
w=openpyxl.load_workbook(io.BytesIO(Path(a.gv).read_bytes()),read_only=True,data_only=True);cities=[]
for row in w.worksheets[1].values:
 if row[0]!='60' or not row[7]:continue
 name=row[7].split(',')[0]
 if name not in want:continue
 cities.append(dict(id=''.join(str(row[i] or '') for i in range(2,7)),name=name,full_name=row[7],population=int(row[9]),lon=float(row[14].replace(',','.')),lat=float(row[15].replace(',','.')),reference_date='2024-12-31'))
assert len(cities)==len(want),set(want)-{p['name'] for p in cities}
cities.sort(key=lambda p:-p['population'])
(out/'cities.json').write_text(json.dumps(dict(display_time='Bevölkerung am 31.12.2024',source=source,geographic_reference='Gemeindemittelpunkte; Gebietsstand 31.03.2026',attribution='Statistische Ämter des Bundes und der Länder / Destatis, 2026',reuse='Weiterverbreitung mit Quellenangabe laut Tabellenblatt Inhalt gestattet.',cities=cities),ensure_ascii=False,separators=(',',':')))
with (out/'city_population.csv').open('w') as f:
 wr=csv.DictWriter(f,fieldnames=list(cities[0]));wr.writeheader();wr.writerows(cities)
features=json.loads((root/'01_visual_variables_color/data/boundary.geojson').read_text())['features'];border=shape(features[0]['geometry']);trans=Transformer.from_crs(4326,25832,always_xy=True);pois=[];wanted={'library','townhall','pharmacy','hospital','community_centre','theatre','cinema','post_office','bank','toilets'}
for e in json.loads(Path(a.osm).read_text())['elements']:
 tags=e['tags'];c=e if 'lat' in e else e.get('center',{});name=tags.get('name');wc=tags.get('wheelchair')
 if tags.get('amenity') not in wanted or not name or wc not in ['no','limited','yes'] or not c:continue
 lon,lat=c['lon'],c['lat']
 if not border.covers(Point(lon,lat)):continue
 x,y=trans.transform(lon,lat);pois.append(dict(id=f"{e['type']}/{e['id']}",name=name,x=round(x,1),y=round(y,1),lon=lon,lat=lat,access=wc,level=['no','limited','yes'].index(wc),amenity=tags['amenity'],source=f"https://www.openstreetmap.org/{e['type']}/{e['id']}"))
assert {p['access'] for p in pois}=={'yes','limited','no'}
(out/'accessibility.json').write_text(json.dumps(dict(retrieved='2026-10-30',source='OpenStreetMap / Overpass API',license='ODbL',categories=['nicht zugänglich','eingeschränkt','zugänglich'],pois=pois),ensure_ascii=False,separators=(',',':')))
wind=json.loads((out/'wind.json').read_text());region={k:wind[k] for k in ['states','rivers','bbox','cities']};region['bbox']=[6.3,48.95,10.05,50.8];(out/'region.json').write_text(json.dumps(region,ensure_ascii=False,separators=(',',':')))
print(len(cities),'cities;',len(pois),'places with wheelchair tags')
