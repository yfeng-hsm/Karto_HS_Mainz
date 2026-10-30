import {classify,BERTIN_BAD,COLOR_BAD,categorySize,categoryLight} from './core.mjs?v=5';
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs={},parent){const n=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);if(parent)parent.append(n);return n;}
function txt(parent,x,y,text,size=11,extra={}){const n=el('text',{x,y,'font-size':size,fill:'#293c38','font-family':'Arial, sans-serif',...extra},parent);n.textContent=text;return n;}
const types=['Schulen','Kindertagesstätten','Bibliotheken','Sportzentren'];
export async function start(){
 const d3=globalThis.d3,kind=document.body.dataset.lab;if(!kind)return;
 // Keep the map and its controls visible together on classroom laptops.
 document.body.classList.add('compact-lab');
 document.querySelector('.controls-heading h2').textContent='Karte gestalten';
 const main=document.querySelector('main'),panel=document.querySelector('.controls-panel'),workspace=document.querySelector('.workspace');
 const stage=document.createElement('div');stage.className='lab-stage';panel.before(stage);stage.append(workspace,panel);
 const tasks=document.querySelector('.tasks'),taskDetails=document.createElement('details');taskDetails.className='task-details';
 const taskSummary=document.createElement('summary');taskSummary.textContent=kind==='bertin'?'Aufgabe: Probleme erkennen → rechts verbessern → drei Änderungen begründen':'Aufgabe: Klassifikation vergleichen → Farben wählen → Entscheidungen begründen';
 tasks.before(taskDetails);taskDetails.append(taskSummary,tasks);
 const help=document.createElement('details');help.className='help-details';const hs=document.createElement('summary');hs.textContent='Datenhinweise · Vorzeigen · Quellen';help.append(hs);
 main.append(help);for(const n of document.querySelectorAll('.note,.discussion,footer'))help.append(n);

 const response=await fetch('data/mainz.json');if(!response.ok)throw Error('Kartendaten konnten nicht geladen werden.');const data=await response.json();
 const bad=kind==='bertin'?BERTIN_BAD:COLOR_BAD,state={...bad},values=data.population.map(d=>d.value);
 function build(id){
  const svg=document.getElementById(id),defs=el('defs',{},svg);el('rect',{width:600,height:680,fill:'#fffdf7'},svg);
  el('rect',{x:16,y:12,width:5,height:22,fill:'#efc54a'},svg);txt(svg,30,23,'MAINZ  /  KARTOGRAPHISCHES LABOR',10,{'font-weight':'bold','letter-spacing':1});
  txt(svg,16,46,kind==='bertin'?'Einrichtungen im Stadtraum':'Wie viele Menschen wohnen hier?',22,{'font-family':'Georgia, serif','font-weight':'bold'});
  const subtitle=txt(svg,16,64,kind==='bertin'?'Vier Einrichtungstypen · Innenstadt und Umgebung':'Bevölkerung je 100 × 100 m · Zensus 2022',11);
  const view=data.views[kind==='bertin'?'bertin':'color'];const projection=d3.geoIdentity().reflectY(true).fitExtent([[16,77],[584,574]],{type:'LineString',coordinates:[[view[0],view[2]],[view[1],view[3]]]});const path=d3.geoPath(projection);
  const clip=el('clipPath',{id:id+'-clip'},defs);el('rect',{x:16,y:77,width:568,height:497},clip);
  const g=el('g',{'clip-path':`url(#${id}-clip)`},svg);el('rect',{x:16,y:77,width:568,height:497,fill:'#f1f0e8'},g);
  const land=el('g',{},g),patterns=[];
  data.land.forEach((l,i)=>{const p=el('pattern',{id:id+'-p'+i,patternUnits:'userSpaceOnUse',width:8,height:8,patternTransform:`rotate(${i*25})`},defs);el('path',{d:i%2?'M0,0L8,8M-4,4L4,12M4,-4L12,4':'M0,0V8',stroke:'#888c7a','stroke-width':.8},p);patterns.push(p);el('path',{d:path(l.geometry),fill:`url(#${id}-p${i})`,'fill-rule':'evenodd'},land);});
  el('path',{d:path(data.water),fill:'#c4dadd','fill-rule':'evenodd'},g);const roads=el('path',{d:path(data.roads),stroke:'#ffffff','stroke-width':1,fill:'none'},g);
  el('path',{d:path(data.boundary),stroke:'#9caa9e','stroke-width':.6,fill:'none'},g);
  const marks=el('g',{},g),labelGroup=el('g',{},g);let nodes=[];
  if(kind==='bertin')nodes=data.pois.map(p=>{const n=el('path',{},marks);el('title',{},n).textContent=p.name+' · '+types[p.category];return n;});
  else nodes=data.population.map(p=>{const n=el('path',{d:path(p.geometry),'fill-rule':'evenodd'},marks);el('title',{},n).textContent=p.value+' Einwohner · '+p.id;return n;});
  data.labels.forEach(l=>{const[x,y]=projection([l.x,l.y]);txt(labelGroup,x,y,l.name,8,{'letter-spacing':1,'paint-order':'stroke',stroke:'#fffdf7','stroke-width':2,'text-anchor':'middle'});});
  el('rect',{x:495,y:81,width:85,height:109,fill:'#fffdf7','fill-opacity':.94,rx:4},svg);const gp=d3.geoIdentity().reflectY(true).fitExtent([[508,103],[571,174]],data.germany);el('path',{d:d3.geoPath(gp)(data.germany),fill:'#e3e3d9',stroke:'#a6b2a8','stroke-width':.7},svg);const[dx,dy]=gp(data.mainz);el('circle',{cx:dx,cy:dy,r:3,fill:'#c75538',stroke:'white'},svg);txt(svg,dx+4,dy+3,'Mainz',8);txt(svg,502,94,'DEUTSCHLAND',7,{'font-weight':'bold','letter-spacing':1});
  const legend=el('g',{},svg),stats=el('g',{},svg);
  const distance=kind==='bertin'?1000:2000,scale=projection.scale()*distance;el('path',{d:`M16,623v5h${scale}v-5`,stroke:'#293c38',fill:'none'},svg);txt(svg,16,639,(distance/1000)+' km',10);txt(svg,565,637,'N ↑',11);
  txt(svg,16,654,'© OpenStreetMap contributors · Kartenhintergrund vereinfacht',8);txt(svg,16,666,kind==='bertin'?'OSM: 24.10.2026 · Typen, keine Kapazitäten oder Qualitätswerte':'Zensus: 15.05.2022 · Fehlende/unterdrückte Werte sind nicht null',8);
  function update(s){
   labelGroup.setAttribute('display',s.names?'':'none');legend.replaceChildren();stats.replaceChildren();
   if(kind==='bertin'){
    land.setAttribute('opacity',.65*s.background);roads.setAttribute('opacity',Math.max(.2,s.background));
    patterns.forEach(p=>{p.setAttribute('width',12-s.density*2);p.setAttribute('height',12-s.density*2);});
    [...land.children].forEach(n=>n.setAttribute('fill','#c6c9bc'));
    const palette=s.palette==='bright'?['#ed04c8','#00cb69','#4932ed','#f78c00']:s.palette==='single'?Array(4).fill('#326b78'):['#246a7b','#ba633e','#83723e','#7a6284'];
    const color=i=>{const c=s.valueOnly?d3.lab(50,0,0):d3.lab(palette[i]);c.l=categoryLight(s,i)*100;return c.formatHex();};
    patterns.slice(0,4).forEach((p,i)=>{const gap=12-s.density*2;p.replaceChildren();p.setAttribute('patternTransform','rotate(0)');el('rect',{width:gap,height:gap,fill:color(i)},p);const ink=d3.hsl(color(i));ink.l=Math.max(.08,ink.l-.27);if(i===1)el('circle',{cx:gap/2,cy:gap/2,r:1.1,fill:ink.formatHex()},p);else el('path',{d:i===0?`M0,${gap}L${gap},0M${-gap/2},${gap/2}L${gap/2},${-gap/2}M${gap/2},${gap*1.5}L${gap*1.5},${gap/2}`:i===2?`M0,${gap/2}H${gap}`:`M0,${gap/2}H${gap}M${gap/2},0V${gap}`,stroke:ink.formatHex(),'stroke-width':.9,fill:'none'},p);});
    const symbolFill=i=>s.texture?`url(#${id}-p${i})`:color(i);
    const symbol=i=>d3.symbol().type(s.form==='circle'?d3.symbolCircle:s.form==='triangle'?d3.symbolTriangle:[d3.symbolCircle,d3.symbolSquare,d3.symbolTriangle,d3.symbolDiamond][i]).size(categorySize(s,i))();
    nodes.forEach((n,i)=>{const p=data.pois[i],[x,y]=projection([p.x,p.y]);n.setAttribute('d',symbol(p.category));n.setAttribute('transform',`translate(${x},${y}) rotate(${s.angle+(s.directions?p.category*35:0)})`);n.setAttribute('fill',symbolFill(p.category));n.setAttribute('stroke','#fffdf7');n.setAttribute('stroke-width',.6);});
    types.forEach((name,i)=>{el('path',{d:symbol(i),transform:`translate(${26+i*143},597) rotate(${s.angle+(s.directions?i*35:0)})`,fill:symbolFill(i)},legend);txt(legend,39+i*143,600,name,9);});

   }else{
    land.setAttribute('opacity',.12);const c=classify(values,s.method,s.classes),k=c.bins.length;
    const ramps={warm:d3.interpolateYlOrRd,blue:d3.interpolateBlues,viridis:d3.interpolateViridis,diverging:d3.interpolateRdBu};
    let colors=Array.from({length:k},(_,i)=>s.palette==='category'?d3.schemeTableau10[i]:ramps[s.palette](.52+((.12+.82*i/Math.max(1,k-1))-.52)*s.contrast));if(s.reverse)colors.reverse();
    if(s.gray)colors=colors.map(v=>{const c=d3.rgb(v),l=Math.round(.2126*c.r+.7152*c.g+.0722*c.b);return `rgb(${l},${l},${l})`;});
    nodes.forEach((n,i)=>{n.setAttribute('fill',colors[c.ids[i]]);n.setAttribute('stroke','#fffdf7');n.setAttribute('stroke-width',s.border);});
    c.bins.forEach((b,i)=>{const x=18+i*(565/k);el('rect',{x,y:587,width:12,height:12,fill:colors[i]},legend);const low=i?Math.floor(c.bins[i-1])+1:Math.min(...values);txt(legend,x+16,597,`${low}–${Math.floor(b)}`,9);txt(legend,x+16,608,`${c.counts[i]} Zellen`,7,{fill:'#7b817b'});});
    subtitle.textContent=`100 × 100 m · ${s.method==='equal'?'Gleiche Intervalle':s.method==='jenks'?'Jenks / natürliche Grenzen':'Quantile'} · ${k} Klassen`;

   }
  }return{svg,update};
 }
 const left=build('map-left'),right=build('map-right');left.update(bad);
 let queued=false;function render(){queued=false;right.update(state);document.querySelectorAll('[data-key]').forEach(n=>{if(n.type==='checkbox')n.checked=state[n.dataset.key];else n.value=state[n.dataset.key];const out=document.getElementById(n.id+'-value');if(out)out.value=n.value;});if(kind==='bertin'){document.getElementById('density').disabled=!state.texture;document.getElementById('palette').disabled=state.valueOnly;}document.getElementById('live-state').textContent='● Vorschau aktuell';}
 document.querySelectorAll('[data-key]').forEach(n=>n.addEventListener('input',()=>{state[n.dataset.key]=n.type==='checkbox'?n.checked:n.type==='range'?+n.value:n.value;if(!queued){queued=true;requestAnimationFrame(render);}}));
 document.getElementById('reset').onclick=()=>{Object.assign(state,bad);render();};
 function download(blob,ext){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=`Mainz_${kind}.${ext}`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const serialize=()=>new XMLSerializer().serializeToString(right.svg);
 document.getElementById('export-svg').onclick=()=>download(new Blob([serialize()],{type:'image/svg+xml'}),'svg');
 document.getElementById('export-png').onclick=()=>{const img=new Image(),url=URL.createObjectURL(new Blob([serialize()],{type:'image/svg+xml'}));img.onload=()=>{const canvas=document.createElement('canvas');canvas.width=1800;canvas.height=2040;canvas.getContext('2d').drawImage(img,0,0,1800,2040);canvas.toBlob(b=>download(b,'png'));URL.revokeObjectURL(url);};img.src=url;};
 render();document.body.classList.remove('is-loading');document.getElementById('load-message').hidden=true;return{state,left,right};
}
if(!globalThis.KARTO_TEST)start().catch(e=>{document.getElementById('load-message').textContent=e.message;console.error(e);});
