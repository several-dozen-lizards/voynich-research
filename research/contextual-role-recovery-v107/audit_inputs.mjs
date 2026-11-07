import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const dir=path.dirname(fileURLToPath(import.meta.url));
const source='C:/Users/lewis/.codex/visualizations/2026/10/21/01a160c2-56f0-7303-b3bf-ed8594c6ec40/voynich-grammar-v36/sources';
const read=async n=>JSON.parse(await fs.readFile(path.join(dir,n),'utf8'));
const saved=await read('BLIND-INPUT.json');const expected=new Map(saved.map(r=>[r.id,r]));
const cfg=(await read('PROTOCOL.json')).historical;const seen=new Set();let checked=0;let duplicate=0;let admitted=0;
for(const partition of ['train','dev','test']) {
const txt=(await fs.readFile(path.join(source,'la_proiel-ud-'+partition+'.conllu'),'utf8')).replace(/\r\n/g,'\n');
for(const paragraph of txt.trim().split('\n\n')) {
const lines=paragraph.split('\n');const sourceLine=lines.find(x=>x.startsWith('# source = '));if(!sourceLine)continue;
const sour=sourceLine.slice(11);const work=sour.split(',')[0];if(!cfg.works.includes(work))continue;
const tok=lines.filter(x=>/^\d+\t/.test(x)).map(x=>x.split('\t'));
const idline=lines.find(x=>x.startsWith('# sent_id = '));if(!idline)throw Error('No sentence id');const sentid=idline.slice(12);
const identity=JSON.stringify(tok.map(t=>t[1].toLowerCase()));if(seen.has(identity)){duplicate++;continue;}seen.add(identity);admitted++;
const ref=tok.map(t=>t[9].split('|').find(x=>x.startsWith('Ref='))).find(Boolean)?.slice(4);if(!ref)throw Error('No reference');
const unit=work+':'+ref.split('.').slice(0,2).join('.');const h=crypto.createHash('sha256').update('v107:'+unit).digest('hex');const split=parseInt(h.slice(0,8),16)%5<2?'test':'train';
for(let i=0;i<tok.length;i++) {
const target=tok[i][1].toLowerCase();if(!(target in cfg.targets))continue;
const context=[i-2,i-1,i+1,i+2].map(j=>{
if(j<0||j>=tok.length)return '#edge';
const between=tok.slice(Math.min(i,j),Math.max(i,j)+1).filter((_,offset)=>Math.min(i,j)+offset!==i);
if(between.some(t=>!/[\p{L}\p{N}]/u.test(t[1])))return '#barrier';return tok[j][1].toLowerCase();});
const id=partition+':'+sentid+':'+tok[i][0];const r=expected.get(id);if(!r)throw Error('Missing saved row '+id);
if(r.page!==unit||r.split!==split||r.stratum!==work+'|'+target||r.source_ref!==ref||JSON.stringify(r.context)!==JSON.stringify(context))throw Error('Context/metadata mismatch '+id);
expected.delete(id);checked++;
}
}
}
if(expected.size||checked!==saved.length)throw Error('Coverage mismatch');
const tr=new Set(saved.filter(r=>r.split==='train').map(r=>r.page));const te=new Set(saved.filter(r=>r.split==='test').map(r=>r.page));if([...tr].some(x=>te.has(x)))throw Error('Block leakage');
const audit={independent_language:'JavaScript reconstruction, separate from Python preparation; uses only visible surfaces for context barriers',checks:{all_occurrences_reconstructed:checked===2254,no_missing_or_extra_rows:expected.size===0,whole_block_splits_disjoint:true,no_gospel_model_rows:saved.every(r=>cfg.works.includes(r.stratum.split('|')[0]))},checked,admitted_sentences:admitted,duplicate_sentences_removed:duplicate};
await fs.writeFile(path.join(dir,'INDEPENDENT-INPUT-AUDIT.json'),JSON.stringify(audit,null,2));console.log(JSON.stringify(audit));
