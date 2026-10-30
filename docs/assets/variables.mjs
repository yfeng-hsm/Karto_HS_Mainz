import {setupLayout,exportButtons,drawLocator} from './ui.mjs?v=10';
import {flowTo,symbolArea,defaultState,placeLabels,toneColor} from './variables-core.mjs?v=10';
const NS='http://www.w3.org/2000/svg',TYPES=['Schulen','Kindertagesstätten','Bibliotheken','Sportzentren'];
function el(tag,a={},p){const n=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(a))n.setAttribute(k,v);p?.append(n);return n;}
function text(p,x,y,t,size=13,a={}){const n=el('text',{x,y,'font-size':size,fill:'#293c38','font-family':'Arial, sans-serif',...a},p);n.textContent=t;return n;}
export async function start(){
 const d3=globalThis.d3,kind=document.body.dataset.lab;setupLayout(kind);
 const get=async path=>{const r=await fetch(path);if(!r.ok)throw Error('Daten konnten nicht geladen werden.');return r.json();};
 const regional=['quantitative','direction'].includes(kind);
 const [mainz,data,region]=await Promise.all([get(regional?'data/locator.json':'data/mainz.json'),kind==='nominal'?Promise.resolve(null):get(kind==='ordinal'?'data/accessibility.json':kind==='quantitative'?'data/cities.json':'data/wind.json'),regional?get('data/region.json'):Promise.resolve(null)]);
 const wind=kind==='direction'?data:null,points=kind==='nominal'?mainz.pois:kind==='ordinal'?data.pois:kind==='quantitative'?data.cities:wind.stations,bad=defaultState(kind),state={...bad};
 if(wind)region.bbox=wind.bbox;
 const measurement=p=>kind==='quantitative'?p.population:p.speed;
 const min=regional?Math.min(...points.map(measurement)):0,max=regional?Math.max(...points.map(measurement)):(kind==='ordinal'?2:3);
 const labels=kind==='nominal'?TYPES:kind==='ordinal'?['nicht zugänglich','eingeschränkt','zugänglich']:[];
 const value=p=>kind==='nominal'?p.category:kind==='ordinal'?p.level:p.population;
 const norm=p=>kind==='nominal'?p.category/3:kind==='ordinal'?p.level/2:(p.population-min)/(max-min);
 const num=x=>new Intl.NumberFormat('de-DE').format(x);
 function arrowPath(area){const pts=[[-.14,.5],[.14,.5],[.14,-.1],[.5,-.1],[0,-.5],[-.5,-.1],[-.14,-.1]];const a=Math.abs(pts.reduce((t,p,i)=>{const q=pts[(i+1)%pts.length];return t+p[0]*q[1]-q[0]*p[1];},0))/2,z=Math.sqrt(area/a);return pts.map((p,i)=>(i?'L':'M')+(p[0]*z)+','+(p[1]*z)).join('')+'Z';}
 function build(id){
  const svg=document.getElementById(id),defs=el('defs',{},svg);el('rect',{width:600,height:680,fill:'#ffffff'},svg);

  text(svg,16,37,kind==='nominal'?'Einrichtungen im Stadtraum':kind==='ordinal'?'Rollstuhlzugang in Mainz':kind==='quantitative'?'Städte im Vergleich':'Wohin strömt die Luft?',21,{'font-family':'Arial, sans-serif','font-weight':'bold'});
  text(svg,16,60,kind==='direction'?'DWD · '+wind.display_time:kind==='quantitative'?'Einwohner · 31.12.2024 · Gemeindegebiet':kind==='ordinal'?'Zugangsangaben laut OpenStreetMap · 30.10.2026':'Mainz · vier Einrichtungstypen',12);
  const projection=regional?d3.geoMercator().fitExtent([[16,85],[584,553]],{type:'MultiPoint',coordinates:[[region.bbox[0],region.bbox[1]],[region.bbox[2],region.bbox[3]]]}):d3.geoIdentity().reflectY(true).fitExtent([[16,85],[584,553]],{type:'MultiPoint',coordinates:[[mainz.views.bertin[0],mainz.views.bertin[2]],[mainz.views.bertin[1],mainz.views.bertin[3]]]});
  const path=d3.geoPath(projection),clip=el('clipPath',{id:id+'-clip'},defs);el('rect',{x:16,y:85,width:568,height:468},clip);const g=el('g',{'clip-path':`url(#${id}-clip)`},svg);el('rect',{x:16,y:85,width:568,height:468,fill:'#f1f5f0'},g);
  if(regional){el('path',{d:path(region.states),fill:'#ebf0e9',stroke:'#b9c1b5','stroke-width':1},g);el('path',{d:path(region.rivers),stroke:'#aacbd0','stroke-width':2,fill:'none'},g);}else{mainz.land.forEach(l=>el('path',{d:path(l.geometry),fill:'#e1e3d6','fill-rule':'evenodd'},g));el('path',{d:path(mainz.water),fill:'#c3dadd','fill-rule':'evenodd'},g);el('path',{d:path(mainz.roads),stroke:'white','stroke-width':1,fill:'none'},g);}
  const marks=el('g',{class:'data-symbols'},g),names=el('g',{},g),nodes=points.map((p,i)=>{const n=el('path',{class:'data-symbol'},marks);const tt=el('title',{},n);tt.textContent=kind==='quantitative'?`${p.name}\n${num(p.population)} Einwohner · 31.12.2024\nQuelle: Statistische Ämter / Destatis`:kind==='ordinal'?`${p.name}\nRollstuhlzugang: ${labels[p.level]}\nOSM ${p.id}`:kind==='direction'?`${p.name} · DWD ${p.id}\nF: ${p.speed} m/s · Wind aus ${p.from_deg}° · Strömung nach ${p.to_deg}°\nQN_3: ${p.qn}`:`${p.name} · ${TYPES[p.category]}`;return n;});
  let cityLabelBoxes=[];
  if(kind!=='quantitative')(regional?region.cities:mainz.labels).forEach(p=>{const[x,y]=projection(regional?[p.lon,p.lat]:[p.x,p.y]);text(names,x+5,y-6,p.name,12,{'font-weight':'600','paint-order':'stroke',stroke:'#ffffff','stroke-width':3});});
  function layoutCityNames(s){
   names.replaceChildren();const projected=points.map(p=>{const[x,y]=projection([p.lon,p.lat]),r=Math.sqrt(area(p,s)/Math.PI)*(s.mode==='orientation'?1.8:1.2);return{...p,x,y,r};}),obstacles=projected.map(p=>({x:p.x-p.r-2,y:p.y-p.r-2,w:2*p.r+4,h:2*p.r+4}));
   const items=projected.map(p=>{const label=p.name.replace(' am Main','').replace(' am Rhein','').replace(' an der Weinstraße',' a. d. W.');return{...p,label,w:label.length*7+8,h:19};});
   const placed=placeLabels(items,obstacles,[{x:495,y:87,w:87,h:107},{x:26,y:518,w:110,h:36}],{x:20,y:90,w:560,h:458});cityLabelBoxes=placed.map(p=>p.rect);
   for(const p of placed){const r=p.rect,ex=Math.max(r.x,Math.min(r.x+r.w,p.x)),ey=Math.max(r.y,Math.min(r.y+r.h,p.y)),d=Math.hypot(ex-p.x,ey-p.y);if(d>p.r+9)el('path',{class:'city-leader',d:`M${p.x+(ex-p.x)*p.r/d},${p.y+(ey-p.y)*p.r/d}L${ex},${ey}`,stroke:'#839a90','stroke-width':.7,fill:'none'},names);}
   for(const p of placed)text(names,p.rect.x+4,p.rect.y+14,p.label,12,{class:'city-label','data-city':p.name,'font-weight':'600','paint-order':'stroke',stroke:'#ffffff','stroke-width':3});
  }
  const pats=Array.from({length:points.length+8},(_,i)=>el('pattern',{id:id+'-pat'+i,patternUnits:'userSpaceOnUse',width:8,height:8},defs));
  const legend=el('g',{class:'map-legend'},svg);drawLocator(d3,svg,mainz);
  const scaleWidth=regional?projection([8.27+20/(111.195*Math.cos(50*Math.PI/180)),50])[0]-projection([8.27,50])[0]:projection.scale()*1000;el('path',{d:`M30,531v6h${scaleWidth}v-6`,fill:'none',stroke:'#455e56','stroke-width':1},g);text(g,30,550,regional?'20 km':'1 km',12);
  text(svg,560,573,'N ↑',13);text(svg,16,653,kind==='direction'?'© Deutscher Wetterdienst · CC BY 4.0 · 26 Messstationen':kind==='quantitative'?'© Statistische Ämter des Bundes und der Länder / Destatis, 2026':'© OpenStreetMap contributors · ODbL · Stand 30.10.2026',12);text(svg,16,671,kind==='direction'?'Momentaufnahme · keine Interpolation · Natural Earth: Public Domain':kind==='quantitative'?'Bevölkerung 31.12.2024 · Gebietsstand 31.03.2026 · Natural Earth':kind==='ordinal'?'Nur Orte mit Zugangsangabe · fehlende Angaben sind keine Verneinung.':'Quellen und Datenhinweise unter der Karte.',11);
  const hues=kind==='ordinal'?['#7b51a5','#e78b36','#328f90','#c34e68']:['#246a7b','#ba633e','#827438','#806180'];
  const shapeSets={geometric:[d3.symbolCircle,d3.symbolSquare,d3.symbolTriangle,d3.symbolDiamond],distinct:[d3.symbolCircle,d3.symbolStar,d3.symbolCross,d3.symbolWye]};
  function color(p,s){if(s.mode==='value'||(s.combine&&s.mode==='size'))return toneColor(d3,s.valueFamily,s.lightHigh-(s.lightHigh-s.lightLow)*(s.reverseValue?1-norm(p):norm(p)));if(s.mode==='hue'||(s.combine&&s.mode==='form'))return kind==='quantitative'?d3.interpolateRainbow(norm(p)*.9):s.palette==='bright'?d3.schemeTableau10[value(p)]:hues[value(p)];return '#356e74';}
  function shape(p,s){const v=Math.max(0,Math.min(3,Math.floor(norm(p)*3.999)));return s.mode==='form'||(s.combine&&s.mode==='hue')?shapeSets[s.formSet||'geometric'][v]:s.shape==='square'?d3.symbolSquare:d3.symbolCircle;}
  function area(p,s){return (s.mode==='size'||(s.combine&&s.mode==='value'))?(kind==='quantitative'?symbolArea(p.population,max,s.size):Math.PI*s.size*s.size*(.18+.82*norm(p))):Math.PI*s.size*s.size;}
  function pattern(p,s,index){const q=pats[index],gap=kind==='nominal'?s.texture:Math.max(3,s.texture*(1-.6*norm(p)));q.setAttribute('width',gap);q.setAttribute('height',gap);q.replaceChildren();el('rect',{width:gap,height:gap,fill:'#ffffff'},q);const stroke='#356e74';if(kind==='nominal'&&value(p)===1)el('circle',{cx:gap/2,cy:gap/2,r:gap*.21,fill:stroke},q);else el('path',{d:kind==='nominal'&&value(p)===2?`M0,${gap/2}H${gap}M${gap/2},0V${gap}`:kind==='nominal'&&value(p)===3?`M0,0L${gap},${gap}`:`M0,${gap/2}H${gap}`,stroke,'stroke-width':gap*.23},q);return`url(#${id}-pat${index})`;}
  function drawPoint(n,p,s,index,x,y){n.setAttribute('d',s.mode==='orientation'?arrowPath(area(p,s)):d3.symbol().type(shape(p,s)).size(area(p,s))());n.setAttribute('transform',`translate(${x},${y}) rotate(${s.mode==='orientation'?s.angle+norm(p)*180:0})`);n.setAttribute('fill',s.mode==='texture'?pattern(p,s,index):color(p,s));n.setAttribute('stroke','#ffffff');n.setAttribute('stroke-width',1);}
  function windPoint(n,p,s,x,y,index=0){
   const sector=Math.floor(((p.from_deg+22.5)%360)/45),t=(p.from_deg%360)/360,oriented=s.mode==='orientation',length=(s.speed?s.speedSize:s.size)*(s.speed?Math.sqrt(p.speed/max):1),h=length/2;
   let d,fill=s.ink,stroke='#ffffff',width=1;
   if(oriented){d=s.symbol==='circle'?d3.symbol().type(d3.symbolCircle).size(Math.PI*(length*.35)**2)():s.symbol==='axis'?`M0,${h}V${-h}`:arrowPath(length*length*.418);if(s.symbol==='axis'){fill='none';stroke=s.ink;width=2.7;}}
   else if(s.mode==='form'){const shapes=[d3.symbolCircle,d3.symbolSquare,d3.symbolTriangle,d3.symbolDiamond,d3.symbolStar,d3.symbolCross,d3.symbolWye];d=sector===7?arrowPath(Math.PI*(s.size*.35)**2):d3.symbol().type(shapes[sector]).size(Math.PI*(s.size*.35)**2)();}
   else{const r=s.size*.35*(s.mode==='size'?Math.sqrt(.1+.9*t):1);d=d3.symbol().type(d3.symbolCircle).size(Math.PI*r*r)();}
   if(s.mode==='hue')fill=d3.schemeTableau10[sector];if(s.mode==='value')fill=toneColor(d3,s.valueFamily,s.lightHigh-(s.lightHigh-s.lightLow)*(s.reverseValue?1-t:t));
   if(s.mode==='texture'){const q=pats[index],gap=Math.max(3,s.texture*(1-.6*t));q.replaceChildren();q.setAttribute('width',gap);q.setAttribute('height',gap);el('rect',{width:gap,height:gap,fill:'white'},q);el('path',{d:`M0,${gap/2}H${gap}`,stroke:s.ink,'stroke-width':gap*.23},q);fill=`url(#${id}-pat${index})`;}
   n.setAttribute('d',d);n.setAttribute('transform',`translate(${x},${y}) rotate(${oriented&&s.encode?flowTo(p.from_deg):0})`);n.setAttribute('fill',fill);n.setAttribute('stroke',stroke);n.setAttribute('stroke-width',width);n.setAttribute('stroke-linecap','round');n.setAttribute('stroke-linejoin','round');
  }
  function update(s){if(s.mode!=='texture')pats.forEach(p=>{p.replaceChildren();p.setAttribute('width',8);p.setAttribute('height',8);});names.setAttribute('display',s.names?'':'none');if(kind==='quantitative')layoutCityNames(s);nodes.forEach((n,i)=>{const p=points[i],[x,y]=projection(regional?[p.lon,p.lat]:[p.x,p.y]);if(kind==='direction')windPoint(n,p,s,x,y,i);else drawPoint(n,p,s,i,x,y);});legend.replaceChildren();
   if(kind==='direction'){
    if(s.mode==='orientation'){
     text(legend,16,578,'DWD: Windherkunft · Rotation zeigt hier die Zielrichtung der Luft',12,{'font-weight':'bold'});
     if(s.speed){[Math.min(...points.map(p=>p.speed)),max].forEach((f,i)=>{const n=el('path',{},legend);windPoint(n,{from_deg:180,speed:f},s,40+i*260,605,points.length+i);text(legend,80+i*260,609,`${f.toFixed(1)} m/s`,13);});text(legend,16,639,'Zusatzvariable Größe: Pfeilfläche proportional zur Windgeschwindigkeit.',11);}
     else{text(legend,16,606,s.encode?(s.symbol==='arrow'?'Pfeilspitze = Zielrichtung der Luft':'Ausrichtung = DWD-Windherkunft + 180°'):'Einheitliche Ausrichtung',13);text(legend,16,629,'Windgeschwindigkeit: Tooltip und Datentabelle',11);}
    }else{
     text(legend,16,578,'DWD-Windherkunft · Richtungscodes',13,{'font-weight':'bold'});
     ['N','NO','O','SO','S','SW','W','NW'].forEach((lab,i)=>{const n=el('path',{},legend);windPoint(n,{from_deg:i*45||360,speed:max},s,34+i*70,602,points.length+i);text(legend,34+i*70,630,`${lab} ${i*45}°`,11,{'text-anchor':'middle'});});
    }
   }else{
    text(legend,16,577,kind==='nominal'?'Einrichtungstyp':kind==='ordinal'?'Rollstuhlzugang laut OSM':'Einwohner je Gemeinde',13,{'font-weight':'bold'});
    const examples=kind==='quantitative'?[min,100000,250000,max].map(population=>({population})):labels.map((_,i)=>kind==='nominal'?{category:i}:{level:i});
    examples.forEach((p,i)=>{const x=31+i*(572/examples.length),n=el('path',{},legend),old=s.size,ls={...s,size:old};drawPoint(n,p,ls,points.length+i,x,600);text(legend,x+27,605,kind==='quantitative'?num(p.population):labels[i],kind==='nominal'?11:12);});
    text(legend,16,637,kind==='quantitative'?'Einwohnerzahlen für das gesamte Gemeindegebiet.':kind==='ordinal'?'Die Angaben beziehen sich auf Rollstuhlzugang, nicht auf alle Aspekte der Barrierefreiheit.':'Legende: Einrichtungstypen laut OSM.',11);
   }
  }return {svg,update,labelBoxes:()=>cityLabelBoxes};
 }
 const left=build('map-left'),right=build('map-right');left.update(bad);
 let pending=false;
 function render(){pending=false;
  if(kind==='direction'){
   const available=state.mode==='orientation'&&state.symbol==='arrow';if(!available)state.speed=false;document.getElementById('speed').disabled=!available;document.getElementById('wind-combo-details').hidden=!state.speed;document.getElementById('common-size').hidden=state.speed;
   document.querySelectorAll('[data-wind-modes]').forEach(n=>n.hidden=!n.dataset.windModes.split(' ').includes(state.mode));
  }else{
   const allowed=kind==='nominal'?['hue','form']:['size','value'];if(!allowed.includes(state.mode))state.combine=false;document.getElementById('combine').disabled=!allowed.includes(state.mode);
   const extra={hue:'form',form:'hue',size:'value',value:'size'}[state.mode],titles={form:'Form',hue:'Farbton',value:'Helligkeit / Tonwert',size:'Größe'};document.getElementById('combo-details').hidden=!state.combine;document.getElementById('combo-title').textContent=state.combine?'Zusatzvariable: '+titles[extra]:'';
   for(const k of ['form','hue','value','size'])document.getElementById('combo-'+k).hidden=!state.combine||extra!==k;
   document.getElementById('common-size').hidden=state.combine&&state.mode==='value';
   for(const n of document.querySelectorAll('[data-modes]'))n.hidden=(kind==='quantitative'&&n.querySelector('h3')?.textContent==='Farbtöne')||!n.dataset.modes.split(' ').includes(state.mode);
  }
  right.update(state);
  for(const n of document.querySelectorAll('[data-key]')){if(n.type==='checkbox')n.checked=!!state[n.dataset.key];else n.value=state[n.dataset.key];const o=document.getElementById(n.id+'-value');if(o)o.value=n.value;}
 }
 const change=n=>{state[n.dataset.key]=n.type==='checkbox'?n.checked:n.type==='range'?+n.value:n.value;if(n.dataset.key==='mode'){state.combine=false;if(kind==='direction'){state.speed=false;if(state.mode==='orientation'){state.symbol='arrow';state.encode=true;}}}if(n.dataset.key==='symbol'&&state.symbol!=='arrow')state.speed=false;if(!pending){pending=true;requestAnimationFrame(render);}};
 document.querySelectorAll('[data-key]').forEach(n=>{n.addEventListener('input',()=>change(n));n.addEventListener('change',()=>change(n));});document.getElementById('reset').onclick=()=>{Object.assign(state,bad);render();};exportButtons(right.svg,'Mainz_'+kind);render();document.body.classList.remove('is-loading');document.getElementById('load-message').hidden=true;
 if(kind!=='nominal'){const table=document.querySelector('.data-table'),headers=kind==='direction'?['Station','F (m/s)','Wind aus (°)','Strömung nach (°)']:kind==='quantitative'?['Stadt','Einwohner','Stichtag']:['Ort','Rollstuhlzugang','OSM-ID'];const summary=document.createElement('summary');summary.textContent='Verwendete Daten ansehen';const t=document.createElement('table'),head=document.createElement('thead'),hr=document.createElement('tr');for(const v of headers){const th=document.createElement('th');th.textContent=v;hr.append(th);}head.append(hr);t.append(head);const body=document.createElement('tbody');for(const p of points){const tr=document.createElement('tr'),values=kind==='direction'?[p.name,p.speed,p.from_deg,p.to_deg]:kind==='quantitative'?[p.name,num(p.population),'31.12.2024']:[p.name,labels[p.level],p.id];for(const v of values){const td=document.createElement('td');td.textContent=v;tr.append(td);}body.append(tr);}t.append(body);table.replaceChildren(summary,t);}

 return{left,right,state};
}
if(!globalThis.KARTO_TEST)start().catch(e=>{document.getElementById('load-message').textContent=e.message;console.error(e);});
