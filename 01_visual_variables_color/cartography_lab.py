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
from matplotlib.patches import Patch,Rectangle
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
            'water':context[context.layer=='water'], 'roads':context[context.layer=='road']}


def extent(view='Innenstadt'):
    if view=='Innenstadt':return (444800,449700,5535700,5540600)
    a,b,c,d=data()['boundary'].total_bounds
    return (a-350,c+350,b-350,d+350)


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
    data()['boundary'].plot(ax=ax,facecolor='#eeece3',edgecolor='#c6c5bc',linewidth=.45,zorder=0)
    data()['water'].plot(ax=ax,facecolor='#ccdee0',edgecolor='none',zorder=1)
    bar=1000 if view=='Innenstadt' else 2000
    x=x0+(x1-x0)*.04;y=y0+(y1-y0)*.035
    ax.plot([x,x+bar],[y,y],color=INK,lw=1.5,zorder=20)
    ax.text(x,y+(y1-y0)*.022,f'{bar//1000} km',fontsize=7.3,color=INK,zorder=20)
    ax.annotate('N',xy=(.955,.94),xytext=(.955,.88),xycoords='axes fraction',textcoords='axes fraction',ha='center',fontsize=8,color=INK,arrowprops={'arrowstyle':'-|>','lw':.8,'color':INK})
    # Locator: the study window within the city; not a decorative globe.
    loc=fig.add_axes([.785,.635,.15,.15],facecolor=PAPER)
    data()['boundary'].plot(ax=loc,facecolor='#e5e1d5',edgecolor='#9a9a8c',linewidth=.6)
    loc.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,edgecolor='#ad573c',linewidth=1))
    a,b,c,d=data()['boundary'].total_bounds;loc.set_xlim(a-800,c+800);loc.set_ylim(b-800,d+800)
    loc.set_aspect('equal');loc.axis('off')
    fig.text(.785,.618,'Ausschnitt im Stadtgebiet',fontsize=7.2,color=MUTED)
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
BERTIN_CASES={
 'Karte A':{**BERTIN_BASE,'size':155,'palette':'Grell','form':'Verschiedene Formen',
                        'angle':40,'directions':True,'texture':'Kategorien','texture_density':3,'background':.95},
 'Karte B':{**BERTIN_BASE,'size':12,'palette':'Ein Farbton','form':'Kreise',
                                  'lightness':.83,'background':.8,'names':False},
 'Karte C':{**BERTIN_BASE,'size':160,'size_mode':'Nach Kategorie',
                                    'light_mode':'Nach Kategorie','palette':'Ein Farbton','form':'Kreise'}
}
BERTIN_DEFAULT=BERTIN_CASES['Karte A']


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
        sub.plot(ax=ax,facecolor='#cac7b5',edgecolor='#777967' if texture else 'none',
                 linewidth=.15 if texture else 0,hatch=texture,alpha=p['background'],zorder=2)
    d['roads'].plot(ax=ax,color='#fefdf6',linewidth=.5,alpha=.8,zorder=3)
    # Keep water visible on top of any overlapping land-use geometry.
    d['water'].plot(ax=ax,facecolor='#ccdee0',edgecolor='none',zorder=3)
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
COLOR_CASES={
 'Karte A':{**COLOR_BASE,'palette':'tab10','k':7,'border':.25},
 'Karte B':{**COLOR_BASE,'method':'Equal Interval','k':5},
 'Karte C':{**COLOR_BASE,'contrast':.22,'k':7}
}
COLOR_DEFAULT=COLOR_CASES['Karte A']


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
    pop.plot(ax=ax,color=colors[ids],edgecolor=PAPER,linewidth=p['border'],zorder=4)
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


def png(fig,dpi=110):
    stream=io.BytesIO();fig.savefig(stream,format='png',dpi=dpi,facecolor=fig.get_facecolor());plt.close(fig)
    return base64.b64encode(stream.getvalue()).decode()


def image_html(fig):
    return '<img alt="Kartendarstellung" style="display:block;width:100%;height:auto" src="data:image/png;base64,'+png(fig)+'">'


