const $=id=>document.getElementById(id);
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=x=>Object.entries(x).map(([k,v])=>esc(k)+': '+v).join(' · ')||'none';
const frac=(n,d)=>d?n+'/'+d+' ('+(100*n/d).toFixed(1)+'%)':n+'/'+d+' (not estimable)';
let page=0;
const current=()=>DATA.groups[Number($('group').value)];
function modelAssessment(g,m){
 const op=m.name.includes('Preparation');
 if(g.id==='celestial')return 'The original worksheet specified no exact neighbour for sar. Its additional occurrences are too sparse to separate an operation, entity or celestial referent. A strict line-interior-only claim breaks, but no model originally required that claim.';
 return (op?'An operation followed by the originally assigned object remains a possible local reading.':'The same pair counts also permit this alternative assignment.')+' The other readable neighbours are unassigned. They break an obligatory exact-word adjacency rule, but do not by themselves refute a broader category model. The worksheet supplied no labelled set of acceptable substitute objects/values/conditions, so that stronger prediction remains untestable.';
}
function render(){
 const g=current();page=0;
 let out='<h2>'+esc(g.title)+'</h2><p>'+fmt(g.metadata)+' · excluded folios '+esc(g.excluded_folios.join(', '))+'</p>';
 out+='<div class="scroll"><table><thead><tr><th>Reading</th><th>Additional support</th><th>Fixed forward pair</th><th>Reverse pair</th><th>Right-neighbour rank</th><th>Unknown / edge right</th></tr></thead><tbody>';
 for(const tr of ['H','F']){const d=g.readings[tr],ties=g.target?Object.values(d.right_neighbors).filter(n=>n===d.forward_count).length:0;
  out+='<tr><td>'+tr+'</td><td>'+d.anchor_events+' '+esc(g.anchor)+' occurrences / '+d.anchor_folios+' folios<br>'+d.eligible_lines+' eligible lines / '+d.eligible_folios+' folios<br>'+d.single_reading_loci+' single-reading loci excluded</td><td>'+(g.target?esc(g.anchor+' '+g.target)+'<br>'+frac(d.forward_count,d.known_right_opportunities)+' readable right slots<br>'+d.forward_folios+' folios':'Not specified')+'</td><td>'+(g.target?esc(g.target+' '+g.anchor)+'<br>'+frac(d.reverse_count,d.known_left_opportunities)+' readable left slots':'Not specified')+'</td><td>'+(g.target?(d.target_right_rank===null?'Absent':d.target_right_rank+'; '+ties+' words tied at '+d.forward_count+' occurrence(s)'):'No predicted target')+'</td><td>'+d.unknown_right+' unknown / '+d.edge_right+' edge</td></tr>';
 }
 out+='</tbody></table></div><p class="muted">Denominators exclude unreadable neighbours and line edges. Forward and reverse rates use their own eligible sides. Ranks are descriptive; rank 1 among singleton ties is not a distinctive association.</p><h3>Position transfer</h3><div class="paired">';
 for(const tr of ['H','F']){const d=g.readings[tr];out+='<div><h3>'+tr+'</h3><p>Original anchor positions: '+fmt(d.original_positions)+'<br>Additional anchor positions: '+fmt(d.positions)+'<br>All readable tokens in eligible additional lines: '+fmt(d.all_readable_positions)+'</p><p>Original anchor ordinals: '+fmt(d.original_ordinals)+'<br>Additional anchor ordinals: '+fmt(d.ordinals)+'</p><details><summary>Neighbour distributions</summary><p>Following: '+fmt(d.right_neighbors)+'</p><p>Previous: '+fmt(d.left_neighbors)+'</p></details></div>';}
 out+='</div><p class="notice">Line interiors are numerous in the eligible text. An interior-heavy anchor distribution alone does not establish a record field or instruction role. Positions refer to source lines, not sentence or record boundaries.</p>';
 $('summary').innerHTML=out;
 $('models').innerHTML='<table class="models"><thead><tr><th>Fixed model</th><th>Unchanged assignments</th><th>Extension assessment</th></tr></thead><tbody>'+g.models.map(m=>'<tr><td data-label="Model">'+esc(m.name)+'</td><td data-label="Assignments">'+Object.entries(m.mapping).map(([w,k])=>esc(w)+' → '+esc(k)).join('<br>')+'</td><td data-label="Assessment">'+esc(modelAssessment(g,m))+'</td></tr>').join('')+'</tbody></table><p><strong>Form/discourse alternative:</strong> recurrence and source-line position are also compatible with grammatical, orthographic, copying or formulaic constraints. Those mechanisms are not individually tested here. Relabelling the same words leaves the measured neighbour pattern unchanged; these observations do not discriminate the proposed meanings.</p>';
 renderExamples();
}
function renderExamples(){
 const g=current(),mode=$('filter').value;
 const qualifies=e=>mode==='all'||mode==='forward'&&e.forward===true||mode==='exception'&&g.target&&![g.target,'#UNKNOWN','#EDGE'].includes(e.right)||mode==='boundary'&&['#UNKNOWN','#EDGE'].includes(e.right);
 const locs=[...new Set(['H','F'].flatMap(tr=>g.readings[tr].events.filter(qualifies).map(e=>e.locator)))].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
 const size=8;page=Math.max(0,Math.min(page,Math.max(0,Math.ceil(locs.length/size)-1)));
 $('page').textContent=locs.length?(page*size+1)+'–'+Math.min((page+1)*size,locs.length)+' of '+locs.length+' source lines':'No qualifying lines';
 $('prev').disabled=page===0;$('next').disabled=(page+1)*size>=locs.length;
 $('examples').innerHTML=locs.slice(page*size,(page+1)*size).map(loc=>'<article class="source"><h3>'+esc(loc)+'</h3><div class="paired">'+['H','F'].map(tr=>{
  const es=g.readings[tr].events.filter(e=>e.locator===loc);if(!es.length)return '<div><strong>'+tr+'</strong><p>No anchor occurrence at this locus in this reading. No text inferred from the other reading.</p></div>';
  const tokens=es[0].tokens;
  return '<div><strong>'+tr+'</strong><div class="raw">'+tokens.map(w=>w===null?'□':w===g.anchor||w===g.target?'<mark>'+esc(w)+'</mark>':esc(w)).join(' ')+'</div><p class="muted">'+es.map(e=>'ordinal '+e.ordinal+' · '+e.position+' · left '+esc(e.left)+' · right '+esc(e.right)).join('<br>')+'</p><details><summary>Three fixed category readings</summary>'+g.models.map(m=>'<p>'+esc(m.name)+'</p><div class="skeleton">'+esc(tokens.map(w=>w===null?'[□ UNKNOWN SLOT]':m.mapping[w]?'['+m.mapping[w]+']':w).join(' '))+'</div>').join('')+'</details></div>';
 }).join('')+'</div></article>').join('');
}
$('group').innerHTML=DATA.groups.map((g,i)=>'<option value="'+i+'">'+esc(g.title)+'</option>').join('');
$('group').onchange=render;$('filter').onchange=()=>{page=0;renderExamples();};$('prev').onclick=()=>{page--;renderExamples();};$('next').onclick=()=>{page++;renderExamples();};render();
