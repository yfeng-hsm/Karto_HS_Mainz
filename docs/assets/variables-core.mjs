export const MODES=['hue','form','size','value','texture','orientation'];
export function flowTo(from){return (from+180)%360;}
export function speedLevel(speed){return [2,4,6].filter(t=>speed>=t).length;}
export function symbolArea(value,max,maxRadius){return Math.PI*maxRadius**2*value/max;}
export const defaultState=kind=>kind==='direction'?{symbol:'circle',encode:false,color:'direction',size:26,names:true,speed:false}:{mode:kind==='nominal'?'size':kind==='ordinal'?'form':'hue',size:14,palette:'editorial',shape:'circle',lightLow:25,lightHigh:83,texture:6,angle:0,combine:false,names:true};
