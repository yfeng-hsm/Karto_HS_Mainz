import {classify,BERTIN_BAD,COLOR_BAD,categorySize,categoryLight} from './core.mjs';
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs={},parent){const n=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);if(parent)parent.append(n);return n;}
function txt(parent,x,y,text,size=11,extra={}){const n=el('text',{x,y,'font-size':size,fill:'#293c38','font-family':'Arial, sans-serif',...extra},parent);n.textContent=text;return n;}
const types=['Schulen','Kindertagesstätten','Bibliotheken','Sportzentren'];
export async function start(){
 const d3=globalThis.d3,kind=document.body.dataset.lab;if(!kind)return;
 const response=await fetch('data/mainz.json');if(!response.ok)throw Error('Kartendaten konnten nicht geladen werden.');const data=await response.json();
 const bad=kind==='bertin'?BERTIN_BAD:COLOR_BAD,state={...bad},values=data.population.map(d=>d.value);
 function build(id){
  const svg=document.getElementById(id),defs=el('defs',{},svg);el('rect',{width:600,height:680,fill:'#fffdf7'},svg);
  el('rect',{x:22,y:23,width:7,height:26,fill:'#efc54a'},svg);txt(svg,39,34,'MAINZ  /  KARTOGRAPHISCHES LABOR',10,{'font-weight':'bold','letter-spacing':1});
  txt(svg,22,71,kind==='bertin'?'Einrichtungen im Stadtraum':'Wie viele Menschen wohnen hier?',25,{'font-family':'Georgia, serif','font-weight':'bold'});
  const subtitle=txt(svg,22,95,kind==='bertin'?'Vier Einrichtungstypen · Innenstadt und Umgebung':'Bevölkerung je 100 × 100 m · Zensus 2022',11);
  const view=data.views[kind==='bertin'?'bertin':'color'];const projection=d3.geoIdentity().reflectY(true).fitExtent([[22,122],[426,575]],{type:'LineString',coordinates:[[view[0],view[2]],[view[1],view[3]]]});const path=d3.geoPath(projection);
  const clip=el('clipPath',{id:id+'-clip'},defs);el('rect',{x:22,y:122,width:404,height:453},clip);
  const g=el('g',{'clip-path':`url(#${id}-clip)`},svg);el('rect',{x:22,y:122,width:404,height:453,fill:'#f1f0e8'},g);
  const land=el('g',{},g),patterns=[];
  data.land.forEach((l,i)=>{const p=el('pattern',{id:id+'-p'+i,patternUnits:'userSpaceOnUse',width:8,height:8,patternTransform:`rotate(${i*25})`},defs);el('path',{d:i%2?'M0,0L8,8M-4,4L4,12M4,-4L12,4':'M0,0V8',stroke:'#888c7a','stroke-width':.8},p);patterns.push(p);el('path',{d:path(l.geometry),fill:`url(#${id}-p${i})`,'fill-rule':'evenodd'},land);});
  el('path',{d:path(data.water),fill:'#c4dadd','fill-rule':'evenodd'},g);const roads=el('path',{d:path(data.roads),stroke:'#ffffff','stroke-width':1,fill:'none'},g);
  el('path',{d:path(data.boundary),stroke:'#9caa9e','stroke-width':.6,fill:'none'},g);
  const marks=el('g',{},g),labelGroup=el('g',{},g);let nodes=[];
  if(kind==='bertin')nodes=data.pois.map(p=>{const n=el('path',{},marks);el('title',{},n).textContent=p.name+' · '+types[p.category];return n;});
  else nodes=data.population.map(p=>{const n=el('path',{d:path(p.geometry),'fill-rule':'evenodd'},marks);el('title',{},n).textContent=p.value+' Einwohner · '+p.id;return n;});
  data.labels.forEach(l=>{const[x,y]=projection([l.x,l.y]);txt(labelGroup,x,y,l.name,8,{'letter-spacing':1,'paint-order':'stroke',stroke:'#fffdf7','stroke-width':2,'text-anchor':'middle'});});
  const gp=d3.geoIdentity().reflectY(true).fitExtent([[461,143],[569,256]],data.germany);el('path',{d:d3.geoPath(gp)(data.germany),fill:'#e3e3d9',stroke:'#a6b2a8','stroke-width':.7},svg);const[dx,dy]=gp(data.mainz);el('circle',{cx:dx,cy:dy,r:3,fill:'#c75538',stroke:'white'},svg);txt(svg,dx+5,dy+3,'Mainz',9);txt(svg,451,132,'DEUTSCHLAND',9,{'font-weight':'bold','letter-spacing':1});
  txt(svg,451,288,'LEGENDE',10,{'font-weight':'bold','letter-spacing':1});const legend=el('g',{},svg),stats=el('g',{},svg);
  const distance=kind==='bertin'?1000:2000,scale=projection.scale()*distance;el('path',{d:`M22,591v5h${scale}v-5`,stroke:'#293c38',fill:'none'},svg);txt(svg,22,612,(distance/1000)+' km',10);txt(svg,413,603,'N ↑',11);
  txt(svg,22,640,'© OpenStreetMap contributors · Kartenhintergrund vereinfacht',8);txt(svg,22,654,kind==='bertin'?'OSM: 24.10.2026 · Typen, keine Kapazitäten oder Qualitätswerte':'Zensus: 15.05.2022 · Fehlende/unterdrückte Werte sind nicht null',8);txt(svg,22,668,'HS MAINZ  ·  DIGITALE KARTOGRAPHIE',8,{'letter-spacing':1});
  function update(s){
   labelGroup.setAttribute('display',s.names?'':'none');legend.replaceChildren();stats.replaceChildren();
   if(kind==='bertin'){
    land.setAttribute('opacity',s.texture?s.background:.18*s.background);roads.setAttribute('opacity',Math.max(.2,s.background));
    patterns.forEach(p=>{p.setAttribute('width',12-s.density*2);p.setAttribute('height',12-s.density*2);});
    [...land.children].forEach((n,i)=>n.setAttribute('fill',s.texture?`url(#${id}-p${i})`:'#c6c9bc'));
    const palette=s.palette==='bright'?['#ed04c8','#00cb69','#4932ed','#f78c00']:s.palette==='single'?Array(4).fill('#326b78'):['#246a7b','#ba633e','#83723e','#7a6284'];
    const color=i=>{const c=d3.hsl(palette[i]);c.l=categoryLight(s,i);return c.formatHex();};
    const symbol=i=>d3.symbol().type(s.form==='circle'?d3.symbolCircle:s.form==='triangle'?d3.symbolTriangle:[d3.symbolCircle,d3.symbolSquare,d3.symbolTriangle,d3.symbolDiamond][i]).size(categorySize(s,i))();
    nodes.forEach((n,i)=>{const p=data.pois[i],[x,y]=projection([p.x,p.y]);n.setAttribute('d',symbol(p.category));n.setAttribute('transform',`translate(${x},${y}) rotate(${s.angle+(s.directions?p.category*35:0)})`);n.setAttribute('fill',color(p.category));n.setAttribute('stroke','#fffdf7');n.setAttribute('stroke-width',.6);});
    types.forEach((name,i)=>{el('path',{d:symbol(i),transform:`translate(458,${317+i*38}) rotate(${s.angle+(s.directions?i*35:0)})`,fill:color(i)},legend);txt(legend,473,321+i*38,name,9);});
    txt(legend,451,489,'Stadtflächen',9,{'font-weight':'bold'});data.land.slice(0,4).forEach((l,i)=>{el('rect',{x:451,y:502+i*18,width:12,height:12,fill:s.texture?`url(#${id}-p${i})`:'#c6c9bc'},legend);txt(legend,469,512+i*18,l.category,8);});
   }else{
    land.setAttribute('opacity',.12);const c=classify(values,s.method,s.classes),k=c.bins.length;
    const ramps={warm:d3.interpolateYlOrRd,blue:d3.interpolateBlues,viridis:d3.interpolateViridis,diverging:d3.interpolateRdBu};
    let colors=Array.from({length:k},(_,i)=>s.palette==='category'?d3.schemeTableau10[i]:ramps[s.palette](.52+((.12+.82*i/Math.max(1,k-1))-.52)*s.contrast));if(s.reverse)colors.reverse();
    if(s.gray)colors=colors.map(v=>{const c=d3.rgb(v),l=Math.round(.2126*c.r+.7152*c.g+.0722*c.b);return `rgb(${l},${l},${l})`;});
    nodes.forEach((n,i)=>{n.setAttribute('fill',colors[c.ids[i]]);n.setAttribute('stroke','#fffdf7');n.setAttribute('stroke-width',s.border);});
    txt(legend,451,309,'Einwohner / Zelle',10);c.bins.forEach((b,i)=>{const y=329+i*26;el('rect',{x:451,y:y-11,width:14,height:14,fill:colors[i]},legend);const low=i?Math.floor(c.bins[i-1])+1:Math.min(...values);txt(legend,472,y,`${low}–${Math.floor(b)}`,10);txt(legend,472,y+10,`${c.counts[i]} Zellen`,7,{fill:'#7b817b'});});
    subtitle.textContent=`100 × 100 m · ${s.method==='equal'?'Gleiche Intervalle':s.method==='jenks'?'Jenks / natürliche Grenzen':'Quantile'} · ${k} Klassen`;
    txt(stats,451,548,'Verteilung der Werte',9);const hist=d3.bin().thresholds(20)(values),max=Math.max(...hist.map(b=>b.length));hist.forEach((b,i)=>el('rect',{x:451+i*6,y:583-b.length/max*25,width:5,height:b.length/max*25,fill:'#a5afa4'},stats));txt(stats,451,598,'3',7);txt(stats,550,598,'946',7);
   }
  }return{svg,update};
 }
 const left=build('map-left'),right=build('map-right');left.update(bad);
 let queued=false;function render(){queued=false;right.update(state);document.querySelectorAll('[data-key]').forEach(n=>{if(n.type==='checkbox')n.checked=state[n.dataset.key];else n.value=state[n.dataset.key];const out=document.getElementById(n.id+'-value');if(out)out.value=n.value;});if(kind==='bertin'){document.getElementById('density').disabled=!state.texture;document.getElementById('light').disabled=state.lightMode==='category';}document.getElementById('live-state').textContent='● Vorschau aktuell';}
 document.querySelectorAll('[data-key]').forEach(n=>n.addEventListener('input',()=>{state[n.dataset.key]=n.type==='checkbox'?n.checked:n.type==='range'?+n.value:n.value;if(!queued){queued=true;requestAnimationFrame(render);}}));
 document.getElementById('reset').onclick=()=>{Object.assign(state,bad);render();};
 function download(blob,ext){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=`Mainz_${kind}.${ext}`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const serialize=()=>new XMLSerializer().serializeToString(right.svg);
 document.getElementById('export-svg').onclick=()=>download(new Blob([serialize()],{type:'image/svg+xml'}),'svg');
 document.getElementById('export-png').onclick=()=>{const img=new Image(),url=URL.createObjectURL(new Blob([serialize()],{type:'image/svg+xml'}));img.onload=()=>{const canvas=document.createElement('canvas');canvas.width=1800;canvas.height=2040;canvas.getContext('2d').drawImage(img,0,0,1800,2040);canvas.toBlob(b=>download(b,'png'));URL.revokeObjectURL(url);};img.src=url;};
 render();document.body.classList.remove('is-loading');document.getElementById('load-message').hidden=true;return{state,left,right};
}
if(!globalThis.KARTO_TEST)start().catch(e=>{document.getElementById('load-message').textContent=e.message;console.error(e);});
