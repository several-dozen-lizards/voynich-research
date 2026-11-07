import {createHash} from 'node:crypto';
export const OPENERS=['qok','qo','ot','ok','ch','sh','d','k','t','p','f','y','o','a','s'];
export const ENDINGS=['aiin','ain','air','edy','eey','ar','al','ey','ol','or','y'];
export const RESERVED=new Set(['f72v1','f72v2','f73r','f73v']);
export function splitFolio(f){return BigInt('0x'+createHash('sha256').update('v8-T3:'+f).digest('hex'))%2n===0n?'DISCOVERY':'CONFIRMATION';}
export function segment(w){
 if(typeof w!=='string'||!(/^[a-z]+$/).test(w))throw Error('Readable lowercase word required');
 const opener=OPENERS.find(p=>w.startsWith(p))||'';
 const rest=w.slice(opener.length),ending=ENDINGS.find(s=>rest.endsWith(s))||'';
 const core=ending?rest.slice(0,-ending.length):rest;
 const category=['k','t','p','f'].includes(opener)?'other-gallows':opener||'other';
 const endgroup=['aiin','ain','air','ar','al'].includes(ending)?'a-family':['edy','eey','ey','y'].includes(ending)?'y-family':['ol','or'].includes(ending)?'ol-or':'other';
 return {opener,category,core,ending,endgroup,classKey:JSON.stringify([opener,core])};
}
export function tokenize(text){
 // Inherit attempt-C original-slot policy; commas/uncertain tokens remain barriers.
 text=text.split('#')[0].replace(/\{[^}]*\}/g,'').replace(/[!\s]/g,'');
 return text.split(/[.,=\-]/).filter(Boolean).map(w=>/^[a-z]+$/.test(w)?w:null);
}
export function windows(){let a=[];for(let lo=2;lo<=15;lo++)for(let hi=lo;hi<=15;hi++)a.push([lo,hi]);return a;}
export function variantsFor(paras,key){let types=new Set();for(let p of paras)for(let w of p.tokens.slice(1))if(w&&segment(w).classKey===key)types.add(w);return types;}
export function metrics(paras,key,W,variantMode='ending'){
 let hit=0,inside=0,outside=0,ci=0,co=0,unknown=0,counts={};
 for(let p of paras){let present=false;for(let i=1;i<p.tokens.length;i++){
  let w=p.tokens[i],inW=i+1>=W[0]&&i+1<=W[1];if(!w){unknown++;continue;}
  if(inW)inside++;else outside++;
  let s=segment(w);if(s.classKey!==key)continue;
  if(inW){ci++;present=true;let v=variantMode==='word'?w:s.ending;counts[v]=(counts[v]||0)+1;}else co++;
 }if(present)hit++;}
 let concentration=inside&&outside?(co?((ci/inside)/(co/outside)):ci?Infinity:null):null;
 return {paragraphs:paras.length,present:hit,presence:paras.length?hit/paras.length:null,inside_slots:inside,outside_slots:outside,inside_class:ci,outside_class:co,unknown_slots:unknown,concentration,variant_counts:counts};
}
export function closedSet(counts){let a=Object.entries(counts).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'en'));if(a.length<4)return null;let n=a.reduce((s,x)=>s+x[1],0),c=0;for(let i=0;i<Math.min(16,a.length);i++){c+=a[i][1];if(i>=3&&c/n>=.8)return a.slice(0,i+1).map(x=>x[0]);}return null;}
export function discoverReference(paras){
 let classes=new Set();for(let p of paras)for(let w of p.tokens.slice(1))if(w)classes.add(segment(w).classKey);
 let candidates=[],tested=0;
 for(let key of [...classes].sort()){
  let types=variantsFor(paras,key),mode=types.size===1?'word':'ending';
  for(let W of windows()){tested++;let m=metrics(paras,key,W,mode),V=closedSet(m.variant_counts);
   if(m.presence>=.5&&m.concentration>=2&&V)candidates.push({classKey:key,W,variantMode:mode,variants:V,discovery:m,score:m.presence*m.concentration});
  }
 }
 candidates.sort((a,b)=> b.score-a.score||b.discovery.presence-a.discovery.presence||b.discovery.concentration-a.discovery.concentration||(a.W[1]-a.W[0])-(b.W[1]-b.W[0])||a.W[0]-b.W[0]||(a.classKey<b.classKey?-1:a.classKey>b.classKey?1:0));
 return {status:candidates.length?'CANDIDATE':'NO CANDIDATE',tested_classes:classes.size,tested_class_windows:tested,eligible_candidates:candidates.length,selected:candidates[0]||null};
}
export function confirmMetrics(paras,candidate){let m=metrics(paras,candidate.classKey,candidate.W,candidate.variantMode),C=m.variant_counts,total=m.inside_class,known=candidate.variants.reduce((s,v)=>s+(C[v]||0),0),newTypes=Object.keys(C).filter(v=>!candidate.variants.includes(v));return {...m,coverage:total?known/total:null,new_types:newTypes,pass:m.presence>=candidate.discovery.presence-.15&&m.concentration>=1.5&&total>0&&known/total>=.7&&newTypes.length<=4};}
export function shuffled(paras,rng){return paras.map(p=>{let t=p.tokens.slice();for(let i=t.length-1;i>1;i--){let j=1+Math.floor(rng()*i);[t[i],t[j]]=[t[j],t[i]];}return {...p,tokens:t};});}
export function holm(ps){let ix=ps.map((p,i)=>({p:p??1,i})).sort((a,b)=>a.p-b.p||a.i-b.i),out=[],prev=0;for(let j=0;j<ix.length;j++){prev=Math.max(prev,Math.min(1,ix[j].p*(ix.length-j)));out[ix[j].i]=prev;}return out;}
export function quadraticKappa(a,b){if(!a.length||a.length!==b.length)throw Error('complete pairs required');if(a.some(x=>![0,1,2].includes(x))||b.some(x=>![0,1,2].includes(x)))throw Error('ordinal score required');let ma=[0,0,0],mb=[0,0,0],obs=0;for(let i=0;i<a.length;i++){ma[a[i]]++;mb[b[i]]++;obs+=(a[i]-b[i])**2;}let exp=0;for(let i=0;i<3;i++)for(let j=0;j<3;j++)exp+=ma[i]*mb[j]*(i-j)**2/a.length;return exp?1-obs/exp:null;}
export function safeJSON(x){return JSON.stringify(x,(k,v)=>typeof v==='number'&&!Number.isFinite(v)?v===Infinity?'POSITIVE_INFINITY':v===-Infinity?'NEGATIVE_INFINITY':'UNDEFINED':v,2)+'\n';}

