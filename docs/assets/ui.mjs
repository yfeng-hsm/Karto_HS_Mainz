export function setupLayout(kind){
 document.body.classList.add('compact-lab');
 const main=document.querySelector('main'),panel=document.querySelector('.controls-panel'),workspace=document.querySelector('.workspace');
 const stage=document.createElement('div');stage.className='lab-stage';panel.before(stage);stage.append(workspace,panel);
 const tasks=document.querySelector('.tasks'),wrap=document.createElement('div');wrap.className='task-details task-hover';
 const trigger=document.createElement('button');trigger.type='button';trigger.className='task-trigger';trigger.textContent='Aufgabe ⓘ';trigger.setAttribute('aria-describedby','task-tooltip');trigger.setAttribute('aria-expanded','false');
 tasks.classList.add('task-popup');tasks.id='task-tooltip';tasks.setAttribute('role','tooltip');tasks.before(wrap);wrap.append(trigger,tasks);
 const show=on=>{wrap.classList.toggle('is-open',on);trigger.setAttribute('aria-expanded',String(on));};
 wrap.addEventListener('mouseenter',()=>show(true));wrap.addEventListener('mouseleave',()=>{if(!wrap.contains(document.activeElement))show(false);});wrap.addEventListener('focusin',()=>show(true));wrap.addEventListener('focusout',e=>{if(!wrap.contains(e.relatedTarget))show(false);});trigger.addEventListener('click',()=>show(true));trigger.addEventListener('keydown',e=>{if(e.key==='Escape')show(false);});document.addEventListener('pointerdown',e=>{if(!wrap.contains(e.target))show(false);});
 const help=document.createElement('details');help.className='help-details';const hs=document.createElement('summary');hs.textContent='Daten · Messwerte · Quellen';help.append(hs);main.append(help);for(const n of document.querySelectorAll('.note,.discussion,footer,.data-table'))help.append(n);
}
export function exportButtons(svg,name){
 function download(blob,ext){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=name+'.'+ext;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const serialize=()=>new XMLSerializer().serializeToString(svg);
 document.getElementById('export-svg').onclick=()=>download(new Blob([serialize()],{type:'image/svg+xml'}),'svg');
 document.getElementById('export-png').onclick=()=>{const img=new Image(),url=URL.createObjectURL(new Blob([serialize()],{type:'image/svg+xml'}));img.onload=()=>{const c=document.createElement('canvas');c.width=1800;c.height=2040;c.getContext('2d').drawImage(img,0,0,1800,2040);c.toBlob(b=>download(b,'png'));URL.revokeObjectURL(url);};img.src=url;};
}
