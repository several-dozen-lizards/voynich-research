import fs from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import readline from 'node:readline';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {tokenize,RESERVED} from '../context-tests-v8/engine.mjs';
const P=path.dirname(fileURLToPath(import.meta.url)),ROOT=path.dirname(P);
const read=async rel=>JSON.parse(await fs.readFile(path.join(ROOT,rel),'utf8'));
const freeze=JSON.parse(await fs.readFile(path.join(P,'LABEL-RESOLUTION-FREEZE.json'),'utf8'));
const inventory=await read('context-tests-v8/T1/GEOMETRY-INVENTORY.json');
const manifest=await read('complete-atlas-v56/SOURCE-MANIFEST.json');
const sourceEntry=Object.entries(manifest.hashes).find(([name])=>name.endsWith('text16e6.original.evt'));
const source=sourceEntry[0].replace(/\\/g,'/');
const hash=createHash('sha256');for await(const bytes of createReadStream(source))hash.update(bytes);if(hash.digest('hex')!==sourceEntry[1])throw Error('EVT source hash mismatch');
const allowed=new Map();
for(const row of inventory.reading_specific_maps){if(RESERVED.has(row.folio))throw Error('Reserved registration');for(const reading of ['H','F'])if(row[reading]){let key=reading+':'+row[reading];if(allowed.has(key))throw Error('Duplicate reading locus');allowed.set(key,{id:row.id,folio:row.folio,reading,locus:row[reading]});}}
const found=new Map();let acceptedBodies=0;
for await(const line of readline.createInterface({input:createReadStream(source,{encoding:'latin1'}),crlfDelay:Infinity})){
 const close=line.indexOf('>');if(close<0)continue;
 const m=line.slice(0,close+1).match(/^<(f\d+[rv]\d*)\.([^.]+)\.([^;]+);([A-Z])>$/);if(!m)continue;
 const [,folio,place,number,reading]=m;
 if(RESERVED.has(folio)||!['H','F'].includes(reading)||!place.startsWith('P'))continue;
 const key=reading+':'+folio+'.'+place+'.'+number;if(!allowed.has(key))continue;
 if(found.has(key))throw Error('Duplicate allowed EVT row');
 const mask=tokenize(line.slice(close+1)).map(word=>word!==null);
 found.set(key,{...allowed.get(key),available:true,original_slots:mask.length,initial_slot_present:mask.length>0,initial_readable:mask[0]??false,noninitial_mask:mask.slice(1)});acceptedBodies++;
}
const rows=[];
for(const row of inventory.reading_specific_maps)for(const reading of ['H','F']){
 const key=reading+':'+row[reading];rows.push(found.get(key)??{id:row.id,folio:row.folio,reading,locus:row[reading]??null,available:false,reason:row[reading]?'REGISTERED_LOCUS_NOT_FOUND':'NO_READING_SPECIFIC_MAP'});
}
const output={status:'READABILITY_MASKS_ONLY; NO IMAGE LABEL INPUTS OR REAL FEATURE OUTPUTS',source_sha256:sourceEntry[1],registered_physical_lines:1145,rows,accepted_registered_bodies:acceptedBodies,reserved_bodies_tokenized:0,unregistered_bodies_tokenized:0,real_word_classes_computed:0,raw_tokens_exported:0,allowed_data_inputs:['context-tests-v8/T1/GEOMETRY-INVENTORY.json','complete-atlas-v56/SOURCE-MANIFEST.json',sourceEntry[0]],tokenizer_owner:'context-tests-v8/engine.mjs tokenize; exact inherited original-slot policy',image_label_files_read:0};
await fs.writeFile(path.join(P,'READABILITY-MASKS.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({status:output.status,accepted_registered_bodies:acceptedBodies,source_sha256:sourceEntry[1],unavailable:rows.filter(row=>!row.available).length,real_word_classes_computed:0,raw_tokens_exported:0}));
