export const MODES=['hue','form','size','value','texture','orientation'];
export function flowTo(from){return (from+180)%360;}
export function speedLevel(speed){return [2,4,6].filter(t=>speed>=t).length;}
export function symbolArea(value,max,maxRadius){return Math.PI*maxRadius**2*value/max;}
export const defaultState=kind=>kind==='direction'?{windExtra:'none',windPalette:'tableau',extraPalette:'tableau',windForms:'geometric',extraForms:'geometric',observedRange:true,minRatio:.2,mode:'hue',symbol:'circle',encode:false,size:26,names:true,speed:false,speedSize:38,valueFamily:'blue',reverseValue:false,lightLow:25,lightHigh:83,texture:6,ink:'#285c68'}:{mode:kind==='nominal'?'size':kind==='ordinal'?'form':'hue',size:14,palette:'editorial',shape:'circle',formSet:'geometric',valueFamily:'blue',reverseValue:false,lightLow:25,lightHigh:83,texture:6,angle:0,combine:false,names:true};
// Deterministic, non-overlapping label boxes; leader lines can connect distant labels.
export function placeLabels(items,obstacles,reserved,bounds){
 const boxes=[],result=[],hit=(a,b)=>a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;
 const inside=r=>r.x>=bounds.x&&r.y>=bounds.y&&r.x+r.w<=bounds.x+bounds.w&&r.y+r.h<=bounds.y+bounds.h;
 for(const p of items){const candidates=[],dirs=[[1,-1],[-1,-1],[1,1],[-1,1],[0,-1],[0,1],[1,0],[-1,0]];
  for(const gap of [8,18,32,48,72,100])for(const[dx,dy]of dirs){const d=p.r+gap,x=dx>0?p.x+d:dx<0?p.x-d-p.w:p.x-p.w/2,y=dy>0?p.y+d:dy<0?p.y-d-p.h:p.y-p.h/2;candidates.push({x,y,w:p.w,h:p.h});}
  for(let y=bounds.y;y<bounds.y+bounds.h-p.h;y+=20)for(let x=bounds.x;x<bounds.x+bounds.w-p.w;x+=30)candidates.push({x,y,w:p.w,h:p.h});
  const valid=candidates.filter(r=>inside(r)&&![...reserved,...boxes,...obstacles].some(b=>hit(r,b)));
  const options=valid.length?valid:candidates.filter(r=>inside(r)&&![...reserved,...boxes].some(b=>hit(r,b)));
  options.sort((a,b)=>{const cost=r=>(r.x+r.w/2-p.x)**2+(r.y+r.h/2-p.y)**2;return cost(a)-cost(b);});
  const rect=options[0];if(!rect)continue;boxes.push(rect);result.push({...p,rect});
 }return result;
}
export function toneColor(d3,family,L){
 const bases={gray:'#777777',blue:'#286da2',green:'#28744d',orange:'#b65c22',purple:'#7650a1'},base=d3.lab(bases[family]||bases.gray),c=d3.lab(L,family==='gray'?0:base.a,family==='gray'?0:base.b);
 for(let i=0;i<30&&!d3.rgb(c).displayable();i++){c.a*=.84;c.b*=.84;}
 return c.formatHex();
}
