export function setupLayout(kind){
 document.body.classList.add('compact-lab');
 const main=document.querySelector('main'),panel=document.querySelector('.controls-panel'),workspace=document.querySelector('.workspace');
 const stage=document.createElement('div');stage.className='lab-stage';panel.before(stage);stage.append(workspace,panel);
 const tasks=document.querySelector('.tasks'),wrap=document.createElement('div');wrap.className='task-details task-hover';
 const trigger=document.createElement('button');trigger.type='button';trigger.className='task-trigger';trigger.textContent='i';trigger.setAttribute('aria-label','Aufgabe anzeigen');trigger.setAttribute('aria-describedby','task-tooltip');trigger.setAttribute('aria-expanded','false');
 const title=document.querySelector('.hero h1'),line=document.createElement('div');line.className='title-line';title.before(line);line.append(title,wrap);tasks.classList.add('task-popup');tasks.id='task-tooltip';tasks.setAttribute('role','tooltip');wrap.append(trigger,tasks);
 let hideTimer;
 const show=on=>{clearTimeout(hideTimer);if(on){const r=trigger.getBoundingClientRect(),view=trigger.ownerDocument.defaultView,width=Math.min(340,view.innerWidth-32);tasks.style.width=width+'px';tasks.style.left=Math.max(16,Math.min(r.right-width,view.innerWidth-width-16))+'px';tasks.style.top=(r.bottom+8)+'px';}wrap.classList.toggle('is-open',on);trigger.setAttribute('aria-expanded',String(on));};
 wrap.addEventListener('mouseenter',()=>show(true));wrap.addEventListener('mouseleave',()=>{hideTimer=setTimeout(()=>{if(!wrap.contains(document.activeElement))show(false);},150);});wrap.addEventListener('focusin',()=>show(true));wrap.addEventListener('focusout',e=>{if(!wrap.contains(e.relatedTarget))show(false);});trigger.addEventListener('click',()=>show(true));trigger.addEventListener('keydown',e=>{if(e.key==='Escape')show(false);});document.addEventListener('pointerdown',e=>{if(!wrap.contains(e.target))show(false);});
 const help=document.createElement('details');help.className='help-details';const hs=document.createElement('summary');hs.textContent='Daten · Messwerte · Quellen';help.append(hs);main.append(help);for(const n of document.querySelectorAll('.note,.discussion,footer,.data-table'))help.append(n);
}
export function exportButtons(svg,name){
 function download(blob,ext){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=name+'.'+ext;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const serialize=()=>new XMLSerializer().serializeToString(svg);
 document.getElementById('export-svg').onclick=()=>download(new Blob([serialize()],{type:'image/svg+xml'}),'svg');
 document.getElementById('export-png').onclick=()=>{const img=new Image(),url=URL.createObjectURL(new Blob([serialize()],{type:'image/svg+xml'}));img.onload=()=>{const c=document.createElement('canvas');c.width=1800;c.height=2040;c.getContext('2d').drawImage(img,0,0,1800,2040);c.toBlob(b=>download(b,'png'));URL.revokeObjectURL(url);};img.src=url;};
}
export function drawLocator(d3,svg,data){
 const ns='http://www.w3.org/2000/svg',add=(tag,attrs,parent)=>{const n=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);parent.append(n);return n;};
 const g=add('g',{class:'map-locator'},svg);add('rect',{x:498,y:90,width:81,height:101,fill:'#ffffff','fill-opacity':.95,rx:3},g);
 const project=d3.geoIdentity().reflectY(true).fitExtent([[512,111],[568,175]],data.germany);add('path',{d:d3.geoPath(project)(data.germany),fill:'#dfe6dc',stroke:'#aab4a5','stroke-width':.7},g);
 const[x,y]=project(data.mainz);add('circle',{cx:x,cy:y,r:3,fill:'#bf6545',stroke:'white','stroke-width':.5},g);
 const label=(x,y,s,bold=false)=>{const n=add('text',{x,y,'font-family':'Arial, sans-serif','font-size':10,fill:'#293c38','font-weight':bold?'bold':'normal'},g);n.textContent=s;};label(502,104,'DEUTSCHLAND',true);label(x+5,y+4,'Mainz');return g;
}
