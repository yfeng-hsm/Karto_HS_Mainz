"""Interactive, open-source cartography labs for Google Colab (German UI).
Code: MIT. Data retain ODbL / DL-DE-BY-2.0; see data/.
"""
from pathlib import Path
import colorsys
import copy
import warnings
from functools import lru_cache
import numpy as np
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.markers import MarkerStyle
from matplotlib.transforms import Affine2D
from matplotlib.colors import ListedColormap, to_rgb
import mapclassify
import ipywidgets as W
from IPython.display import display, clear_output, HTML

ROOT = Path(__file__).resolve().parent
INK = '#263a40'
ACCENT = '#b85d43'
PALE = '#f4f1ea'
CAT_COLORS = ['#417b89','#c36b4e','#8a8651','#8c6b91','#bd9849','#678b70','#a96070','#627fa2','#8c8a81','#b37a4c']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titleweight':'bold','svg.fonttype':'none'})
_DATA = None

def data():
    global _DATA
    if _DATA is None:
        facilities = gpd.read_file(ROOT/'data/facilities.geojson').to_crs(25832)
        _DATA = {'poi': facilities[facilities.layer == 'poi'].copy(),
                 'land': facilities[facilities.layer == 'landuse'].copy(),
                 'population': gpd.read_file(ROOT/'data/population.geojson').to_crs(25832),
                 'boundary': gpd.read_file(ROOT/'data/boundary.geojson').to_crs(25832)}
    return _DATA


def extent(view):
    if view == 'Innenstadt':
        # Fixed study window in ETRS89/UTM32, approximately 5.2 x 5.2 km.
        return (444300, 449500, 5534700, 5539900)
    a,b,c,d = data()['boundary'].total_bounds
    margin = 450
    return (a-margin,c+margin,b-margin,d+margin)


def canvas(title, subtitle, view='Innenstadt', paper='white', histogram=False):
    fig = plt.figure(figsize=(10.5,9.3 if histogram else 8.6), facecolor=paper)
    ax = fig.add_axes([.04,.24 if histogram else .14,.70,.61 if histogram else .71], facecolor=paper)
    fig.text(.055,.952,'MAINZ  /  KARTOGRAFISCHES LABOR',fontsize=9,color=ACCENT,weight='bold')
    fig.text(.055,.908,title,fontsize=23,weight='bold',color=INK)
    fig.text(.055,.871,subtitle,fontsize=9.2,color='#697477')
    boundary = data()['boundary']
    boundary.plot(ax=ax,facecolor=PALE,edgecolor='#d7d5cc',linewidth=.55,zorder=0)
    x0,x1,y0,y1 = extent(view)
    ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect('equal');ax.axis('off')
    # A scale bar in projected metres.
    length = 1000 if view == 'Innenstadt' else 2000
    x=x0+(x1-x0)*.06;y=y0+(y1-y0)*.045
    ax.plot([x,x+length],[y,y],color=INK,lw=1.7,zorder=12)
    ax.text(x,y+(y1-y0)*.018,f'{length//1000} km',fontsize=8,color=INK,zorder=12)
    fig.text(.755,.83,'LEGENDE',fontsize=9,color=INK,weight='bold')
    return fig,ax


def footer(fig, text):
    fig.text(.055,.055,text,fontsize=7,color='#697477',va='bottom',linespacing=1.5)


def legend(fig, handles, title=''):
    fig.legend(handles=handles,title=title,loc='upper left',bbox_to_anchor=(.742,.81),
               frameon=False,fontsize=8,title_fontsize=8,labelspacing=1.2,handlelength=1.6)


BERTIN_DEFAULT = dict(variable='Farbton',categories=('Schule','Kindertagesstätte','Bibliothek','Sportzentrum'),
    metric='nearby_poi_500m',size=80,light_min=.30,light_max=.82,hue=195,
    palette='Editorial',form_family='Gemischt',shape='^',angle=30,angle_step=30,pattern='Schraffur',density=1,
    view='Innenstadt',labels=False,show_land=True,background=.65)


