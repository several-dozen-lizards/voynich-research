import assert from 'node:assert/strict';
import * as e from './engine.mjs';
const checks=[];function check(name,fn){fn();checks.push(name);}
check('105 unique bounded windows',()=>{assert.equal(e.windows().length,105);assert.equal(new Set(e.windows().map(String)).size,105);});
check('longest prefix and suffix; no overlap',()=>{assert.deepEqual(e.segment('qokaiin'),{opener:'qok',category:'qok',core:'',ending:'aiin',endgroup:'a-family',classKey:'["qok",""]'});assert.equal(e.segment('qok').ending,'');});
check('unknown original slots preserved',()=>assert.deepEqual(e.tokenize('chol.ai?n.daiin='),['chol',null,'daiin']));
check('reserved split deterministic',()=>{assert.equal(e.splitFolio('f1r'),'CONFIRMATION');assert(e.RESERVED.has('f73r'));});
const variants=['aiin','ain','air','ar'];const planted=Array.from({length:40},(_,i)=>({tokens:['pfirst','chol'+variants[i%4],null,'zzzz','zzzz','zzzz','zzzz','zzzz']}));
check('known early four-variant slot recovered',()=>{let d=e.discover(planted);assert.equal(d.status,'CANDIDATE');assert.deepEqual(d.selected.W,[2,2]);assert.equal(d.selected.classKey,'["ch","ol"]');assert.equal(d.selected.variants.length,4);assert(e.confirmMetrics(planted,d.selected).pass);});
check('single-type cannot be padded into closed set',()=>assert.equal(e.closedSet({x:100}),null));
check('over16 required variants rejected',()=>assert.equal(e.closedSet(Object.fromEntries(Array.from({length:30},(_,i)=>['v'+i,1]))),null));
check('no candidate distinct type control',()=>assert.equal(e.discover([{tokens:['pfirst','cholaiin','zzzz']}]).status,'NO CANDIDATE'));
check('missing outside support is undefined',()=>assert.equal(e.metrics([{tokens:['first','cholaiin']}],'["ch","ol"]',[2,15]).concentration,null));
check('first token and all original slots preserved by shuffle',()=>{let s=77;let rng=()=>((s=(Math.imul(s,1664525)+1013904223)>>>0)/4294967296);for(let i=0;i<50;i++){let p=e.shuffled(planted,rng);assert.equal(p[0].tokens[0],'pfirst');assert.deepEqual(p[0].tokens.slice(1).map(String).sort(),planted[0].tokens.slice(1).map(String).sort());}});
check('frozen variants reject novel confirmation inventory',()=>{let c=e.discover(planted).selected;let x=planted.map(p=>({...p,tokens:p.tokens.map(w=>w&&w.startsWith('chol')?'cholal':w)}));assert.equal(e.confirmMetrics(x,c).pass,false);});
check('Holm inactive slot retains factor2',()=>assert.deepEqual(e.holm([.03,null]),[.06,1]));
check('quadratic kappa exact fixtures and degenerate abstention',()=>{assert.equal(e.quadraticKappa([0,1,2],[0,1,2]),1);assert.equal(e.quadraticKappa([0,0],[0,0]),null);assert.equal(e.quadraticKappa([0,2],[2,0]),-1);});
export const result={status:'PASS',checks,count:checks.length,scope:'Authored engineering; NOT historical positive-control or scientific qualification'};
