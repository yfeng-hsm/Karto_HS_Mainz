import {setupLayout,drawLocator} from './ui.mjs?v=11';
import {classify,BERTIN_BAD,COLOR_BAD,categorySize,categoryLight} from './core.mjs?v=10';
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs={},parent){const n=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);if(parent)parent.append(n);return n;}
function txt(parent,x,y,text,size=11,extra={}){const n=el('text',{x,y,'font-size':size,fill:'#293c38','font-family':'Arial, sans-serif',...extra},parent);n.textContent=text;return n;}
const types=['Schulen','Kindertagesstätten','Bibliotheken','Sportzentren'];
export async function start(){
 const d3=globalThis.d3,kind=document.body.dataset.lab;if(!kind)return;
 setupLayout(kind);
 const response=await fetch('data/mainz.json');if(!response.ok)throw Error('Kartendaten konnten nicht geladen werden.');const data=await response.json();
 const bad=kind==='bertin'?BERTIN_BAD:COLOR_BAD,state={...bad},values=data.population.map(d=>d.value);
 function build(id){
  const svg=document.getElementById(id),defs=el('defs',{},svg);el('rect',{width:600,height:680,fill:'#ffffff'},svg);

  txt(svg,16,37,kind==='bertin'?'Einrichtungen im Stadtraum':'Wie viele Menschen wohnen hier?',21,{'font-family':'Arial, sans-serif','font-weight':'bold'});
  const subtitle=txt(svg,16,60,kind==='bertin'?'Vier Einrichtungstypen · Innenstadt und Umgebung':'Bevölkerung je 100 × 100 m · Zensus 2022',11);
  const mapBottom=kind==='color'?464:574;const view=data.views[kind==='bertin'?'bertin':'color'];const projection=d3.geoIdentity().reflectY(true).fitExtent([[16,77],[584,mapBottom]],{type:'LineString',coordinates:[[view[0],view[2]],[view[1],view[3]]]});const path=d3.geoPath(projection);
  const clip=el('clipPath',{id:id+'-clip'},defs);el('rect',{x:16,y:77,width:568,height:mapBottom-77},clip);
  const g=el('g',{'clip-path':`url(#${id}-clip)`},svg);el('rect',{x:16,y:77,width:568,height:mapBottom-77,fill:'#f1f0e8'},g);
  const land=el('g',{},g),patterns=[];
  data.land.forEach((l,i)=>{const p=el('pattern',{id:id+'-p'+i,patternUnits:'userSpaceOnUse',width:8,height:8,patternTransform:`rotate(${i*25})`},defs);el('path',{d:i%2?'M0,0L8,8M-4,4L4,12M4,-4L12,4':'M0,0V8',stroke:'#888c7a','stroke-width':.8},p);patterns.push(p);el('path',{d:path(l.geometry),fill:`url(#${id}-p${i})`,'fill-rule':'evenodd'},land);});
  el('path',{d:path(data.water),fill:'#c4dadd','fill-rule':'evenodd'},g);const roads=el('path',{d:path(data.roads),stroke:'#ffffff','stroke-width':1,fill:'none'},g);
  el('path',{d:path(data.boundary),stroke:'#9caa9e','stroke-width':.6,fill:'none'},g);
  const marks=el('g',{},g),labelGroup=el('g',{},g);let nodes=[];
  if(kind==='bertin')nodes=data.pois.map(p=>{const n=el('path',{},marks);el('title',{},n).textContent=p.name+' · '+types[p.category];return n;});
  else nodes=data.population.map(p=>{const n=el('path',{d:path(p.geometry),'fill-rule':'evenodd'},marks);el('title',{},n).textContent=p.value+' Einwohner · '+p.id;return n;});
  data.labels.forEach(l=>{const[x,y]=projection([l.x,l.y]);txt(labelGroup,x,y,l.name,12,{'letter-spacing':1,'paint-order':'stroke',stroke:'#ffffff','stroke-width':2,'text-anchor':'middle'});});
  drawLocator(d3,svg,data);
  const legend=el('g',{},svg),stats=el('g',{'class':'histogram'},svg);
  const distance=kind==='bertin'?1000:2000,scale=projection.scale()*distance;el('path',{d:`M16,623v5h${scale}v-5`,stroke:'#293c38',fill:'none'},svg);txt(svg,16,639,(distance/1000)+' km',10);txt(svg,565,637,'N ↑',11);
  txt(svg,16,654,'© OpenStreetMap contributors · Kartenhintergrund vereinfacht',12);txt(svg,16,666,kind==='bertin'?'OSM: 24.10.2026 · Typen, keine Kapazitäten oder Qualitätswerte':'Zensus: 15.05.2022 · Fehlende/unterdrückte Werte sind nicht null',12);
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
    nodes.forEach((n,i)=>{const p=data.pois[i],[x,y]=projection([p.x,p.y]);n.setAttribute('d',symbol(p.category));n.setAttribute('transform',`translate(${x},${y}) rotate(${s.angle+(s.directions?p.category*35:0)})`);n.setAttribute('fill',symbolFill(p.category));n.setAttribute('stroke','#ffffff');n.setAttribute('stroke-width',.6);});
    types.forEach((name,i)=>{el('path',{d:symbol(i),transform:`translate(${26+i*143},597) rotate(${s.angle+(s.directions?i*35:0)})`,fill:symbolFill(i)},legend);txt(legend,39+i*143,600,name,9);});

   }else{
    land.setAttribute('opacity',.12);const c=classify(values,s.method,s.classes),k=c.bins.length;
    const ramps={warm:d3.interpolateYlOrRd,blue:d3.interpolateBlues,green:d3.interpolateGreens,purple:d3.interpolatePurples,viridis:d3.interpolateViridis,diverging:d3.interpolateRdBu};
    let colors=Array.from({length:k},(_,i)=>s.palette==='category'?d3.schemeTableau10[i]:ramps[s.palette](.52+((.12+.82*i/Math.max(1,k-1))-.52)*s.contrast));if(s.reverse)colors.reverse();
    if(s.gray)colors=colors.map(v=>{const c=d3.rgb(v),l=Math.round(.2126*c.r+.7152*c.g+.0722*c.b);return `rgb(${l},${l},${l})`;});
    const forms=[d3.symbolCircle,d3.symbolSquare,d3.symbolTriangle,d3.symbolDiamond,d3.symbolCross,d3.symbolStar,d3.symbolWye];
    const shapeFor=i=>s.classShapes?forms[i%forms.length]:({circle:d3.symbolCircle,square:d3.symbolSquare,triangle:d3.symbolTriangle,diamond:d3.symbolDiamond}[s.symbolForm]||d3.symbolCircle);
    const shapePath=i=>d3.symbol().type(shapeFor(i)).size(Math.PI*s.symbolSize*s.symbolSize)();
    nodes.forEach((n,i)=>{const cell=data.population[i],symbol=s.symbolForm!=='none';n.setAttribute('class','population-cell');n.setAttribute('d',symbol?shapePath(c.ids[i]):path(cell.geometry));if(symbol){const [x,y]=path.centroid(cell.geometry);n.setAttribute('transform',`translate(${x},${y})`);}else n.removeAttribute('transform');n.setAttribute('fill',colors[c.ids[i]]);n.setAttribute('stroke','#ffffff');n.setAttribute('stroke-width',s.border);});
    // Equal-width bins retain the numerical distribution; class boundaries use the same numeric x-scale.
    txt(stats,18,483,'VERTEILUNG · Personen je 100 × 100 m',11,{'font-weight':'bold'});
    txt(stats,580,483,s.logCounts?'Häufigkeit (log₁₀(1+n))':'Häufigkeit (Zellen)',10,{'text-anchor':'end'});
    const xmin=Math.min(...values),xmax=Math.max(...values),x=d3.scaleLinear().domain([xmin,xmax]).range([42,578]);
    const hist=d3.bin().domain([xmin,xmax]).thresholds(d3.range(1,33).map(i=>xmin+(xmax-xmin)*i/33))(values);
    const transform=n=>s.logCounts?Math.log10(1+n):n, ymax=d3.max(hist,b=>transform(b.length));
    const y=d3.scaleLinear().domain([0,ymax]).range([553,493]);
    hist.forEach(b=>{const cls=c.bins.findIndex(v=>(b.x0+b.x1)/2<=v);const bar=el('rect',{x:x(b.x0),y:y(transform(b.length)),width:Math.max(.5,x(b.x1)-x(b.x0)-.6),height:553-y(transform(b.length)),fill:colors[Math.max(0,cls)]},stats);el('title',{},bar).textContent=`${Math.ceil(b.x0)}–${Math.floor(b.x1)} Personen: ${b.length} Zellen`;});
    el('path',{d:'M42,493V553H578',stroke:'#7a8983',fill:'none'},stats);
    [0,ymax].forEach(v=>txt(stats,37,y(v)+3,s.logCounts?v.toFixed(1):Math.round(v),9,{'text-anchor':'end'}));
    x.ticks(5).forEach(v=>{txt(stats,x(v),567,v,10,{'text-anchor':'middle'});});
    c.bins.slice(0,-1).forEach(v=>{const line=el('line',{'class':'class-boundary',x1:x(v),x2:x(v),y1:490,y2:553,stroke:'#203a37','stroke-width':1.3,'stroke-dasharray':'3 2'},stats);el('title',{},line).textContent=`Klassengrenze: ${Number(v.toFixed(2))}`;});

    c.bins.forEach((b,i)=>{const x=18+i*(565/k);if(s.symbolForm==='none')el('rect',{x,y:587,width:12,height:12,fill:colors[i]},legend);else el('path',{d:shapePath(i),transform:`translate(${x+6},593)`,fill:colors[i]},legend);const low=i?Math.floor(c.bins[i-1])+1:Math.min(...values);txt(legend,x+16,597,`${low}–${Math.floor(b)}`,13);txt(legend,x+16,614,`${c.counts[i]} Zellen`,10,{fill:'#7b817b'});});
    subtitle.textContent=`100 × 100 m · ${s.method==='equal'?'Gleiche Intervalle':s.method==='jenks'?'Jenks / natürliche Grenzen':'Quantile'} · ${k} Klassen`;

   }
  }return{svg,update};
 }
 const left=build('map-left'),right=build('map-right');left.update(bad);
 let queued=false;function render(){queued=false;right.update(state);document.querySelectorAll('[data-key]').forEach(n=>{if(n.type==='checkbox')n.checked=state[n.dataset.key];else n.value=state[n.dataset.key];const out=document.getElementById(n.id+'-value');if(out)out.value=n.value;});if(kind==='bertin'){document.getElementById('density').disabled=!state.texture;document.getElementById('palette').disabled=state.valueOnly;}if(kind==='color'){document.getElementById('contrast').disabled=state.palette==='category';document.getElementById('shape-options').hidden=state.symbolForm==='none';}}
 document.querySelectorAll('[data-key]').forEach(n=>{const onChange=()=>{state[n.dataset.key]=n.type==='checkbox'?n.checked:n.type==='range'?+n.value:n.value;if(!queued){queued=true;requestAnimationFrame(render);}};n.addEventListener('input',onChange);n.addEventListener('change',onChange);});
 document.getElementById('reset').onclick=()=>{Object.assign(state,bad);render();};
 function download(blob,ext){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=`Mainz_${kind}.${ext}`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const serialize=()=>new XMLSerializer().serializeToString(right.svg);
 document.getElementById('export-svg').onclick=()=>download(new Blob([serialize()],{type:'image/svg+xml'}),'svg');
 document.getElementById('export-png').onclick=()=>{const img=new Image(),url=URL.createObjectURL(new Blob([serialize()],{type:'image/svg+xml'}));img.onload=()=>{const canvas=document.createElement('canvas');canvas.width=1800;canvas.height=2040;canvas.getContext('2d').drawImage(img,0,0,1800,2040);canvas.toBlob(b=>download(b,'png'));URL.revokeObjectURL(url);};img.src=url;};
 render();document.body.classList.remove('is-loading');document.getElementById('load-message').hidden=true;return{state,left,right};
}
if(!globalThis.KARTO_TEST)start().catch(e=>{document.getElementById('load-message').textContent=e.message;console.error(e);});