def bertin_map(settings=None):
    p={**BERTIN_DEFAULT,**(settings or {})}
    d=data();poi=d['poi'][d['poi'].category_de.isin(p['categories'])].copy()
    variable=p['variable'];combo=variable=='Kombination'
    title='Einrichtungen im Stadtraum'
    subtitle=f"Visuelle Variable: {variable}  ·  {len(poi)} ausgewählte OSM-Objekte im Stadtgebiet"
    fig,ax=canvas(title,subtitle,p['view'])
    land=d['land']
    if p['show_land']:
        land.plot(ax=ax,facecolor='#e4e4da',edgecolor='white',linewidth=.15,alpha=p['background'],zorder=1)
    if variable=='Textur' or combo:
        patterns={'Schraffur':['/','\\','|','-','+','x','o','.'],
                  'Punkte':['.','o','O','..','oo','**','++','xx'],
                  'Gemischt':['/','o','x','-','|','+','.','O']}[p['pattern']]
        cats=sorted(land.category_de.unique())
        for i,cat in enumerate(cats):
            land[land.category_de==cat].plot(ax=ax,facecolor='#efeee6',edgecolor='#9a9d8d',
                linewidth=.12,hatch=patterns[i%len(patterns)]*p['density'],alpha=.78,zorder=2)
        handles=[matplotlib.patches.Patch(facecolor='#efeee6',edgecolor='#7a7e70',
                hatch=patterns[i%len(patterns)]*p['density'],label=cat) for i,cat in enumerate(cats)]
    else: handles=[]
    numeric=p['metric']
    values=poi[numeric].astype(float).to_numpy() if len(poi) else np.array([])
    finite=np.isfinite(values)
    vmax=max(float(np.nanmax(values[finite])),1.) if finite.any() else 1.
    use_size=variable=='Größe' or combo
    use_light=variable=='Helligkeit' or combo
    use_hue=variable=='Farbton' or combo
    use_shape=variable=='Form' or combo
    use_angle=variable=='Orientierung' or combo
    for i,cat in enumerate(p['categories']):
        sub=poi[poi.category_de==cat];v=sub[numeric].astype(float).to_numpy()
        norm=np.clip(np.nan_to_num(v,nan=0)/vmax,0,1)
        sizes=np.maximum(5,norm*p['size']) if use_size else np.full(len(sub),p['size'])
        if use_hue:
            base=CAT_COLORS[i%len(CAT_COLORS)] if p['palette']=='Editorial' else plt.get_cmap('tab10')(i%10)
        else:base=colorsys.hls_to_rgb(p['hue']/360,.46,.48)
        if use_light:
            hh,_,ss=colorsys.rgb_to_hls(*to_rgb(base))
            colors=[colorsys.hls_to_rgb(hh,p['light_max']-(p['light_max']-p['light_min'])*n,ss) for n in norm]
        else:colors=[base]*len(sub)
        if use_size or use_light:
            colors=[c if np.isfinite(vv) else '#bbbcb7' for c,vv in zip(colors,v)]
        forms={'Gemischt':['o','s','^','D','P','v','X','>','p','*'], 'Kantig':['s','D','^','v','>','<','P','X','p','*'], 'Rund und sternförmig':['o','p','h','8','*','H','s','D','P','X']}[p['form_family']]
        symbol=forms[i%10] if use_shape else 'o'
        if use_angle:symbol=p['shape']
        marker=MarkerStyle(symbol)
        if use_angle:marker=marker.transformed(Affine2D().rotate_deg(p['angle']+i*p['angle_step']))
        ax.scatter(sub.geometry.x,sub.geometry.y,s=sizes,c=colors,marker=marker,
                   edgecolors='white',linewidths=.55,alpha=.92,zorder=5)
        if variable!='Textur' and not combo:
            handles.append(Line2D([],[],marker=marker,color='none',markerfacecolor=base,
                markeredgecolor='white',markersize=8,label=cat))
    if p['labels']:
        x0,x1,y0,y1=extent(p['view'])
        named=poi[poi.name.notna() & poi.geometry.x.between(x0,x1) & poi.geometry.y.between(y0,y1)]
        for _,row in named.head(6).iterrows():
            ax.annotate(str(row['name'])[:36],(row.geometry.x,row.geometry.y),xytext=(5,5),
                        textcoords='offset points',fontsize=6.8,color=INK,zorder=10,
                        bbox=dict(boxstyle='round,pad=.15',fc='white',ec='none',alpha=.8))
    legend(fig,handles,'Stadtflächen' if variable=='Textur' or combo else 'Einrichtungstyp')
    numeric_active=use_size or use_light
    if numeric_active:
        label='Andere ausgewählte POI\nim 500-m-Radius' if numeric=='nearby_poi_500m' else 'Kartierte Fläche (m²)\nFehlende Werte: grau'
        fig.text(.755,.29,label,fontsize=8,color=INK)
        if use_size:
            positive=values[finite & (values>0)]
            qs=np.unique(np.quantile(positive,[.25,.6,1]).astype(int)) if len(positive) else []
            y=.24
            for val in qs:
                fig.add_artist(Line2D([.768],[y],marker='o',markersize=np.sqrt(max(5,val/vmax*p['size'])),
                    markerfacecolor='#6f858a',markeredgecolor='white',linestyle='none',transform=fig.transFigure))
                fig.text(.805,y-.004,f'{val:,}'.replace(',','.'),fontsize=8,color=INK);y-=.035
        elif use_light:
            fig.text(.755,.23,f'hell: 0  →  dunkel: {vmax:g}',fontsize=8,color=INK)
    if variable=='Orientierung':
        fig.text(.755,.32,'Drehung kodiert hier Kategorien,\nkeine reale Bewegungsrichtung.',fontsize=8,color=INK)
    if combo:fig.text(.755,.24,'Kombination: Sind alle\nInformationen noch lesbar?',fontsize=8,color=INK)
    footer(fig,'© OpenStreetMap contributors · ODbL · OSM-Stand: 24.10.2026\n'
               'Auswahl, keine vollständige Bestandsliste. Zugang nicht geprüft. Größenminimum: 5 pt².\n'
               'Nachbarschaft zählt nur POI dieser Auswahl; Fläche ist keine Kapazität oder Qualität.')
    return fig