class Lab:
    def __init__(self,kind='bertin'):
        self.kind=kind;self.cases=BERTIN_CASES if kind=='bertin' else COLOR_CASES
        self.original=copy.deepcopy(next(iter(self.cases.values())))
        self.controls={};self.busy=False
        def add(key,cls,**kw):
            c=cls(value=self.original[key],style={'description_width':'initial'},layout=W.Layout(width='255px'),**kw)
            self.controls[key]=c;return c
        if kind=='bertin':
            groups=[
                ('Größe', [add('size',W.IntSlider,description='Symbolfläche',min=8,max=200,step=4,continuous_update=False),add('size_mode',W.Dropdown,description='Zuordnung',options=['Einheitlich','Nach Kategorie'])]),
                ('Helligkeit',[add('lightness',W.FloatSlider,description='Helligkeit',min=.20,max=.88,step=.02,continuous_update=False),add('light_mode',W.Dropdown,description='Zuordnung',options=['Einheitlich','Nach Kategorie'])]),
                ('Farbton',[add('palette',W.Dropdown,description='Farben',options=['Vier Farbtöne','Ein Farbton','Grell'])]),
                ('Form',[add('form',W.Dropdown,description='Zeichen',options=['Kreise','Dreiecke','Verschiedene Formen'])]),
                ('Orientierung',[add('angle',W.IntSlider,description='Drehwinkel',min=0,max=180,step=10,continuous_update=False),add('directions',W.Checkbox,description='Richtung je Kategorie'),W.HTML('<small style="color:#444">An Kreisen ist eine Drehung unsichtbar.</small>')]),
                ('Textur',[add('texture',W.Dropdown,description='Flächenmuster',options=['Keine','Kategorien']),add('texture_density',W.IntSlider,description='Musterdichte',min=1,max=4,continuous_update=False)])]
            common=[add('background',W.FloatSlider,description='Hintergrundkontrast',min=.05,max=1,step=.05,continuous_update=False),add('names',W.Checkbox,description='Orientierungsnamen')]
        else:
            groups=[('Klassifikation',[add('method',W.Dropdown,description='Methode',options=['Equal Interval','Quantile','Jenks (Fisher-Jenks)']),add('k',W.IntSlider,description='Klassen',min=3,max=7,continuous_update=False)]),
                    ('Farben',[add('palette',W.Dropdown,description='Palette',options=[('Sequenziell · Orange–Rot','YlOrRd'),('Sequenziell · Blau','Blues'),('Sequenziell · Viridis','viridis'),('Divergierend · Rot–Blau','RdBu'),('Qualitativ · Kategorien','tab10')]),add('reverse',W.Checkbox,description='Reihenfolge umkehren')]),
                    ('Lesbarkeit',[add('contrast',W.FloatSlider,description='Farbkontrast',min=.15,max=1,step=.05,continuous_update=False),add('gray',W.Checkbox,description='Graustufen prüfen')])]
            common=[add('border',W.FloatSlider,description='Randlinien',min=0,max=.65,step=.05,continuous_update=False),add('names',W.Checkbox,description='Orientierungsnamen')]
        common.append(add('view',W.Dropdown,description='Ausschnitt',options=['Innenstadt','Gesamtstadt']))
        cards=[]
        for title,children in groups:
            cards.append(W.VBox([W.HTML('<div style="background:#eeeade;color:#252b29;padding:6px;font-weight:600">'+title+'</div>'),*children],layout=W.Layout(width='280px',padding='10px',border='1px solid #d9d6c9',margin='4px')))
        self.case=W.Dropdown(options=list(self.cases),description='Ausgangskarte',layout=W.Layout(width='370px'),style={'description_width':'initial'})
        load=W.Button(description='Fall laden',button_style='info',layout=W.Layout(width='110px'));load.on_click(self.load_case)
        buttons=[]
        for text,fn in [('Vorher / Nachher',self.compare),('Nur meine Karte',self.render),('Ausgangskarte zurücksetzen',self.reset),('SVG exportieren',self.svg),('PNG exportieren',self.png_export)]:
            b=W.Button(description=text,layout=W.Layout(width='205px' if 'zurück' in text else '150px'));b.on_click(fn);buttons.append(b)
        self.map=W.HTML(layout=W.Layout(width='100%'))
        self.message=W.HTML()
        # The lesson instructions are Markdown in the notebook, not a long coloured banner.
        self.ui=W.VBox([W.HBox([self.case,load],layout=W.Layout(flex_flow='row wrap')),
            W.Box(cards,layout=W.Layout(display='flex',flex_flow='row wrap')),
            W.Box(common,layout=W.Layout(display='flex',flex_flow='row wrap',gap='10px',padding='8px')),
            W.Box(buttons,layout=W.Layout(display='flex',flex_flow='row wrap',gap='6px',padding='8px 0')),
            self.message,self.map],layout=W.Layout(width='100%',max_width='1050px'))
        for c in self.controls.values():c.observe(self.changed,names='value')
        self.sync_controls();self.render()

    def values(self):return {k:c.value for k,c in self.controls.items()}
    def figure(self,p,label='Ihre Fassung'):return bertin_map(p,label) if self.kind=='bertin' else color_map(p,label)
    def sync_controls(self):
        if self.kind=='bertin':
            self.controls['lightness'].disabled=self.controls['light_mode'].value!='Einheitlich'
            self.controls['texture_density'].disabled=self.controls['texture'].value=='Keine'
    def changed(self,event):
        if not self.busy:
            self.sync_controls();self.render()
    def assign(self,p):
        self.busy=True
        try:
            for key,v in p.items():self.controls[key].value=v
        finally:self.busy=False
        self.sync_controls()
    def load_case(self,_=None):
        self.original=copy.deepcopy(self.cases[self.case.value]);self.assign(self.original)
        self.message.value='<p style="color:#252b29;background:#f4f1e8;padding:9px;line-height:1.5">Ausgangskarte geladen. Nennen Sie zuerst zwei Probleme. Ändern Sie dann gezielt die Gestaltung.</p>'
        self.render()
    def reset(self,_=None):self.assign(self.original);self.render()
    def render(self,_=None):self.map.value=image_html(self.figure(self.values()))
    def compare(self,_=None):
        before={**self.original,'view':self.values()['view']}
        left=image_html(self.figure(before,'Vorher · Ausgangskarte'))
        right=image_html(self.figure(self.values(),'Nachher · Ihre Fassung'))
        self.map.value='<div style="display:flex;flex-wrap:wrap;gap:8px"><div style="flex:1 1 400px;min-width:0"><p style="background:#eeeade;color:#252b29;padding:8px;font-weight:600">Vorher · Ausgangskarte</p>'+left+'</div><div style="flex:1 1 400px;min-width:0"><p style="background:#eeeade;color:#252b29;padding:8px;font-weight:600">Nachher · Ihre Fassung</p>'+right+'</div></div>'
        self.message.value='<p style="color:#252b29;background:#f4f1e8;padding:9px">Welche Änderung hilft der Leserin oder dem Leser? Welche Information ist jetzt leichter erkennbar?</p>'
    def export(self,ext):
        target=ROOT/'results';target.mkdir(exist_ok=True)
        path=target/f'Mainz_{self.kind}_Redesign.{ext}';fig=self.figure(self.values());fig.savefig(path,dpi=240,facecolor=PAPER);plt.close(fig)
        (target/f'Mainz_{self.kind}_settings.json').write_text(json.dumps(self.values(),ensure_ascii=False,indent=2))
        try:
            from google.colab import files
            files.download(str(path))
        except ImportError:self.message.value=f'<p style="color:#252b29">Gespeichert: {path}</p>'
    def svg(self,_=None):self.export('svg')
    def png_export(self,_=None):self.export('png')
    def show(self):display(self.ui);return self


def case_gallery(kind='bertin'):
    cases=BERTIN_CASES if kind=='bertin' else COLOR_CASES
    render=bertin_map if kind=='bertin' else color_map
    cards=[]
    for name,p in cases.items():
        cards.append('<div style="flex:1 1 280px;min-width:0;border:1px solid #d8d5cb"><p style="color:#252b29;background:#f6f3e9;font-weight:600;margin:0;padding:10px">'+name+'</p>'+image_html(render(p,'Ausgangskarte'))+'</div>')
    from IPython.display import HTML
    display(HTML('<div style="display:flex;flex-wrap:wrap;gap:8px">'+''.join(cards)+'</div>'))


def bertin_lab():return Lab('bertin').show()
def color_lab():return Lab('color').show()
