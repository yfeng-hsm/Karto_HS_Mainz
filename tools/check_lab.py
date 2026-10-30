"""Behavioral checks for the classification and interactive controls (no WebGL)."""
from pathlib import Path
import sys,ast,json,zipfile,base64,io
import numpy as np
import matplotlib
matplotlib.use('Agg')
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'01_visual_variables_color'))
import cartography_lab as lab

v=lab.data()['population'].population.to_numpy()
for method in ['Equal Interval','Quantile','Jenks (Fisher-Jenks)']:
 for k in [3,5,7]:
  ids,bins=lab.classify(v,method,k)
  assert len(ids)==2982 and np.all(np.diff(bins)>0)
  assert np.all(v<=bins[ids]) and ids.min()==0 and ids.max()==len(bins)-1
ids,bins=lab.classify(np.array([3]*40+[8]*20+[20]*20),'Quantile',7)
assert len(bins)<=3 and len(ids)==80

for var in ['Größe','Helligkeit','Farbton','Form','Orientierung','Textur','Kombination']:
 f=lab.bertin_map({'variable':var});f.canvas.draw();lab.plt.close(f)
# Scalar size control changes the actual plotted symbol area.
a=lab.bertin_map({'variable':'Größe','size':30})
b=lab.bertin_map({'variable':'Größe','size':200})
assert np.max(b.axes[0].collections[-1].get_sizes())>np.max(a.axes[0].collections[-1].get_sizes())
lab.plt.close(a);lab.plt.close(b)
for palette in ['YlOrRd','Blues','viridis','RdBu','Spectral','tab10']:
 f=lab.color_map({'palette':palette,'gray':True,'k':7});f.canvas.draw();lab.plt.close(f)
# A/B stores values, not a live alias; reset restores controls.
b=lab.Lab('bertin')
assert b.controls['variable'].layout.display!='none' and b.controls['palette'].layout.display!='none'
assert b.controls['metric'].layout.display=='none'
assert len({id(c.layout) for c in b.controls.values()})==len(b.controls)
b.remember();b.controls['variable'].value='Textur';assert b.a['variable']=='Farbton'
b.controls['density'].value=3;b.compare();b.reset();assert b.values()==lab.BERTIN_DEFAULT
b.export('svg');assert '<svg' in (lab.ROOT/'results/Mainz_bertin.svg').read_text()
c=lab.Lab('color');c.remember();c.controls['method'].value='Jenks (Fisher-Jenks)'
assert c.a['method']=='Quantile';c.reset();assert c.values()==lab.COLOR_DEFAULT
# Every notebook cell parses and its embedded source matches the readable files.
nb=json.loads((r/'01_visual_variables_color/01_Visuelle_Variablen_und_Farbe.ipynb').read_text())
setup=''.join(nb['cells'][1]['source']);tree=ast.parse(setup)
for node in ast.walk(tree):
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in node.targets):payload=ast.literal_eval(node.value)
z=zipfile.ZipFile(io.BytesIO(base64.b64decode(payload)))
for name in z.namelist():assert z.read(name)==(r/'01_visual_variables_color'/name).read_bytes()
for cell in nb['cells']:
 if cell['cell_type']=='code':ast.parse(''.join(cell['source']))
assert len(list(r.glob('0[2-4]*/README.md')))==3
print('PASS: real data, 9 classification configurations, tied quantiles, all six variables, six palettes, widget changes, A/B, reset, SVG export and embedded notebook integrity.')
