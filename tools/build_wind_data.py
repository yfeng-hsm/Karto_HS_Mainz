"""Create a fixed DWD teaching snapshot; requires pyshp for Natural Earth.
Downloads recent archives to a cache, keeps only the shared observation hour.
Usage: python tools/build_wind_data.py --cache /tmp/karto_wind
"""
from pathlib import Path
import argparse,csv,io,json,math,urllib.request,zipfile,concurrent.futures
import shapefile
p=argparse.ArgumentParser();p.add_argument('--cache',default='/tmp/karto_wind');p.add_argument('--timestamp',default='2026102812');args=p.parse_args()
cache=Path(args.cache);cache.mkdir(exist_ok=True,parents=True);out=Path(__file__).resolve().parents[1]/'docs/data';out.mkdir(exist_ok=True,parents=True)
base='https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/wind/recent/'
stations=json.loads((out/'wind_stations.json').read_text())
observations=[]
for s in stations:
 raw=cache/(s['id']+'.txt')
 if not raw.exists():
  z=zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(base+'stundenwerte_FF_'+s['id']+'_akt.zip',timeout=40).read()));raw.write_bytes(z.read(next(n for n in z.namelist() if n.startswith('produkt_ff_stunde'))))
 rows=({k.strip():v.strip() for k,v in r.items()} for r in csv.DictReader(raw.read_text().splitlines(),delimiter=';'))
 r=next((r for r in rows if r['MESS_DATUM']==args.timestamp),None)
 if not r:continue
 f,d=float(r['F']),float(r['D'])
 if f<=0 or not 0<d<=360:continue
 observations.append(dict(**s,speed=f,from_deg=d,to_deg=(d+180)%360,qn=int(r['QN_3']),level=sum(f>=x for x in [2,4,6]),source=base+'stundenwerte_FF_'+s['id']+'_akt.zip'))
assert len(observations)>=15,'Not enough valid observations; do not fabricate missing values.'
def geometry(key):
 dest=cache/(key+'10' if key=='states' else key);dest.mkdir(exist_ok=True)
 archive=cache/('states10.zip' if key=='states' else key+'.zip')
 if not archive.exists():
  url='https://naturalearth.s3.amazonaws.com/'+('10m_cultural/ne_10m_admin_1_states_provinces.zip' if key=='states' else '50m_physical/ne_50m_rivers_lake_centerlines.zip');archive.write_bytes(urllib.request.urlopen(url,timeout=60).read())
 if not list(dest.glob('*.shp')):zipfile.ZipFile(archive).extractall(dest)
 reader=shapefile.Reader(str(next(dest.glob('*.shp'))));fs=[]
 for sr in reader.iterShapeRecords():
  a=sr.record.as_dict()
  if not hasattr(sr.shape,'bbox'):continue
  b=sr.shape.bbox
  if key=='states' and a['iso_a2']!='DE':continue
  if b[0]>10.4 or b[2]<6.5 or b[1]>51.2 or b[3]<48.5:continue
  from shapely.geometry import shape,mapping
  geom=mapping(shape(sr.shape.__geo_interface__).simplify(.003,preserve_topology=True))
  fs.append({'type':'Feature','properties':{'name':a.get('name_de') or a.get('name','')},'geometry':geom})
 return {'type':'FeatureCollection','features':fs}
data=dict(timestamp=args.timestamp,display_time='28.10.2026 · 12:00 UTC / 13:00 MEZ',retrieved='2026-10-30',stations=observations,states=geometry('states'),rivers=geometry('rivers'),bbox=[6.6,48.85,10.15,51.0],cities=[dict(name=n,lon=x,lat=y) for n,x,y in [('Mainz',8.247,49.999),('Frankfurt',8.682,50.110),('Koblenz',7.588,50.357),('Mannheim',8.467,49.489)]],source=base,license='CC BY 4.0; © Deutscher Wetterdienst',classification=dict(bounds_m_s=[2,4,6],labels=['Stufe I','Stufe II','Stufe III','Stufe IV'],note='Didaktische Einteilung, keine amtlichen Warnstufen und keine Beaufort-Skala.'))
(out/'wind.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
with (out/'dwd_wind_snapshot.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['station_id','station_name','lat','lon','MESS_DATUM','F_m_s','D_from_deg','to_deg','QN_3']);writer.writeheader()
 for s in observations:writer.writerow(dict(station_id=s['id'],station_name=s['name'],lat=s['lat'],lon=s['lon'],MESS_DATUM=args.timestamp,F_m_s=s['speed'],D_from_deg=s['from_deg'],to_deg=s['to_deg'],QN_3=s['qn']))
locator=json.loads((out/'mainz.json').read_text());(out/'locator.json').write_text(json.dumps({k:locator[k] for k in ['germany','mainz']},separators=(',',':')))
print(len(observations),'observations;', (out/'wind.json').stat().st_size,'bytes')
