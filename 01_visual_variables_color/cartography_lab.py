"""Guided map critiques: diagnose, redesign, justify. MIT code; separate data licences."""
from pathlib import Path
from functools import lru_cache
import base64,copy,io,json,warnings,colorsys
import numpy as np
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Patch,Rectangle,PathPatch
from matplotlib.collections import PatchCollection,LineCollection,PolyCollection
from matplotlib.path import Path as MplPath
from matplotlib.markers import MarkerStyle
from matplotlib.transforms import Affine2D
from matplotlib.colors import to_rgb
import mapclassify
import ipywidgets as W
from IPython.display import display

ROOT=Path(__file__).resolve().parent
INK='#242a2a';MUTED='#6a706d';PAPER='#faf8f1';YELLOW='#efc647'
CATS=('Schule','Kindertagesstätte','Bibliothek','Sportzentrum')
NAMES=('Schulen','Kitas','Bibliotheken','Sportzentren')
COLORS=['#246a7b','#ba633e','#83723e','#7a6284']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})

@lru_cache(maxsize=1)
def data():
    f=gpd.read_file(ROOT/'data/facilities.geojson').to_crs(25832)
    context=gpd.read_file(ROOT/'data/context.geojson').to_crs(25832)
    return {'poi':f[(f.layer=='poi')&f.category_de.isin(CATS)].copy(),
            'land':f[f.layer=='landuse'].copy(),
            'pop':gpd.read_file(ROOT/'data/population.geojson').to_crs(25832),
            'boundary':gpd.read_file(ROOT/'data/boundary.geojson').to_crs(25832),
            'germany':gpd.read_file(ROOT/'data/germany.geojson').to_crs(3035),
            'water':context[context.layer=='water'], 'roads':context[context.layer=='road']}


def extent(view='Innenstadt'):
    if view=='Innenstadt':return (444800,449700,5535700,5540600)
    a,b,c,d=data()['boundary'].total_bounds
    return (a-350,c+350,b-350,d+350)


@lru_cache(maxsize=64)
def polygon_paths(kind,view,category=None):
    frame=data()[kind]
    if category is not None:frame=frame[frame.category_de==category]
    x0,x1,y0,y1=extent(view)
    frame=frame.cx[x0:x1,y0:y1]
    from shapely.geometry.polygon import orient
    result=[]
    def add(g):
        if g.geom_type=='Polygon':
            g=orient(g,sign=1.)
            rings=[np.asarray(g.exterior.coords),*[np.asarray(r.coords) for r in g.interiors]]
            codes=[]
            for ring in rings:codes.extend([MplPath.MOVETO]+[MplPath.LINETO]*(len(ring)-2)+[MplPath.CLOSEPOLY])
            result.append(MplPath(np.concatenate(rings),codes))
        elif hasattr(g,'geoms'):
            for sub in g.geoms:add(sub)
    for g in frame.geometry:add(g)
    return result


def draw_polygons(ax,kind,view,category=None,**style):
    patches=[PathPatch(path) for path in polygon_paths(kind,view,category)]
    if patches:ax.add_collection(PatchCollection(patches,**style))


@lru_cache(maxsize=2)
def road_segments(view):
    x0,x1,y0,y1=extent(view);segments=[]
    def add(g):
        if g.geom_type=='LineString':segments.append(np.asarray(g.coords))
        elif hasattr(g,'geoms'):
            for sub in g.geoms:add(sub)
    for g in data()['roads'].cx[x0:x1,y0:y1].geometry:add(g)
    return segments


@lru_cache(maxsize=1)
def population_vertices():return [np.asarray(g.exterior.coords) for g in data()['pop'].geometry]


