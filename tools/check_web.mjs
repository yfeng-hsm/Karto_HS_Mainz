// NODE_PATH=/tmp/karto-test/node_modules node tools/check_web.mjs
import {createRequire} from 'node:module';import fs from 'node:fs';import assert from 'node:assert/strict';import {classify} from '../docs/assets/core.mjs';import {flowTo,speedLevel,symbolArea,toneColor} from '../docs/assets/variables-core.mjs';
const require=createRequire(import.meta.url),{JSDOM,VirtualConsole}=require('jsdom'),mainz=JSON.parse(fs.readFileSync('docs/data/mainz.json')),wind=JSON.parse(fs.readFileSync('docs/data/wind.json'));
assert.equal(flowTo(360),180);assert.equal(flowTo(90),270);assert.equal(flowTo(330),150);assert.equal(symbolArea(4,6,10)/symbolArea(2,6,10),2);assert.deepEqual([1.9,2,3.9,4,5.9,6].map(speedLevel),[0,1,1,2,2,3]);assert.equal(wind.stations.length,26);for(const p of wind.stations){assert.equal(p.to_deg,flowTo(p.from_deg));assert.equal(p.level,speedLevel(p.speed));assert(p.speed>0&&p.from_deg>0&&p.from_deg<=360);}
for(const m of ['equal','quantile','jenks'])assert.equal(classify(mainz.population.map(p=>p.value),m,5).counts.reduce((a,b)=>a+b),2982);
const access=JSON.parse(fs.readFileSync('docs/data/accessibility.json')),cities=JSON.parse(fs.readFileSync('docs/data/cities.json')),region=JSON.parse(fs.readFileSync('docs/data/region.json'));assert.equal(cities.cities.length,20);assert(cities.cities.every(p=>p.reference_date==='2024-12-31'));assert.equal(cities.cities.find(p=>p.name==='Mainz').population,224684);assert.deepEqual([...new Set(access.pois.map(p=>p.access))].sort(),['limited','no','yes']);
let referenceLocator;globalThis.KARTO_TEST=true;const vars=await import('../docs/assets/variables.mjs'),colors=await import('../docs/assets/app.mjs');
for(const[kind,file]of[['nominal','bertin'],['ordinal','ordinal'],['quantitative','quantitativ'],['direction','richtung'],['color','farben']]){
 const errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));const dom=new JSDOM(fs.readFileSync(`docs/${file}.html`,'utf8'),{runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc}),w=dom.window;w.eval(fs.readFileSync('docs/assets/d3.min.js','utf8'));Object.assign(globalThis,{document:w.document,d3:w.d3,requestAnimationFrame:w.requestAnimationFrame.bind(w),fetch:async url=>({ok:true,json:async()=>url.includes('wind.json')?wind:url.includes('accessibility')?access:url.includes('cities.json')?cities:url.includes('region.json')?region:mainz})});
 const app=await(kind==='color'?colors:vars).start(),left=app.left.svg.outerHTML,right=app.right.svg.outerHTML;
 const actualSymbols=()=>[...app.right.svg.querySelectorAll('.data-symbol')].map(n=>({d:n.getAttribute('d'),fill:n.getAttribute('fill')}));const locator=app.right.svg.querySelector('.map-locator').outerHTML;if(!referenceLocator)referenceLocator=locator;assert.equal(locator,referenceLocator);assert(!app.right.svg.textContent.includes('KARTOGRAPHISCHES LABOR'));
 const change=async(id,v,eventType='input')=>{const n=w.document.getElementById(id);if(n.type==='checkbox')n.checked=v;else n.value=v;n.dispatchEvent(new w.Event(eventType));await new Promise(r=>w.requestAnimationFrame(r));};
 if(kind==='color')await change('palette','warm');else if(kind==='direction'){for(const mode of ['hue','form','size','value','texture','orientation'])await change('mode',mode);await change('symbol','arrow');await change('encode',true);assert(app.right.svg.outerHTML.includes('rotate(150)'));}else for(const mode of ['hue','form','size','value','texture','orientation']){await change('mode',mode);assert.equal(app.state.mode,mode);assert.equal(app.state.combine,false);assert(!app.right.svg.outerHTML.includes('NaN'));}
 if(kind==='color'){
  const boundaries=()=>[...app.right.svg.querySelectorAll('.class-boundary')].map(n=>+n.getAttribute('x1'));
  assert.equal(boundaries().length,classify(mainz.population.map(p=>p.value),app.state.method,app.state.classes).bins.length-1);
  const before=boundaries();await change('method','equal');assert.notDeepEqual(boundaries(),before);
  const histBefore=app.right.svg.querySelector('.histogram').outerHTML;await change('logCounts',true);assert.notEqual(app.right.svg.querySelector('.histogram').outerHTML,histBefore);
  await change('symbolForm','circle');assert.equal(w.document.getElementById('shape-options').hidden,false);assert.equal(app.right.svg.querySelectorAll('.population-cell[transform]').length,2982);
  const mark=app.right.svg.querySelector('.population-cell').getAttribute('d');await change('symbolSize',7);assert.notEqual(app.right.svg.querySelector('.population-cell').getAttribute('d'),mark);
  await change('classShapes',true);assert(new Set([...app.right.svg.querySelectorAll('.population-cell')].map(n=>n.getAttribute('d'))).size>1);
  await change('symbolForm','none');assert.equal(app.right.svg.querySelectorAll('.population-cell[transform]').length,0);
 }
 if(kind==='direction'){
  assert.equal(actualSymbols().length,26);await change('mode','size');await change('size',12);const small=actualSymbols();await change('size',44,'change');const big=actualSymbols();assert.equal(big.filter((p,i)=>p.d!==small[i].d).length,26,'Wind map symbols must resize, not just the legend');
  await change('mode','value');await change('valueFamily','blue');const blue=actualSymbols();await change('valueFamily','orange','change');assert.equal(actualSymbols().filter((p,i)=>p.fill!==blue[i].fill).length,26,'Wind map symbols must recolor, not just the legend');
  const beforeReverse=actualSymbols();await change('reverseValue',true);assert(actualSymbols().some((p,i)=>p.fill!==beforeReverse[i].fill));
  // Every station's sector must exactly match its legend swatch (including texture geometry).
  for(const mode of ['value','texture']){
   await change('mode',mode);
   const map=[...app.right.svg.querySelectorAll('.data-symbol')],legend=[...app.right.svg.querySelectorAll('.map-legend > path')];assert.equal(legend.length,8);
   wind.stations.forEach((p,i)=>{const j=Math.floor(((p.from_deg+22.5)%360)/45);if(mode==='value')assert.equal(map[i].getAttribute('fill'),legend[j].getAttribute('fill'));else{const pattern=n=>app.right.svg.querySelector(n.getAttribute('fill').slice(4,-1));const a=pattern(map[i]),b=pattern(legend[j]);assert.equal(a.getAttribute('width'),b.getAttribute('width'));assert.equal(a.innerHTML,b.innerHTML);}});
   await change('texture',10);await change('reverseValue',false);
  }
  await change('mode','orientation');await change('ink','#246e59');assert(actualSymbols().every(p=>p.fill==='#246e59'));
  await change('windExtra','hue');assert.equal(w.document.getElementById('wind-extra-hue').hidden,false);assert(new Set(actualSymbols().map(p=>p.fill)).size>1);const comboHue=actualSymbols();await change('extraPalette','muted');assert(actualSymbols().some((p,i)=>p.fill!==comboHue[i].fill));assert.equal(w.document.getElementById('speed').disabled,true);
  await change('mode','size');const angleMarks=actualSymbols();const minStation=wind.stations.findIndex(p=>p.from_deg===240),maxStation=wind.stations.findIndex(p=>p.from_deg===350);assert.notEqual(angleMarks[minStation].d,angleMarks[maxStation].d);await change('observedRange',false);assert.notEqual(actualSymbols()[minStation].d,angleMarks[minStation].d);await change('observedRange',true);
  await change('windExtra','form');assert.equal(w.document.getElementById('wind-extra-form').hidden,false);const shapeBefore=actualSymbols();await change('extraForms','distinct');assert(actualSymbols().every((p,i)=>p.d!==shapeBefore[i].d));await change('mode','hue');assert.equal(app.state.windExtra,'none');
  await change('mode','orientation');

 }
 if(kind!=='color'&&kind!=='direction'){
  await change('mode',kind==='nominal'?'hue':'size');await change('combine',true);assert.equal(w.document.getElementById('combo-details').hidden,false);assert(w.document.getElementById('combo-title').textContent.includes(kind==='nominal'?'Form':'Helligkeit'));
  const prior=app.right.svg.outerHTML;await change(kind==='nominal'?'secondary-formSet':'secondary-valueFamily',kind==='nominal'?'distinct':'orange');assert.notEqual(app.right.svg.outerHTML,prior);
  await change('mode','value');await change('valueFamily','purple');const toneBefore=actualSymbols();await change('reverseValue',true);assert(actualSymbols().some((p,i)=>p.fill!==toneBefore[i].fill));for(const family of ['gray','blue','green','orange','purple']){const cols=[25,55,83].map(L=>w.d3.lab(toneColor(w.d3,family,L)).l);assert(cols[0]<cols[1]&&cols[1]<cols[2]);}
 }
 if(kind!=='color'){
  await change('mode','hue');const key=kind==='direction'?'windPalette':'palette';const label=w.document.querySelector(`label[for="${key}"]`);assert.equal(label.textContent,'Farbserie');const previous=actualSymbols();await change(key,kind==='direction'?'muted':'bright');assert(actualSymbols().some((p,i)=>p.fill!==previous[i].fill));
 }
 if(kind==='quantitative'){
  for(const size of [6,22]){await change('size',size);const boxes=app.right.labelBoxes();assert.equal(boxes.length,20);for(let i=0;i<boxes.length;i++)for(let j=0;j<i;j++){const a=boxes[i],b=boxes[j];assert(!(a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y),'City labels overlap');}}
 }
 if(kind==='direction'){await change('mode','orientation');await change('speed',true);assert.equal(w.document.getElementById('wind-combo-details').hidden,false);const before=app.right.svg.outerHTML;await change('speedSize',50);assert.notEqual(app.right.svg.outerHTML,before);}
 const tasks=w.document.querySelector('.task-hover');tasks.dispatchEvent(new w.Event('mouseenter'));assert(tasks.classList.contains('is-open'));assert.equal(tasks.querySelector('.task-popup').style.width,'340px');assert(w.document.querySelector('.title-line').contains(tasks));tasks.dispatchEvent(new w.Event('mouseleave'));await new Promise(r=>setTimeout(r,180));assert(!tasks.classList.contains('is-open'));assert(!w.document.body.textContent.includes('Vorschau aktuell'));
 if(process.env.KARTO_PREVIEW){if(kind==='nominal')await change('mode','hue');if(kind==='ordinal')await change('mode','value');if(kind==='quantitative')await change('mode','size');if(kind==='direction')await change('mode','orientation');fs.writeFileSync('/tmp/karto-'+kind+'.svg',app.right.svg.outerHTML);}
 assert.equal(app.left.svg.outerHTML,left);assert.notEqual(app.right.svg.outerHTML,right);assert(!app.right.svg.outerHTML.includes('NaN'));assert(!w.document.body.textContent.includes('Hinweis zur Eignung'));assert(!app.right.svg.outerHTML.includes('#efc54a'));assert.equal(w.document.body.classList.contains('is-loading'),false);w.document.getElementById('reset').click();assert.equal(app.right.svg.outerHTML,right);assert(w.document.querySelector('.lab-stage').firstElementChild.classList.contains('workspace'));assert.deepEqual(errors,[]);console.log(kind,': rendering, inputs, fixed original and reset OK');w.close();
}
console.log('DWD direction conversion, OSM access categories, shared population date and proportional area OK');
