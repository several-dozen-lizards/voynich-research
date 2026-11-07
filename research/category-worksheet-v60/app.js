const $ = id => document.getElementById(id);
const esc = x => String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const storageKey = 'voynich-category-worksheet-v60-notes';
let notes = {};
try { notes = JSON.parse(localStorage.getItem(storageKey) || '{}'); } catch (_) {}
function tokens(ws, mapping={}) {
  return '<div class="tokens">'+ws.map((w,i)=>'<span class="token '+(w && mapping[w]?'assigned':'')+'"><b>'+esc(w===null?'□':w)+'</b><small>'+esc(w===null?'UNKNOWN SLOT':mapping[w] || 'unassigned')+' · '+(i+1)+'</small></span>').join('')+'</div>';
}
function skeleton(ws, mapping) { return ws.map(w=>w===null?'[□ UNKNOWN SLOT]':mapping[w]?'['+mapping[w]+']':w).join(' '); }
function changeGroup() {
  const c=WORKSHEET.cohorts[Number($('cohort').value)];
  $('model').innerHTML='<option value="-1">Unassigned source text</option>'+c.models.map((m,i)=>'<option value="'+i+'">'+esc(m.name)+'</option>').join('');
  render();
}
function render() {
  const c=WORKSHEET.cohorts[Number($('cohort').value)];
  const mi=Number($('model').value), mapping=mi<0?{}:c.models[mi].mapping;
  let out='<h2>'+esc(c.title)+'</h2><p>'+esc(c.selection)+'</p>';
  for (const p of c.passages) {
    out+='<h3>'+esc(p.locator)+'</h3><p class="muted">'+esc(p.agreement)+'</p><div class="readings">';
    for (const tr of ['H','F']) {
      const r=p.readings[tr];
      out+='<article class="reading"><h3>'+tr+' · '+(tr==='H'?'Takahashi':'First Study Group')+'</h3><p class="muted">'+esc(r.section)+' · hand '+esc(r.hand)+' · variety '+esc(r.variety)+' · raw format '+esc(r.format)+'</p>'+tokens(r.tokens,mapping)+'<details><summary>Previous / following source lines</summary>';
      for(const [label,v] of [['Previous',r.previous],['Following',r.following]]) out+='<p>'+label+' · '+esc(v?v.locator:'none in same page/format')+'</p>'+(v?'<div class="raw">'+esc(v.tokens.map(w=>w===null?'□':w).join(' '))+'</div>':'');
      out+='</details></article>';
    }
    out+='</div>';
  }
  out+='<h3>Competing substitutions · same words, different proposed functions</h3><p>Only the explicit words below receive categories. All other words stay unassigned. Assignments are local to this passage group, not a manuscript dictionary.</p><table><thead><tr><th>Hypothesis</th><th>H substitutions</th><th>F substitutions</th><th>What fits / breaks / next test</th></tr></thead><tbody>';
  for (const m of c.models) {
    out+='<tr><td data-label="Hypothesis"><strong>'+esc(m.name)+'</strong><p>'+Object.entries(m.mapping).map(([w,v])=>esc(w)+' → '+esc(v)).join('<br>')+'</p></td>';
    for(const tr of ['H','F']) out+='<td data-label="'+tr+' substitutions">'+c.passages.map(p=>'<p><small>'+esc(p.locator)+'</small><br><span class="raw">'+esc(skeleton(p.readings[tr].tokens,m.mapping))+'</span></p>').join('')+'</td>';
    out+='<td data-label="Assessment"><p><strong>Fits, provisionally:</strong> '+esc(m.fits)+'</p><p><strong>Breaks / missing:</strong> '+esc(m.breaks)+'</p><p><strong>Discriminating test:</strong> '+esc(m.test)+'</p></td></tr>';
  }
  out+='</tbody></table><h3>Form / discourse alternative</h3><p>'+esc(WORKSHEET.nonsemantic)+'</p><p>The same word retains the same neutral slot ID within each source line:</p><div class="readings">';
  for(const tr of ['H','F']) out+='<div><strong>'+tr+'</strong>'+c.passages.map(p=>{const ids={};let n=0;return '<p><small>'+esc(p.locator)+'</small><br><span class="raw">'+esc(p.readings[tr].tokens.map(w=>w===null?'□':(ids[w] || (ids[w]='S'+(++n)))).join(' '))+'</span></p>';}).join('')+'</div>';
  out+='</div><h3><label for="notes">Working notes · '+esc(c.title)+'</label></h3><textarea id="notes" placeholder="Which prediction could distinguish these readings? What remains unexplained?"></textarea><p id="saved" class="muted" aria-live="polite"></p>';
  $('content').innerHTML=out;
  $('notes').value=notes[c.id] || '';
  $('notes').oninput=()=>{notes[c.id]=$('notes').value;try{localStorage.setItem(storageKey,JSON.stringify(notes));$('saved').textContent='Notes saved in this browser.';}catch(_){$('saved').textContent='Browser storage unavailable; export to keep these notes.';}};
}
$('cohort').innerHTML=WORKSHEET.cohorts.map((c,i)=>'<option value="'+i+'">'+esc(c.title)+'</option>').join('');
$('null').textContent=WORKSHEET.combination_test_caveat;
$('cohort').onchange=changeGroup;
$('model').onchange=render;
$('export').onclick=()=>{const blob=new Blob([JSON.stringify({worksheet:WORKSHEET,notes,exported_at:new Date().toISOString()},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='voynich-category-worksheet-v60-notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
changeGroup();
