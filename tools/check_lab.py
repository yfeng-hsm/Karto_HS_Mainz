"""Check the two fixed before/after blocks and the Germany locator."""
from pathlib import Path
import sys,json,ast,zipfile,base64,io,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'01_visual_variables_color'))
import cartography_lab as l
v=l.data()['pop'].population.to_numpy()
for method in ['Equal Interval','Quantile','Jenks (Fisher-Jenks)']:
 ids,bins=l.classify(v,method,5)
 assert len(ids)==2982 and np.all(np.diff(bins)>0) and np.all(v<=bins[ids])
assert len(l.classify(np.array([3]*40+[8]*20+[20]*20),'Quantile',7)[1])<=3
# Locator must be a Germany polygon and must actually contain Mainz.
from pyproj import Transformer
from shapely.geometry import Point
mx,my=Transformer.from_crs(4326,3035,always_xy=True).transform(8.2473,50.)
assert l.data()['germany'].geometry.iloc[0].contains(Point(mx,my))
for kind in ['bertin','color']:
 t=time.perf_counter();b=l.Lab(kind);print(kind,'initial block',round(time.perf_counter()-t,3),'s',flush=True)
 assert b.left.value==b.right.value and b.left.value
 assert len({id(c.layout) for c in b.controls.values()})==len(b.controls)
 before=b.left.value;shown=b.right.value
 key='size' if kind=='bertin' else 'k'
 b.controls[key].value=40 if kind=='bertin' else 4
 # Moving controls must not cause heavy rendering or mutate either image.
 assert b.left.value==before and b.right.value==shown
 assert b.applied[key] != b.values()[key]
 t=time.perf_counter();b.apply();print(kind,'right update',round(time.perf_counter()-t,3),'s',flush=True)
 assert b.left.value==before and b.right.value!=shown and b.applied==b.values()
 b.reset();assert b.left.value==b.right.value==before
 t=time.perf_counter();b.apply();assert time.perf_counter()-t<.2
 if kind=='bertin':
  for key in ['size','lightness','palette','form','angle','texture']:assert key in b.controls
  b.controls['texture'].value='Keine';b.controls['palette'].value='Vier Farbtöne';b.apply()
 else:b.controls['method'].value='Jenks (Fisher-Jenks)';b.apply()
 b.export('svg');assert '<svg' in (l.ROOT/f'results/Mainz_{kind}_Redesign.svg').read_text()
 assert all(c.layout.width=='50%' for c in b.ui.children[-1].children)
# Export reflects the right-hand figure actually shown, not un-applied edits.
nb=json.loads((r/'01_visual_variables_color/01_Visuelle_Variablen_und_Farbe.ipynb').read_text())
text=''.join(''.join(c['source']) for c in nb['cells'])
assert 'Version 3' in text and 'case_gallery(' not in text
for c in nb['cells']:
 if c['cell_type']=='code':ast.parse(''.join(c['source']))
for node in ast.walk(ast.parse(''.join(nb['cells'][1]['source']))):
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in node.targets):payload=ast.literal_eval(node.value)
z=zipfile.ZipFile(io.BytesIO(base64.b64decode(payload)))
for name in z.namelist():assert z.read(name)==(r/'01_visual_variables_color'/name).read_bytes()
assert 'data/germany.geojson' in z.namelist()
assert len(list(r.glob('0[2-4]*/README.md')))==3
print('PASS: two independent left/right blocks, deferred updates, fixed left styles, image cache, six controls, classification, Germany/Mainz locator and embedded notebook.')
