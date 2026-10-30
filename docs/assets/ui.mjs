export function setupLayout(kind){
 document.body.classList.add('compact-lab');
 const main=document.querySelector('main'),panel=document.querySelector('.controls-panel'),workspace=document.querySelector('.workspace');
 const stage=document.createElement('div');stage.className='lab-stage';panel.before(stage);stage.append(workspace,panel);
 const tasks=document.querySelector('.tasks'),details=document.createElement('details');details.className='task-details';const summary=document.createElement('summary');summary.textContent=kind==='color'?'Aufgabe: Klassifikation vergleichen → Farben wählen → begründen':'Aufgabe: Datenart erkennen → Zeichen wählen → Darstellung begründen';tasks.before(details);details.append(summary,tasks);
 const help=document.createElement('details');help.className='help-details';const hs=document.createElement('summary');hs.textContent='Daten · Messwerte · Quellen';help.append(hs);main.append(help);for(const n of document.querySelectorAll('.note,.discussion,footer,.data-table'))help.append(n);
}
export function exportButtons(svg,name){
 function download(blob,ext){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=name+'.'+ext;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 const serialize=()=>new XMLSerializer().serializeToString(svg);
 document.getElementById('export-svg').onclick=()=>download(new Blob([serialize()],{type:'image/svg+xml'}),'svg');
 document.getElementById('export-png').onclick=()=>{const img=new Image(),url=URL.createObjectURL(new Blob([serialize()],{type:'image/svg+xml'}));img.onload=()=>{const c=document.createElement('canvas');c.width=1800;c.height=2040;c.getContext('2d').drawImage(img,0,0,1800,2040);c.toBlob(b=>download(b,'png'));URL.revokeObjectURL(url);};img.src=url;};
}