COLOR_DEFAULT=dict(method='Quantile',k=5,palette='YlOrRd',reverse=False,gray=False,
                   border=.12,view='Gesamtstadt',paper='Weiß',labels=True)


def classify(values,method,k):
    return _classify_cached(tuple(np.asarray(values,float)),method,int(k))


@lru_cache(maxsize=64)
def _classify_cached(values,method,k):
    values=np.asarray(values,float)
    if not len(values) or not np.isfinite(values).all():raise ValueError('Finite values required')
    k=min(int(k),len(np.unique(values)))
    classifiers={'Equal Interval':mapclassify.EqualInterval,'Quantile':mapclassify.Quantiles,
                 'Jenks (Fisher-Jenks)':mapclassify.FisherJenks}
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        obj=classifiers[method](values,k=k)
    bins=np.unique(obj.bins)
    # searchsorted(right=False) keeps upper boundaries in their lower class.
    ids=np.minimum(np.searchsorted(bins,values,side='left'),len(bins)-1)
    return ids,bins


def color_map(settings=None):
    p={**COLOR_DEFAULT,**(settings or {})};d=data();pop=d['population']
    vals=pop.population.to_numpy(float);ids,bins=classify(vals,p['method'],p['k'])
    k=len(bins)
    cmap=plt.get_cmap(p['palette']);positions=np.linspace(.13,.93,k)
    if p['reverse']:positions=positions[::-1]
    colors=cmap(positions)
    if p['gray']:
        luminance=colors[:,:3]@np.array([.2126,.7152,.0722]);colors[:,:3]=luminance[:,None]
    paper='white' if p['paper']=='Weiß' else '#faf7ef'
    subtitle=f"Zensus 2022 · Personen je 100 × 100 m · {p['method']} · {k} Klassen"
    fig,ax=canvas('Wo wohnen die Menschen in Mainz?',subtitle,p['view'],paper,True)
    pop.assign(_class=ids).plot(ax=ax,color=colors[ids],edgecolor=paper,linewidth=p['border'],zorder=3)
    handles=[];lo=int(vals.min())
    for i,hi in enumerate(bins):
        handles.append(matplotlib.patches.Patch(facecolor=colors[i],edgecolor='none',label=f'{lo}–{int(hi)}'))
        lo=int(hi)+1
    legend(fig,handles,'Personen je Zelle')
    fig.text(.755,.44,'Keine veröffentlichte Zelle:\nkeine gesicherte Null.\n\nGitterfläche: 1 ha\nPersonen/km² = Wert × 100',fontsize=8,color='#6d7775')
    if p['palette'] in ['RdBu','Spectral']:
        fig.text(.755,.31,'Diskussion: Gibt es für diese\nDaten einen sachlich sinnvollen\nMittelpunkt?',fontsize=8,color=ACCENT)
    if p['labels']:
        # Geographic reference labels, manually positioned; not demographic observations.
        from pyproj import Transformer
        tr=Transformer.from_crs(4326,25832,always_xy=True)
        for name,lon,lat in [('Neustadt',8.257,50.010),('Altstadt',8.276,49.999),('Gonsenheim',8.208,50.005),('Hechtsheim',8.273,49.968)]:
            x,y=tr.transform(lon,lat);x0,x1,y0,y1=extent(p['view'])
            if x0<x<x1 and y0<y<y1:
                import matplotlib.patheffects as pe
                text=ax.text(x,y,name,fontsize=7,color=INK,zorder=10,ha='center')
                text.set_path_effects([pe.withStroke(linewidth=2.2,foreground='white')])
    hist=fig.add_axes([.08,.135,.62,.075],facecolor=paper)
    hist.hist(vals,bins=50,color='#c2c7c3',edgecolor='none')
    for b in bins[:-1]:hist.axvline(b,color=ACCENT,lw=.9)
    hist.set_xlabel('Personen je Zelle · rote Linien: Klassengrenzen',fontsize=7,labelpad=2)
    hist.set_ylabel('Zellen',fontsize=7);hist.tick_params(labelsize=7)
    hist.spines[['top','right']].set_visible(False)
    hist.spines[['left','bottom']].set_color('#cdd2ce')
    footer(fig,'© Statistische Ämter des Bundes und der Länder, 2024 · Zensus 2022 · dl-de/by-2-0\n'
               'Stichtag: 15.05.2022 · 2.982 veröffentlichte Zellen · amtliche Geheimhaltung (CKM)\n'
               'Auswahl nach Zellmittelpunkt innerhalb Mainz; vollständige Randzellen. Kein amtlicher Stadtsummenwert.')
    return fig


