// MIT: classification and visual-encoding helpers, independent of the DOM.
const cache = new WeakMap();
function quantile(sorted,p) {const h=(sorted.length-1)*p,i=Math.floor(h);return sorted[i]+(sorted[Math.min(i+1,sorted.length-1)]-sorted[i])*(h-i);}
export function fisherJenks(values,k) {
 const sorted=[...values].sort((a,b)=>a-b),x=[],w=[];
 for(const v of sorted){if(x.at(-1)===v)w[w.length-1]++;else{x.push(v);w.push(1);}}
 const n=x.length;k=Math.min(k,n);
 const sw=[0],sx=[0],ss=[0];for(let i=0;i<n;i++){sw.push(sw[i]+w[i]);sx.push(sx[i]+w[i]*x[i]);ss.push(ss[i]+w[i]*x[i]*x[i]);}
 const variance=(a,b)=>Math.max(0,ss[b]-ss[a]-(sx[b]-sx[a])**2/(sw[b]-sw[a]));
 const dp=Array.from({length:k+1},()=>new Float64Array(n+1).fill(Infinity));
 const cuts=Array.from({length:k+1},()=>new Int32Array(n+1));dp[0][0]=0;
 for(let c=1;c<=k;c++)for(let j=c;j<=n;j++)for(let i=c-1;i<j;i++){
  const cost=dp[c-1][i]+variance(i,j);if(cost<dp[c][j]){dp[c][j]=cost;cuts[c][j]=i;}
 }
 const bins=[];for(let c=k,j=n;c>0;c--){bins.push(x[j-1]);j=cuts[c][j];}return bins.reverse();
}
export function classify(values,method,k) {
 if(!values.length||values.some(x=>!Number.isFinite(x)))throw Error('Ungültige Zahlenwerte.');
 let record=cache.get(values);if(!record){record={sorted:[...values].sort((a,b)=>a-b),results:new Map()};cache.set(values,record);}
 const key=method+'/'+k;if(record.results.has(key))return record.results.get(key);
 const s=record.sorted,n=new Set(s).size;k=Math.min(Math.max(1,Math.round(k)),n);
 let bins;
 if(method==='equal'){const lo=s[0],hi=s.at(-1);bins=Array.from({length:k},(_,i)=>lo+(hi-lo)*(i+1)/k);}
 else if(method==='quantile')bins=Array.from({length:k},(_,i)=>quantile(s,(i+1)/k));
 else if(method==='log'){if(s[0]<0)throw Error('Logarithmische Intervalle benötigen nichtnegative Werte.');const lo=Math.log1p(s[0]),hi=Math.log1p(s.at(-1));bins=Array.from({length:k},(_,i)=>Math.expm1(lo+(hi-lo)*(i+1)/k));}
 else if(method==='jenks')bins=fisherJenks(s,k);
 else throw Error('Unbekannte Klassifikation.');
 bins=[...new Set(bins)];bins[bins.length-1]=s.at(-1);
 const counts=new Array(bins.length).fill(0);
 const ids=values.map(v=>{let l=0,r=bins.length-1;while(l<r){const m=(l+r)>>1;if(v<=bins[m])r=m;else l=m+1;}counts[l]++;return l;});
 const result={bins,ids,counts};record.results.set(key,result);return result;
}
export const BERTIN_BAD={size:155,sizeMode:'same',light:.44,lightMode:'same',valueOnly:false,palette:'bright',form:'mixed',angle:40,directions:true,texture:true,density:3,background:.95,names:true};
export const COLOR_BAD={logAxis:false,method:'quantile',classes:7,palette:'category',contrast:1,reverse:false,gray:false,border:.25,names:true};
export function categorySize(s,i){return s.size*(s.sizeMode==='category'?[1,.50,.23,.10][i]:1);}
export function categoryLight(s,i){return s.lightMode==='category'?Math.max(.12,Math.min(.94,s.light+[-.25,-.08,.09,.26][i])):s.light;}
export function cellLabel(lo,hi){return `${Math.floor(lo)}–${Math.floor(hi)}`;}
