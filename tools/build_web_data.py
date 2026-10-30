"""Export compact planar drawing data for the static SVG labs.
Coordinates are ETRS89/UTM32 (Germany locator: ETRS89/LAEA), not RFC7946 GeoJSON.
Original WGS84 GeoJSON data and source notices remain in the exercise folder.
"""
from pathlib import Path
import json
import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import mapping
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'01_visual_variables_color/data'
fac=gpd.read_file(source/'facilities.geojson').to_crs(25832)
context=gpd.read_file(source/'context.geojson').to_crs(25832)
bound=gpd.read_file(source/'boundary.geojson').to_crs(25832)
pop=gpd.read_file(source/'population.geojson').to_crs(25832)
germany=gpd.read_file(source/'germany.geojson').to_crs(3035)
categories=['Schule','Kindertagesstätte','Bibliothek','Sportzentrum']
def rounded(value):
 if isinstance(value,(tuple,list)):return [rounded(x) for x in value]
 if isinstance(value,float):return round(value,1)
 return value
def geom(g):
 m=mapping(g);return {'type':m['type'],'coordinates':rounded(m['coordinates'])}
labels=[]
t=Transformer.from_crs(4326,25832,always_xy=True)
for name,lon,lat in [('NEUSTADT',8.257,50.010),('ALTSTADT',8.276,49.998),('GONSENHEIM',8.208,50.005),('HECHTSHEIM',8.273,49.968)]:
 x,y=t.transform(lon,lat);labels.append({'name':name,'x':round(x,1),'y':round(y,1)})
poi=[]
for _,r in fac[(fac.layer=='poi')&fac.category_de.isin(categories)].iterrows():
 poi.append({'x':round(r.geometry.x,1),'y':round(r.geometry.y,1),'category':categories.index(r.category_de),'name':r['name'] if isinstance(r['name'],str) else '', 'id':f'{r.osm_type}/{r.osm_id}'})
land=[]
for cat,group in fac[fac.layer=='landuse'].groupby('category_de'):
 from shapely.ops import unary_union
 # Keep separate outlines in one collection, simplifying only background context.
 land.append({'category':cat,'geometry':{'type':'GeometryCollection','geometries':[geom(g.simplify(2,preserve_topology=True)) for g in group.geometry]}})
def collection(gdf):return {'type':'GeometryCollection','geometries':[geom(g.simplify(2,preserve_topology=True)) for g in gdf.geometry]}
a,b,c,d=bound.total_bounds
point=Transformer.from_crs(4326,3035,always_xy=True).transform(8.2473,50.0)
obj={'version':1,'drawing_crs':'EPSG:25832','locator_crs':'EPSG:3035',
     'views':{'bertin':[444800,449700,5535700,5540600],'color':[round(a-350,1),round(c+350,1),round(b-350,1),round(d+350,1)]},
     'boundary':collection(bound),'roads':collection(context[context.layer=='road']),
     'water':collection(context[context.layer=='water']),'land':land,'pois':poi,
     'population':[{'geometry':geom(r.geometry),'value':int(r.population),'id':r.grid_id} for _,r in pop.iterrows()],
     'labels':labels,'germany':geom(germany.geometry.iloc[0]),'mainz':rounded(point)}
# GeometryCollection must be handled recursively by the geometry converter above.
p=ROOT/'docs/data/mainz.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')))
print('Web data:',p.stat().st_size,'bytes;',len(poi),'POI;',len(pop),'population cells')
