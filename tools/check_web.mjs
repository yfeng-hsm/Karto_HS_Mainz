// Run with: NODE_PATH=/tmp/karto-test/node_modules node tools/check_web.mjs
import {createRequire} from 'node:module';import fs from 'node:fs';import assert from 'node:assert/strict';
import {classify,fisherJenks} from '../docs/assets/core.mjs';
const require=createRequire(import.meta.url),{JSDOM}=require('jsdom');
const data=JSON.parse(fs.readFileSync('docs/data/mainz.json')),values=data.population.map(d=>d.value);
assert.deepEqual(fisherJenks([0,0,1,1,9,10],2),[1,10]);for(const method of ['equal','quantile','jenks'])for(let k=3;k<=7;k++){const c=classify(values,method,k);assert.equal(c.counts.reduce((a,b)=>a+b),2982);assert(c.bins.every((v,i)=>!i||v>c.bins[i-1]));assert.equal(c.bins.at(-1),946);}
globalThis.KARTO_TEST=true;const{start}=await import('../docs/assets/app.mjs');
for(const kind of ['bertin','color']){const dom=new JSDOM(fs.readFileSync(`docs/${kind==='color'?'farben':'bertin'}.html`,'utf8'),{runScripts:'outside-only',pretendToBeVisual:true});const w=dom.window;w.eval(fs.readFileSync('docs/assets/d3.min.js','utf8'));Object.assign(globalThis,{document:w.document,d3:w.d3,requestAnimationFrame:w.requestAnimationFrame.bind(w),fetch:async()=>({ok:true,json:async()=>data})});const app=await start(),before=app.left.svg.outerHTML,right=app.right.svg.outerHTML;
const control=w.document.querySelector(kind==='bertin'?'#size':'#palette');control.value=kind==='bertin'?'24':'warm';control.dispatchEvent(new w.Event('input'));await new Promise(r=>w.requestAnimationFrame(r));assert.equal(app.left.svg.outerHTML,before);assert.notEqual(app.right.svg.outerHTML,right);assert.equal(w.document.body.classList.contains('is-loading'),false);w.document.getElementById('reset').click();assert.equal(app.right.svg.outerHTML,right);assert(!right.includes('NaN'));assert(right.includes('DEUTSCHLAND'));console.log(kind,'render, update, fixed original, reset: OK');w.close();}
console.log('classification, all 3 methods × 5 class counts: OK');