def editorial(title,subtitle,view,number):
    fig=plt.figure(figsize=(11,9.3),facecolor=PAPER)
    fig.add_artist(Rectangle((.055,.935),.027,.022,transform=fig.transFigure,facecolor=YELLOW,edgecolor=INK,linewidth=.8))
    fig.text(.095,.941,'STADTATLAS  /  MAINZ',fontsize=9.3,weight='bold',color=INK)
    fig.text(.945,.941,number,ha='right',fontsize=9,color=MUTED)
    fig.text(.055,.876,title,fontfamily='DejaVu Serif',fontsize=27,weight='bold',color=INK)
    fig.text(.055,.839,subtitle,fontsize=9.1,color=MUTED)
    ax=fig.add_axes([.045,.15,.69,.65],facecolor=PAPER)
    x0,x1,y0,y1=extent(view);ax.set_xlim(x0,x1);ax.set_ylim(y0,y1)
    ax.set_aspect('equal');ax.axis('off')
    # A subtle geographical reference, independent of the thematic encoding.
    draw_polygons(ax,'boundary',view,facecolor='#eeece3',edgecolor='#c6c5bc',linewidth=.45,zorder=0)
    draw_polygons(ax,'water',view,facecolor='#ccdee0',edgecolor='none',zorder=1)
    bar=1000 if view=='Innenstadt' else 2000
    x=x0+(x1-x0)*.04;y=y0+(y1-y0)*.035
    ax.plot([x,x+bar],[y,y],color=INK,lw=1.5,zorder=20)
    ax.text(x,y+(y1-y0)*.022,f'{bar//1000} km',fontsize=7.3,color=INK,zorder=20)
    ax.annotate('N',xy=(.955,.94),xytext=(.955,.88),xycoords='axes fraction',textcoords='axes fraction',ha='center',fontsize=8,color=INK,arrowprops={'arrowstyle':'-|>','lw':.8,'color':INK})
    # Germany locator: the actual geographic position of Mainz.
    loc=fig.add_axes([.785,.635,.15,.15],facecolor=PAPER)
    germany=data()['germany']
    germany.plot(ax=loc,facecolor='#e5e1d5',edgecolor='#8f9283',linewidth=.65)
    from pyproj import Transformer
    mx,my=Transformer.from_crs(4326,3035,always_xy=True).transform(8.2473,50.0000)
    loc.scatter([mx],[my],s=24,c='#ac5138',edgecolors=PAPER,linewidths=.7,zorder=5)
    loc.annotate('Mainz',(mx,my),xytext=(14,-8),textcoords='offset points',fontsize=7.7,
                 color=INK,arrowprops={'arrowstyle':'-','color':'#ac5138','lw':.7},zorder=6)
    a,b,c,d=germany.total_bounds;loc.set_xlim(a-20000,c+35000);loc.set_ylim(b-15000,d+15000)
    loc.set_aspect('equal');loc.axis('off')
    fig.text(.785,.618,'DEUTSCHLAND',fontsize=7.2,color=MUTED)
    return fig,ax


def place_names(ax,view):
    from pyproj import Transformer
    tr=Transformer.from_crs(4326,25832,always_xy=True)
    x0,x1,y0,y1=extent(view)
    for name,lon,lat in [('NEUSTADT',8.257,50.010),('ALTSTADT',8.276,49.998),('GONSENHEIM',8.208,50.005),('HECKTSHEIM',8.273,49.968)]:
        # Correct label spelling while retaining the explicit geographical anchor.
        name=name.replace('HECKTSHEIM','HECHTSHEIM')
        x,y=tr.transform(lon,lat)
        if x0<x<x1 and y0<y<y1:
            t=ax.text(x,y,name,fontsize=7,weight='medium',color='#565e59',ha='center',zorder=8)
            t.set_path_effects([pe.withStroke(linewidth=2.8,foreground=PAPER)])


def footer(fig,kind):
    if kind=='bertin':text='© OpenStreetMap contributors · ODbL · Stand: 24.10.2026\nAusgewählte OSM-Objekte; kein vollständiges Einrichtungsverzeichnis. Zugang nicht geprüft.'
    else:text='© Statistische Ämter des Bundes und der Länder, 2024 · Zensus 2022 · dl-de/by-2-0\nStichtag: 15.05.2022 · amtliche Geheimhaltung (CKM) · vollständige Zellen nach Zellmittelpunkt ausgewählt.'
    fig.add_artist(Line2D([.055,.945],[.105,.105],transform=fig.transFigure,color='#cecdc1',lw=.6))
    fig.text(.055,.065,text,fontsize=7.1,color=MUTED,linespacing=1.6)


BERTIN_BASE=dict(size=55,size_mode='Einheitlich',lightness=.43,light_mode='Einheitlich',
    palette='Vier Farbtöne',form='Verschiedene Formen',angle=0,directions=False,
    texture='Keine',texture_density=1,background=.2,names=True,view='Innenstadt')
