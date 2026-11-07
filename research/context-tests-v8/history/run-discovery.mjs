import fs from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import readline from 'node:readline';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as E from './engine.mjs';
const R=path.dirname(fileURLToPath(import.meta.url));const P=path.dirname(R);
const sha=x=>createHash('sha256').update(x).digest('hex');
const load=async p=>JSON.parse(await fs.readFile(path.join(R,p),'utf8'));
const save=async(p,x)=>fs.writeFile(path.join(R,p),E.safeJSON(x));
export async function run(){
 const freeze=await load('T3/PRE-DISCOVERY-SEAL.json');for(const [p,h]of Object.entries(freeze.hashes))if(sha(await fs.readFile(path.join(R,p)))!==h)throw Error('Seal mismatch '+p);
 const log=await load('T3/DISCOVERY-LOG.json');if(log.looks_used!==0)throw Error('One-shot discovery already used; do not overwrite');
 const split=await load('T3/SPLIT.json');const eligible=new Map(split.folios.filter(x=>x.arm==='DISCOVERY').map(x=>[x.folio,x]));
 const manifest=JSON.parse(await fs.readFile(path.join(P,'complete-atlas-v56/SOURCE-MANIFEST.json'),'utf8'));const source=Object.keys(manifest.hashes).find(x=>x.endsWith('text16e6.original.evt')).replace(/\\+/g,'/');
 const digest=createHash('sha256');for await(const c of createReadStream(source))digest.update(c);if(digest.digest('hex')!==manifest.hashes[Object.keys(manifest.hashes).find(x=>x.endsWith('text16e6.original.evt'))])throw Error('EVT source mismatch');
 let groups=new Map(),seen=new Set(),audit={accepted_lines:0,confirmation_bodies_parsed:0,reserved_bodies_parsed:0,other_readings_parsed:0,paragraph_exclusions:[],source_sha256:manifest.hashes[Object.keys(manifest.hashes).find(x=>x.endsWith('text16e6.original.evt'))],boundary_policy:'group folio/place; original source order; terminate on explicit =; discard unterminated tails'};
 // Scan headers before examining any body. No confirmation body is tokenized or retained.
 for await(const line of readline.createInterface({input:createReadStream(source,{encoding:'latin1'}),crlfDelay:Infinity})){
  let close=line.indexOf('>');if(close<0)continue;let header=line.slice(0,close+1),m=header.match(/^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>$/);if(!m)continue;
  let [,folio,place,number,reading]=m;if(E.RESERVED.has(folio)||!eligible.has(folio)||reading!=='H'||!place.startsWith('P'))continue;
  let locus=folio+'.'+place+'.'+number;if(seen.has(locus))throw Error('Duplicate locus '+locus);seen.add(locus);
  let text=line.slice(close+1),key=folio+'/'+place;if(!groups.has(key))groups.set(key,[]);groups.get(key).push({folio,place,locus,tokens:E.tokenize(text),end:text.split('#')[0].includes('=')});audit.accepted_lines++;
 }
 let paragraphs=[];
 for(const rows of groups.values()){let acc=[],loci=[];for(const r of rows){acc.push(...r.tokens);loci.push(r.locus);if(r.end){if(acc.length>1)paragraphs.push({folio:r.folio,scribe:eligible.get(r.folio).scribe,loci:loci.slice(),tokens:acc.slice()});else audit.paragraph_exclusions.push({loci:loci.slice(),reason:'fewer than two original slots'});acc=[];loci=[];}}if(loci.length)audit.paragraph_exclusions.push({loci,reason:'unterminated paragraph tail'});}
 await save('T3/DISCOVERY-PARAGRAPHS.json',paragraphs);await save('T3/EXTRACTION-AUDIT.json',audit);
 let results={};for(const scribe of ['1','2']){let pp=paragraphs.filter(p=>p.scribe===scribe);results[scribe]={...E.discover(pp),paragraphs:pp.length,folios:new Set(pp.map(p=>p.folio)).size};}
 await save('T3/DISCOVERY.json',results);
 let entries=['1','2'].map(s=>({look:1,scribe:s,reading:'H',search:'all registered class/window combinations; one batch; no refinement',result:results[s].status,utc:new Date().toISOString()}));await save('T3/DISCOVERY-LOG.json',{looks:entries,looks_used:1,maximum:20,refinement_looks:0,confirmation_opened:false});
 await save('T3/FREEZE.json',{utc:new Date().toISOString(),status:'DISCOVERY COMPLETE; EXACT CANDIDATES FROZEN; CONFIRMATION CLOSED',candidates:Object.fromEntries(['1','2'].map(s=>[s,results[s].selected])),thresholds:{presence:'discovery presence minus .15',concentration:1.5,coverage:.7,max_new_types:4},positive_qualification:'OUTSTANDING',confirmation_bodies_parsed:0});
 await save('T3/POST-DISCOVERY-SEAL.json',{utc:new Date().toISOString(),hashes:Object.fromEntries(await Promise.all(['T3/DISCOVERY.json','T3/DISCOVERY-LOG.json','T3/FREEZE.json','T3/EXTRACTION-AUDIT.json','T3/DISCOVERY-PARAGRAPHS.json'].map(async p=>[p,sha(await fs.readFile(path.join(R,p)))])))});
 return {results,audit,paragraphs:paragraphs.length};
}