class Lab:
    """Widget controller. Keep class reference for export and A/B comparisons."""
    def __init__(self,kind='bertin'):
        self.kind=kind;self.defaults=copy.deepcopy(BERTIN_DEFAULT if kind=='bertin' else COLOR_DEFAULT)
        self.controls={};self.a=None;self.last_figure=None
        style={'description_width':'120px'}
        def add(key,cls,**kwargs):
            self.controls[key]=cls(value=self.defaults[key],style=style,layout=W.Layout(width="290px"),**kwargs)
            return self.controls[key]
        if kind=='bertin':
            add('variable',W.Dropdown,description='Variable',options=['Größe','Helligkeit','Farbton','Form','Orientierung','Textur','Kombination'])
            add('categories',W.SelectMultiple,description='POI-Kategorien',options=sorted(data()['poi'].category_de.unique()),rows=5)
            add('metric',W.Dropdown,description='Zahlenmerkmal',options=[('POI im 500-m-Radius','nearby_poi_500m'),('Kartierte Fläche (m²)','area_m2')])
            add('size',W.IntSlider,description='Symbolfläche max.',min=15,max=320,step=5,continuous_update=False)
            add('light_min',W.FloatSlider,description='Dunkelster Ton',min=.1,max=.45,step=.025,continuous_update=False)
            add('light_max',W.FloatSlider,description='Hellster Ton',min=.55,max=.95,step=.025,continuous_update=False)
            add('hue',W.IntSlider,description='Grundfarbton',min=0,max=359,continuous_update=False)
            add('palette',W.Dropdown,description='Kategorienfarben',options=['Editorial','Tab10'])
            add('form_family',W.Dropdown,description='Formenfamilie',options=['Gemischt','Kantig','Rund und sternförmig'])
            add('shape',W.Dropdown,description='Gerichtete Form',options=[('Dreieck','^'),('Pfeil nach rechts','>'),('Dreieck links','<')])
            add('angle',W.IntSlider,description='Drehwinkel',min=0,max=180,step=5,continuous_update=False)
            add('angle_step',W.IntSlider,description='Winkel je Kategorie',min=0,max=90,step=15,continuous_update=False)
            add('pattern',W.Dropdown,description='Texturfamilie',options=['Schraffur','Punkte','Gemischt'])
            add('density',W.IntSlider,description='Texturdichte',min=1,max=4,continuous_update=False)
            add('background',W.FloatSlider,description='Flächenkontrast',min=.05,max=1,step=.05,continuous_update=False)
            add('show_land',W.Checkbox,description='Stadtflächen zeigen')
            add('labels',W.Checkbox,description='Einige Namen zeigen')
            hint='Eine Variable nach der anderen untersuchen. Form, Farbton und Richtung unterscheiden Kategorien; Größe/Helligkeit nutzen das Zahlenmerkmal. Texturen zeigen Stadtflächen. In „Kombination“ werden alle Variablen aktiv.'
        else:
            add('method',W.Dropdown,description='Klassifikation',options=['Equal Interval','Quantile','Jenks (Fisher-Jenks)'])
            add('k',W.IntSlider,description='Klassen',min=3,max=7,continuous_update=False)
            add('palette',W.Dropdown,description='Farbpalette',options=[('Sequenziell · Orange–Rot','YlOrRd'),('Sequenziell · Blau','Blues'),('Sequenziell · Viridis','viridis'),('Divergierend · Rot–Blau','RdBu'),('Divergierend · Spektral','Spectral'),('Qualitativ · Kategorien','tab10')])
            add('reverse',W.Checkbox,description='Farben umkehren')
            add('gray',W.Checkbox,description='Graustufen prüfen')
            add('border',W.FloatSlider,description='Randlinien',min=0,max=.8,step=.04,continuous_update=False)
            add('paper',W.Dropdown,description='Papier',options=['Weiß','Warm'])
            add('labels',W.Checkbox,description='Orientierungsnamen')
            hint='Vergleich 1: Palette und Klassenanzahl konstant halten, nur die Methode ändern. Vergleich 2: Klassifikation konstant halten, nur Farben ändern. Quantile können bei gleichen Werten weniger Klassen ergeben.'
        add('view',W.Dropdown,description='Kartenausschnitt',options=['Innenstadt','Gesamtstadt'])
        self.output=W.Output(layout=W.Layout(width='100%'))
        self.message=W.HTML()
        self.buttons=[]
        for label,fn in [('A merken',self.remember),('A/B vergleichen',self.compare),('Zurücksetzen',self.reset),('SVG herunterladen',self.export_svg),('PNG herunterladen',self.export_png)]:
            b=W.Button(description=label,layout=W.Layout(width='140px'));b.on_click(fn);self.buttons.append(b)
        for control in self.controls.values():control.observe(self.changed,names='value')
        self.panel=W.VBox(list(self.controls.values()),layout=W.Layout(width='315px',flex='0 0 315px'))
        self.ui=W.VBox([W.HTML('<div style="border-left:4px solid #b85d43;padding:10px 14px;background:#f7f4ee;line-height:1.5">'+hint+'</div>'),W.HBox([self.panel,self.output],layout=W.Layout(flex_flow='row wrap',align_items='flex-start')),W.HBox(self.buttons,layout=W.Layout(flex_flow='row wrap')),self.message])
        self.output.layout.flex='1 1 600px'
        self._sync_visibility();self.render()

    def values(self):return {k:c.value for k,c in self.controls.items()}
    def figure(self,p):return bertin_map(p) if self.kind=='bertin' else color_map(p)
    def _sync_visibility(self):
        if self.kind!='bertin':return
        var=self.controls['variable'].value
        groups={'form_family':{'Form','Kombination'},'size':{'Größe','Kombination'},'metric':{'Größe','Helligkeit','Kombination'},
                'light_min':{'Helligkeit','Kombination'},'light_max':{'Helligkeit','Kombination'},
                'hue':{'Größe','Helligkeit','Form','Orientierung','Textur','Kombination'},'palette':{'Farbton','Kombination'},
                'shape':{'Orientierung','Kombination'},'angle':{'Orientierung','Kombination'},'angle_step':{'Orientierung','Kombination'},
                'pattern':{'Textur','Kombination'},'density':{'Textur','Kombination'}}
        for key,allowed in groups.items():self.controls[key].layout.display='' if var in allowed else 'none'
    def changed(self,event):self._sync_visibility();self.render()
    def render(self):
        p=self.values()
        with self.output:
            clear_output(wait=True)
            if self.last_figure is not None:plt.close(self.last_figure)
            self.last_figure=self.figure(p);display(self.last_figure);plt.close(self.last_figure)
    def remember(self,_=None):
        self.a=copy.deepcopy(self.values());self.message.value='<b>Variante A gespeichert.</b> Ändern Sie eine Einstellung und wählen Sie „A/B vergleichen“.'
    def compare(self,_=None):
        if self.a is None:self.message.value='Bitte zuerst „A merken“ anklicken.';return
        with self.output:
            clear_output(wait=True)
            for name,p in [('A',self.a),('B',self.values())]:
                fig=self.figure(p);fig.text(.93,.95,name,fontsize=20,color=ACCENT,weight='bold');display(fig);plt.close(fig)
        self.message.value='A und B sind untereinander mit identischer Darstellungsgröße angeordnet.'
    def reset(self,_=None):
        for c in self.controls.values():c.unobserve(self.changed,names='value')
        for k,v in self.defaults.items():self.controls[k].value=v
        for c in self.controls.values():c.observe(self.changed,names='value')
        self._sync_visibility();self.render();self.message.value='Standardeinstellungen wiederhergestellt.'
    def export(self,extension):
        target=ROOT/'results';target.mkdir(exist_ok=True)
        path=target/f'Mainz_{self.kind}.{extension}'
        fig=self.figure(self.values());fig.savefig(path,dpi=240,facecolor=fig.get_facecolor());plt.close(fig)
        (target/f'Mainz_{self.kind}_settings.json').write_text(__import__('json').dumps(self.values(),ensure_ascii=False,indent=2))
        try:
            from google.colab import files
            files.download(str(path))
        except ImportError:self.message.value=f'Gespeichert: {path}'
    def export_svg(self,_=None):self.export('svg')
    def export_png(self,_=None):self.export('png')
    def show(self):display(self.ui);return self


def bertin_lab():return Lab('bertin').show()
def color_lab():return Lab('color').show()