BERTIN_DEFAULT={**BERTIN_BASE,'size':155,'palette':'Grell','form':'Verschiedene Formen',
                'angle':40,'directions':True,'texture':'Kategorien','texture_density':3,'background':.95}


def symbol(p,i):
    raw={'Kreise':['o']*4,'Dreiecke':['^']*4,'Verschiedene Formen':['o','s','^','D']}[p['form']][i]
    return MarkerStyle(raw).transformed(Affine2D().rotate_deg(p['angle']+(i*35 if p['directions'] else 0)))


def category_style(p,i):
    base=COLORS[i] if p['palette']=='Vier Farbtöne' else ['#ee00c8','#00e685','#4736f5','#f79400'][i] if p['palette']=='Grell' else '#326b78'
    h,_,s=colorsys.rgb_to_hls(*to_rgb(base))
    light=p['lightness'] if p['light_mode']=='Einheitlich' else [.25,.42,.59,.76][i]
    color=colorsys.hls_to_rgb(h,light,s)
    size=p['size'] if p['size_mode']=='Einheitlich' else p['size']*[1,.50,.23,.10][i]
    return color,size


def bertin_map(settings=None,label='Ihre Fassung'):
    p={**BERTIN_DEFAULT,**(settings or {})};d=data()
    fig,ax=editorial('Die Stadt und ihre Orte','Schulen, Kitas, Bibliotheken und Sportzentren · gleiche Daten, andere Gestaltung',p['view'],'01 / VISUELLE VARIABLEN')
    # Intentional critique presets may make the context overpower the theme.
    land=d['land'];patterns=['/','\\','o','x','|','-','.','+']
    for i,(cat,sub) in enumerate(land.groupby('category_de')):
        texture=patterns[i%len(patterns)]*p['texture_density'] if p['texture']=='Kategorien' else ''
        draw_polygons(ax,'land',p['view'],category=cat,facecolor='#cac7b5',edgecolor='#777967' if texture else 'none',
                 linewidth=.15 if texture else 0,hatch=texture,alpha=p['background'],zorder=2)
    ax.add_collection(LineCollection(road_segments(p['view']),colors='#fefdf6',linewidths=.5,alpha=.8,zorder=3))
    # Keep water visible on top of any overlapping land-use geometry.
    draw_polygons(ax,'water',p['view'],facecolor='#ccdee0',edgecolor='none',zorder=3)
    handles=[]
    for i,(cat,name) in enumerate(zip(CATS,NAMES)):
        sub=d['poi'][d['poi'].category_de==cat];color,size=category_style(p,i);marker=symbol(p,i)
        ax.scatter(sub.geometry.x,sub.geometry.y,c=[color],s=size,marker=marker,
                   edgecolors=PAPER,linewidths=.65,zorder=10)
        handles.append(Line2D([],[],color='none',marker=marker,markerfacecolor=color,
                              markeredgecolor=PAPER,markersize=np.sqrt(size),label=name))
    if p['names']:place_names(ax,p['view'])
    fig.text(.785,.57,'EINRICHTUNGSTYPEN',fontsize=8,weight='bold',color=INK)
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.772,.555),frameon=False,
               fontsize=8.8,labelspacing=1.65,handletextpad=1)
    fig.text(.785,.32,'LESERAUFGABE',fontsize=8,weight='bold',color=INK)
    fig.text(.785,.292,'Wo liegen die vier Typen?\nWelche lassen sich schnell\nunterscheiden?',fontsize=8.4,color=MUTED,linespacing=1.6,va='top')
    if p['size_mode']=='Nach Kategorie' or p['light_mode']=='Nach Kategorie':
        fig.text(.785,.205,'Größe / Helligkeit kodiert\nhier nur den Typ, keine\nKapazität oder Qualität.',fontsize=7.6,color='#9b4f34',va='top')
    footer(fig,'bertin')
    fig.text(.945,.115,label,ha='right',fontsize=7.5,color=MUTED)
    return fig


COLOR_BASE=dict(method='Quantile',k=5,palette='YlOrRd',reverse=False,gray=False,
                contrast=1.,border=.06,names=True,view='Gesamtstadt')
COLOR_DEFAULT={**COLOR_BASE,'palette':'tab10','k':7,'border':.25}


