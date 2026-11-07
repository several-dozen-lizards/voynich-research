// Authored in-memory UI fixtures only. Does not create rater data.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/rater-only/index.html','utf8');
const script=html.split('<script>')[1].split('</script>')[0];
class Element {
 constructor(){this.value='';this.children=[];this.style={};this.complete=true;this.naturalWidth=1000;this.files=[];}
 add(x){this.children.push(x);if(this.children.length===1)this.value=String(x.value);}
 append(x){this.children.push(x);}
 replaceChildren(){this.children=[];}
 setPointerCapture(){}
 getBoundingClientRect(){return {left:0,top:0,width:1000,height:1000};}
 click(){}
}
const elements={};const ctx=vm.createContext({document:{getElementById:id=>elements[id]??=(new Element()),createElement:()=>new Element()},Option:function(text,value){this.text=text;this.value=value;},URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}},Blob:function(){},setTimeout:()=>{}});
vm.runInContext(script,ctx);const run=s=>vm.runInContext(s,ctx);
assert(run('tasks.length')===168);
run("el('who').value='ENGINEERING_ONLY'; el('kind').value='line'; el('block').value='b'; el('number').value='1'; el('record').onclick()");assert(run('rows.length')===0);
run("frame.onpointerdown({clientX:100,clientY:200,pointerId:1,preventDefault(){}});frame.onpointermove({clientX:300,clientY:250});frame.onpointerup()");
assert.deepStrictEqual(JSON.parse(run('JSON.stringify(region)')),JSON.parse(run('JSON.stringify([.1*tasks[0].native_width,.2*tasks[0].native_height,.2*tasks[0].native_width,.05*tasks[0].native_height].map(Math.round))')));
run("el('record').onclick()");assert(run('rows.length')===1);
run("region=[1,1,20,20];el('record').onclick()");assert(run('rows.length')===1); // duplicate line number rejected
run("el('kind').value='picture';el('category').value='PL';el('record').onclick()");assert(run('rows.length')===2);
run("page()");assert(run('region')===null);
console.log('PASS: 168 tasks; native-coordinate conversion; missing box rejection; line entry; duplicate-line rejection; picture entry; page reset. Engineering fixtures only.');
