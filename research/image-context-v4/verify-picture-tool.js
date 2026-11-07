// In-memory authored fixtures only; no scientific responses saved.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const script=fs.readFileSync(__dirname+'/rater-only/index.html','utf8').split('<script>')[1].split('</script>')[0];
class E{constructor(){this.value='';this.children=[];this.style={};this.complete=true;this.naturalWidth=1000;}add(x){this.children.push(x);if(this.children.length===1)this.value=String(x.value);}append(x){this.children.push(x);}replaceChildren(){this.children=[];}setPointerCapture(){}getBoundingClientRect(){return{left:0,top:0,width:1000,height:1000};}click(){}}
const elements={},ctx=vm.createContext({document:{getElementById:id=>elements[id]??=new E(),createElement:()=>new E()},Option:function(t,v){this.value=v;},URL:{createObjectURL:()=>'',revokeObjectURL(){}},Blob:function(){},setTimeout(){}});vm.runInContext(script,ctx);const run=s=>vm.runInContext(s,ctx);
assert(run('tasks.length')===168);assert(!script.includes("el('kind')")&&!script.includes("el('block')")&&!script.includes('line_number'));
run("el('who').value='ENGINEERING_ONLY';el('complete').onclick()");assert(run('completed.size')===1);assert(run('rows.length')===0);
run("el('reopen').onclick();el('record').onclick()");assert(run('rows.length')===0);
run("frame.onpointerdown({clientX:100,clientY:200,pointerId:1,preventDefault(){}});frame.onpointermove({clientX:300,clientY:250});frame.onpointerup()");
assert.strictEqual(run('JSON.stringify(region)'),run('JSON.stringify([.1*tasks[0].native_width,.2*tasks[0].native_height,.2*tasks[0].native_width,.05*tasks[0].native_height].map(Math.round))'));
run("el('category').value='PL';el('record').onclick()");assert(run('rows.length')===1);
run("region=rows[0].box;el('record').onclick()");assert(run('rows.length')===1);
run("el('complete').onclick();region=[1,1,30,30];el('record').onclick()");assert(run('rows.length')===1);
run('page()');assert(run('region')===null);console.log('PASS picture-only entry, native geometry, zero-picture completion, duplicates, completed-page lock and reset.');