def classify(values,method,k):return _classified(tuple(np.asarray(values,float)),method,int(k))
@lru_cache(maxsize=64)
def _classified(values,method,k):
    v=np.asarray(values);k=min(k,len(np.unique(v)))
    if not len(v) or not np.isfinite(v).all():raise ValueError('Finite values required')
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        model={'Equal Interval':mapclassify.EqualInterval,'Quantile':mapclassify.Quantiles,'Jenks (Fisher-Jenks)':mapclassify.FisherJenks}[method](v,k=k)
    bins=np.unique(model.bins)
    return np.minimum(np.searchsorted(bins,v,side='left'),len(bins)-1),bins


def color_map(settings=None,label='Ihre Fassung'):
    p={**COLOR_DEFAULT,**(settings or {})};d=data();pop=d['pop'];vals=pop.population.to_numpy(float)
    ids,bins=classify(vals,p['method'],p['k']);k=len(bins)
    pos=np.linspace(.12,.94,k);pos=.52+(pos-.52)*p['contrast']
    if p['reverse']:pos=pos[::-1]
    colors=plt.get_cmap(p['palette'])(pos)
    if p['gray']:
        luminance=colors[:,:3]@np.array([.2126,.7152,.0722]);colors[:,:3]=luminance[:,None]
    fig,ax=editorial('Mainz, wo Menschen wohnen',f'Personen je 100 × 100 m · Zensus 2022 · {p["method"]} · {k} Klassen',p['view'],'02 / FARBE & KLASSIFIKATION')
    ax.add_collection(PolyCollection(population_vertices(),facecolors=colors[ids],edgecolors=PAPER,linewidths=p['border'],zorder=4))
    if p['names']:place_names(ax,p['view'])
    handles=[];lo=int(vals.min())
    for i,hi in enumerate(bins):
        handles.append(Patch(facecolor=colors[i],edgecolor='none',label=f'{lo}–{int(hi)}'));lo=int(hi)+1
    fig.text(.785,.57,'PERSONEN JE ZELLE',fontsize=8,weight='bold',color=INK)
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.772,.555),frameon=False,fontsize=8.5,labelspacing=.65)
    # Compact distribution, on the same page, rather than a second long output.
    h=fig.add_axes([.79,.215,.15,.09],facecolor=PAPER)
    h.hist(vals,bins=35,color='#bfc2b5',edgecolor='none')
    for b in bins[:-1]:h.axvline(b,color='#ae6347',lw=.75)
    h.spines[['top','right','left']].set_visible(False);h.spines['bottom'].set_color('#bbbcae')
    h.tick_params(labelsize=6,length=2);h.set_yticks([]);h.set_xlabel('Personen je Zelle',fontsize=6.5,labelpad=3)
    fig.text(.785,.325,'VERTEILUNG & GRENZEN',fontsize=7.2,weight='bold',color=INK)
    fig.text(.785,.162,'Keine veröffentlichte Zelle\nist keine gesicherte Null.',fontsize=7.2,color=MUTED)
    footer(fig,'color');fig.text(.945,.115,label,ha='right',fontsize=7.5,color=MUTED)
    return fig


def png_bytes(fig,dpi=90):
    stream=io.BytesIO();fig.savefig(stream,format='png',dpi=dpi,facecolor=fig.get_facecolor());plt.close(fig)
    return stream.getvalue()


@lru_cache(maxsize=32)
def rendered(kind,parameters):
    p=dict(parameters)
    fig=bertin_map(p,label='') if kind=='bertin' else color_map(p,label='')
    return png_bytes(fig)


