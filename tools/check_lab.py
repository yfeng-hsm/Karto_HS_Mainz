"""Regression checks for the guided critique/redesign lesson."""
from pathlib import Path
import sys,ast,json,zipfile,base64,io
import numpy as np
import matplotlib
matplotlib.use('Agg')
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'01_visual_variables_color'))
import cartography_lab as l

# Published counts and classification boundaries retain the actual values.
d=l.data();assert len(d['pop'])==2982 and len(d['poi'])==266
v=d['pop'].population.to_numpy()
for method in ['Equal Interval','Quantile','Jenks (Fisher-Jenks)']:
 ids,bins=l.classify(v,method,5)
 assert len(ids)==2982 and np.all(np.diff(bins)>0) and np.all(v<=bins[ids])
 assert ids.min()==0 and ids.max()==len(bins)-1
ids,bins=l.classify(np.array([3]*40+[8]*20+[20]*20),'Quantile',7)
assert len(bins)<=3

# Each deliberately problematic starting point renders without changing data.
for fn,cases in [(l.bertin_map,l.BERTIN_CASES),(l.color_map,l.COLOR_CASES)]:
 for p in cases.values():
  f=fn(p);f.canvas.draw();l.plt.close(f)
assert l.category_style(l.BERTIN_CASES['Karte C'],0)[1]>l.category_style(l.BERTIN_CASES['Karte C'],3)[1]
assert all(l.category_style(l.BERTIN_BASE,i)[1]==l.BERTIN_BASE['size'] for i in range(4))
assert len({l.category_style(l.BERTIN_CASES['Karte B'],i)[0] for i in range(4)})==1
# All six visual variables are exposed; changing a slider modifies current settings,
# but cannot mutate the saved starting map. Independent layouts avoid hidden controls.
b=l.Lab('bertin')
assert len({id(c.layout) for c in b.controls.values()})==len(b.controls)
for key in ['size','lightness','palette','form','angle','texture']:
 assert key in b.controls and b.controls[key].layout.display!='none'
initial=b.original.copy();b.controls['size'].value=40
assert b.original==initial and b.values()['size']==40
b.compare();assert 'Vorher' in b.map.value and 'Nachher' in b.map.value
b.case.value='Karte B';b.load_case();assert b.values()==l.BERTIN_CASES['Karte B']
b.controls['size'].value=80;b.reset();assert b.values()==l.BERTIN_CASES['Karte B']
b.export('svg');assert '<svg' in (l.ROOT/'results/Mainz_bertin_Redesign.svg').read_text()
# Same controller pattern for colours, with a stable before state.
c=l.Lab('color');original=c.original.copy();c.controls['contrast'].value=.4
assert c.original==original and c.values()['contrast']==.4
c.case.value='Karte C';c.load_case();assert c.values()==l.COLOR_CASES['Karte C']
c.controls['gray'].value=True;c.compare();assert 'Vorher' in c.map.value
assert not any('Eine Variable nach der anderen' in str(getattr(w,'value','')) for w in b.ui.children)
# Notebook setup really contains the current code and every data file.
nb=json.loads((r/'01_visual_variables_color/01_Visuelle_Variablen_und_Farbe.ipynb').read_text())
for cell in nb['cells']:
 if cell['cell_type']=='code':ast.parse(''.join(cell['source']))
for node in ast.walk(ast.parse(''.join(nb['cells'][1]['source']))):
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in node.targets):payload=ast.literal_eval(node.value)
z=zipfile.ZipFile(io.BytesIO(base64.b64decode(payload)))
for name in z.namelist():assert z.read(name)==(r/'01_visual_variables_color'/name).read_bytes()
assert 'data/context.geojson' in z.namelist()
assert len(list(r.glob('0[2-4]*/README.md')))==3
print('PASS: classification, six starting designs, all six variable controls, case load/reset, stable before/after, SVG export and self-contained notebook integrity.')
