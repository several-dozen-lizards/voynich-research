import fs from 'node:fs/promises';import crypto from 'node:crypto';import path from 'node:path';
const root=process.cwd(),out=path.join(root,'bc-adapter-qualification-2026-10-25');
async function walk(p){let z=[];for(const e of await fs.readdir(p,{withFileTypes:true})){let f=path.join(p,e.name);if(e.isDirectory())z.push(...await walk(f));else if(e.isFile())z.push(f)}return z}
let names=await walk(path.join(root,'ordered-name-lists-v7c/attempt-3-v7.2'));names.push(path.join(root,'ordered-name-lists-v7c/HARNESS/harness.py'),path.join(root,'priority-continuation-2026-10-25/adapters/adapters.py'));
let files={};for(const f of names)files[path.relative(root,f).replaceAll('\\','/')]=crypto.createHash('sha256').update(await fs.readFile(f)).digest('hex');
let dst=path.join(out,'BASELINE-'+(process.argv[2]||'BEFORE')+'.json');await fs.writeFile(dst,JSON.stringify({utc:new Date().toISOString(),files},null,2)+'\n');console.log(JSON.stringify({files:names.length,destination:dst}));