class Lab:
    """One critique example: immutable left panel and editable right panel."""
    def __init__(self,kind='bertin'):
        self.kind=kind;self.original=copy.deepcopy(BERTIN_DEFAULT if kind=='bertin' else COLOR_DEFAULT)
        self.controls={};self.busy=False;self.applied=copy.deepcopy(self.original)
        def add(key,cls,**kw):
            c=cls(value=self.original[key],style={'description_width':'initial'},layout=W.Layout(width='255px'),**kw)
            self.controls[key]=c;return c
        if kind=='bertin':
            groups=[
                ('Größe', [add('size',W.IntSlider,description='Symbolfläche',min=8,max=200,step=4,continuous_update=False),add('size_mode',W.Dropdown,description='Zuordnung',options=['Einheitlich','Nach Kategorie'])]),
                ('Helligkeit',[add('lightness',W.FloatSlider,description='Helligkeit',min=.20,max=.88,step=.02,continuous_update=False),add('light_mode',W.Dropdown,description='Zuordnung',options=['Einheitlich','Nach Kategorie'])]),
                ('Farbton',[add('palette',W.Dropdown,description='Farben',options=['Vier Farbtöne','Ein Farbton','Grell'])]),
                ('Form',[add('form',W.Dropdown,description='Zeichen',options=['Kreise','Dreiecke','Verschiedene Formen'])]),
                ('Orientierung',[add('angle',W.IntSlider,description='Drehwinkel',min=0,max=180,step=10,continuous_update=False),add('directions',W.Checkbox,description='Richtung je Kategorie'),W.HTML('<small>An Kreisen ist eine Drehung unsichtbar.</small>')]),
                ('Textur',[add('texture',W.Dropdown,description='Flächenmuster',options=['Keine','Kategorien']),add('texture_density',W.IntSlider,description='Musterdichte',min=1,max=4,continuous_update=False)])]
            common=[add('background',W.FloatSlider,description='Hintergrundkontrast',min=.05,max=1,step=.05,continuous_update=False),add('names',W.Checkbox,description='Orientierungsnamen')]
        else:
            groups=[('Klassifikation',[add('method',W.Dropdown,description='Methode',options=['Equal Interval','Quantile','Jenks (Fisher-Jenks)']),add('k',W.IntSlider,description='Klassen',min=3,max=7,continuous_update=False)]),
                    ('Farben',[add('palette',W.Dropdown,description='Palette',options=[('Sequenziell · Orange–Rot','YlOrRd'),('Sequenziell · Blau','Blues'),('Sequenziell · Viridis','viridis'),('Divergierend · Rot–Blau','RdBu'),('Qualitativ · Kategorien','tab10')]),add('reverse',W.Checkbox,description='Reihenfolge umkehren')]),
                    ('Lesbarkeit',[add('contrast',W.FloatSlider,description='Farbkontrast',min=.15,max=1,step=.05,continuous_update=False),add('gray',W.Checkbox,description='Graustufen prüfen')])]
            common=[add('border',W.FloatSlider,description='Randlinien',min=0,max=.65,step=.05,continuous_update=False),add('names',W.Checkbox,description='Orientierungsnamen')]
        # A shared extent selector updates both panels together; the starting style stays fixed.
        add('view',W.Dropdown,description='Ausschnitt',options=['Innenstadt','Gesamtstadt'])
        common.append(self.controls['view'])
        cards=[]
        for title,children in groups:
            card=W.VBox([W.HTML('<b>'+title+'</b>'),*children],layout=W.Layout(width='280px',padding='9px',margin='4px'))
            card.add_class('karto-card');cards.append(card)
        self.left=W.Image(format='png',layout=W.Layout(width='100%',height='auto'))
        self.right=W.Image(format='png',layout=W.Layout(width='100%',height='auto'))
        self.message=W.HTML()
        self.update_button=W.Button(description='Rechte Karte aktualisieren',icon='refresh',layout=W.Layout(width='245px'))
        self.update_button.add_class('karto-primary');self.update_button.on_click(self.apply)
        reset=W.Button(description='Zurücksetzen',icon='undo',layout=W.Layout(width='155px'));reset.on_click(self.reset)
        svg=W.Button(description='SVG exportieren',icon='download',layout=W.Layout(width='165px'));svg.on_click(lambda _:self.export('svg'))
        png=W.Button(description='PNG exportieren',icon='download',layout=W.Layout(width='165px'));png.on_click(lambda _:self.export('png'))
        for b in [reset,svg,png]:b.add_class('karto-secondary')
        style=W.HTML("""<style>
.karto-lab{background:#faf8f1!important;color:#242a2a!important;padding:14px;border:1px solid #d9d3c4;border-radius:12px}
.karto-lab .widget-label,.karto-lab .widget-readout,.karto-lab label,.karto-lab b,.karto-lab small{color:#242a2a!important}
.karto-lab select{background:#fff!important;color:#242a2a!important;border:1px solid #d2cbbb!important;border-radius:6px!important}
.karto-card{background:#fffdf7;border:1px solid #e2ddcf;border-radius:9px}
.karto-lab .widget-button{height:38px!important;border-radius:7px!important;font-weight:600!important;box-shadow:none!important;transition:background .15s}
.karto-lab .karto-primary{background:#28574f!important;color:white!important;border:1px solid #28574f!important}
.karto-lab .karto-primary:hover{background:#193f38!important}
.karto-lab .karto-secondary{background:#f3eee0!important;color:#343b32!important;border:1px solid #d5cdbb!important}
.karto-lab .karto-secondary:hover{background:#e7dfcc!important}
</style>""")
        left_col=W.VBox([W.HTML('<div style="padding:10px;border-bottom:2px solid #b76548;font-weight:700;color:#242a2a">AUSGANGSKARTE · BLEIBT UNVERÄNDERT</div>'),self.left],layout=W.Layout(width='50%',min_width='0'))
        right_col=W.VBox([W.HTML('<div style="padding:10px;border-bottom:2px solid #28574f;font-weight:700;color:#242a2a">IHRE ÜBERARBEITUNG</div>'),self.right],layout=W.Layout(width='50%',min_width='0'))
        self.ui=W.VBox([style,W.Box(cards,layout=W.Layout(display='flex',flex_flow='row wrap')),
            W.Box(common,layout=W.Layout(display='flex',flex_flow='row wrap',gap='10px',padding='8px')),
            W.Box([self.update_button,reset,svg,png],layout=W.Layout(display='flex',flex_flow='row wrap',gap='7px',padding='8px 0')),
            self.message,W.HBox([left_col,right_col],layout=W.Layout(width='100%',gap='8px'))],layout=W.Layout(width='100%',max_width='1250px'))
        self.ui.add_class('karto-lab')
        for c in self.controls.values():c.observe(self.changed,names='value')
        self.sync_controls();self.apply()

    def values(self):return {k:c.value for k,c in self.controls.items()}
    def sync_controls(self):
        if self.kind=='bertin':
            self.controls['lightness'].disabled=self.controls['light_mode'].value!='Einheitlich'
            self.controls['texture_density'].disabled=self.controls['texture'].value=='Keine'
    def changed(self,event):
        if self.busy:return
        self.sync_controls()
        self.message.value='<p style="margin:4px 0;color:#87522d;font-size:12px">Einstellungen geändert. Mit „Rechte Karte aktualisieren“ anwenden.</p>'
    def assign(self,p):
        self.busy=True
        try:
            for key,v in p.items():self.controls[key].value=v
        finally:self.busy=False
        self.sync_controls()
    def apply(self,_=None):
        p=self.values();self.update_button.disabled=True
        self.message.value='<p style="color:#555;font-size:12px">Karte wird aktualisiert …</p>'
        try:
            before={**self.original,'view':p['view']}
            if getattr(self,'left_view',None)!=p['view']:
                self.left.value=rendered(self.kind,tuple(sorted(before.items())));self.left_view=p['view']
            self.right.value=rendered(self.kind,tuple(sorted(p.items())))
            self.applied=copy.deepcopy(p)
            self.message.value='<p style="margin:4px 0;color:#28574f;font-size:12px">Aktuell · links der feste Ausgangsentwurf, rechts Ihre Einstellungen.</p>'
        finally:self.update_button.disabled=False
    def reset(self,_=None):self.assign(self.original);self.apply()
    def export(self,ext):
        # Export the map actually shown, never silently apply pending edits.
        target=ROOT/'results';target.mkdir(exist_ok=True)
        path=target/f'Mainz_{self.kind}_Redesign.{ext}'
        fig=bertin_map(self.applied,'Ihre Überarbeitung') if self.kind=='bertin' else color_map(self.applied,'Ihre Überarbeitung')
        fig.savefig(path,dpi=240,facecolor=PAPER);plt.close(fig)
        (target/f'Mainz_{self.kind}_settings.json').write_text(json.dumps(self.applied,ensure_ascii=False,indent=2))
        try:
            from google.colab import files
            files.download(str(path))
        except ImportError:self.message.value=f'<p>Gespeichert: {path}</p>'
    def show(self):display(self.ui);return self


def bertin_lab():return Lab('bertin').show()
def color_lab():return Lab('color').show()