export function discover(paras){
 const indexed=new Map();let slots=Array(16).fill(0),all=0,unknown=0;
 for(let pi=0;pi<paras.length;pi++)for(let i=1;i<paras[pi].tokens.length;i++){
  let w=paras[pi].tokens[i];if(!w){unknown++;continue;}all++;if(i+1<=15)slots[i+1]++;
  let s=segment(w);if(!indexed.has(s.classKey))indexed.set(s.classKey,[]);indexed.get(s.classKey).push({pi,pos:i+1,ending:s.ending,word:w});
 }
 let candidates=[],tested=0;
 for(let [key,occs]of [...indexed.entries()].sort((a,b)=>a[0]<b[0]?-1:1)){
  let mode=new Set(occs.map(o=>o.word)).size===1?'word':'ending';
  for(let W of windows()){
   tested++;let inside=slots.slice(W[0],W[1]+1).reduce((s,x)=>s+x,0),outside=all-inside;
   let ci=0,counts={},hit=new Set();for(let o of occs)if(o.pos>=W[0]&&o.pos<=W[1]){ci++;hit.add(o.pi);let v=mode==='word'?o.word:o.ending;counts[v]=(counts[v]||0)+1;}
   let co=occs.length-ci,concentration=inside&&outside?(co?(ci/inside)/(co/outside):ci?Infinity:null):null;
   let m={paragraphs:paras.length,present:hit.size,presence:paras.length?hit.size/paras.length:null,inside_slots:inside,outside_slots:outside,inside_class:ci,outside_class:co,unknown_slots:unknown,concentration,variant_counts:counts};
   let V=closedSet(counts);if(m.presence>=.5&&m.concentration>=2&&V)candidates.push({classKey:key,W,variantMode:mode,variants:V,discovery:m,score:m.presence*m.concentration});
  }
 }
 candidates.sort((a,b)=>b.score-a.score||b.discovery.presence-a.discovery.presence||b.discovery.concentration-a.discovery.concentration||(a.W[1]-a.W[0])-(b.W[1]-b.W[0])||a.W[0]-b.W[0]||(a.classKey<b.classKey?-1:a.classKey>b.classKey?1:0));
 return {status:candidates.length?'CANDIDATE':'NO CANDIDATE',tested_classes:indexed.size,tested_class_windows:tested,eligible_candidates:candidates.length,selected:candidates[0]||null};
}
