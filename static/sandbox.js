'use strict';
const $ = id => document.getElementById(id);
let examples = [], result = null, revision = 0;
function invalidate() {
  revision++;
  $('confirmed').checked = false;
  $('run').disabled = true;
  $('results').hidden = true;
  result = null;
  $('error').textContent = '';
}
function addVariable(v = {name:'x',min:'0',max:'2',step:'1/10'}) {
  const row = document.createElement('div'); row.className = 'variable-row';
  for (const field of ['name','min','max','step']) {
    const input = document.createElement('input'); input.value = v[field]; input.dataset.field = field;
    input.setAttribute('aria-label', `${field} for variable ${$('variables').children.length+1}`);
    input.addEventListener('input', invalidate); row.append(input);
  }
  const remove = document.createElement('button'); remove.textContent = '×'; remove.setAttribute('aria-label','Remove variable');
  remove.onclick = () => { row.remove(); invalidate(); updateAdd(); }; row.append(remove);
  $('variables').append(row); updateAdd();
}
function updateAdd() { $('add').disabled = $('variables').children.length >= 2; }
function loadModel(item) {
  $('assertion').value = item?.assertion || '';
  $('assumptions').value = item?.assumptions || '';
  $('variables').replaceChildren();
  (item?.variables || [{name:'x',min:'0',max:'2',step:'1/10'}]).forEach(addVariable);
  $('context').textContent = item?.context || 'Custom claim: write the assertion, assumptions, and bounds below. This tool cannot automatically translate arbitrary scientific language. Split multiple claims into separate reviews.';
  $('provenance').textContent = item ? 'Reviewed example template' : 'Manual formalization';
  $('decomposition').hidden = false; invalidate();
}
$('decompose').onclick = () => {
  if (!$('claim').value.trim()) { $('error').textContent = 'Enter a claim first.'; $('claim').focus(); return; }
  loadModel(examples.find(x => x.claim === $('claim').value.trim()));
  $('assertion').focus();
};
$('example').onchange = () => {
  const item = examples.find(x => x.id === $('example').value);
  if (item) { $('claim').value = item.claim; loadModel(item); }
};
for (const id of ['claim','assertion','assumptions']) $(id).addEventListener('input', () => {
  invalidate(); $('provenance').textContent = 'Edited · review required';
  if (id === 'claim') { $('decomposition').hidden = true; $('example').value = ''; }
});
$('add').onclick = () => {addVariable({name:'y',min:'-2',max:'2',step:'1/2'}); invalidate();};
$('confirmed').onchange = () => {$('run').disabled = !$('confirmed').checked;};
$('run').onclick = async () => {
  const startRevision = revision;
  const spec = {claim:$('claim').value, assertion:$('assertion').value, assumptions:$('assumptions').value,
    confirmed:$('confirmed').checked, variables:[...$('variables').children].map(row => Object.fromEntries([...row.querySelectorAll('input')].map(i => [i.dataset.field,i.value])))};
  $('run').disabled = true; $('error').textContent = ''; $('run').textContent = 'Searching exact rational grid…';
  try {
    const response = await fetch('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(spec)});
    const body = await response.json(); if (!response.ok) throw new Error(body.error || 'Search failed.');
    if (revision !== startRevision) return;
    result = body; render(body.report); $('results').hidden = false; $('results').scrollIntoView({behavior:'smooth',block:'start'});
  } catch (e) { if (revision === startRevision) $('error').textContent = e.message; }
  finally { $('run').disabled = !$('confirmed').checked; $('run').textContent = 'Search for counterexamples ↗'; }
};
function render(r) {
  $('verdict').textContent = r.status.replaceAll('_',' ').toUpperCase(); $('conclusion').textContent = r.conclusion;
  $('stats').replaceChildren();
  for (const [key,value] of Object.entries(r.counts)) {const d=document.createElement('div');d.className='stat';const b=document.createElement('b');b.textContent=value;d.append(b,document.createTextNode(key.replaceAll('_',' ')));$('stats').append(d);}
  $('witness').replaceChildren();
  if (!r.witnesses.length) $('witness').textContent = 'No defined counterexample found in this grid.';
  for (const w of r.witnesses) {const el=document.createElement('div');el.className='witness';el.textContent=Object.entries(w.assignment).map(([k,v])=>`${k} = ${v}`).join(', ')+' → '+w.comparisons.map(c=>`${c.expression}: [${c.values.join(', ')}] → ${c.holds}`).join('; ');$('witness').append(el);}
  for (const issue of r.issues) {const el=document.createElement('p');el.textContent=`Unevaluated: ${JSON.stringify(issue.assignment)} — ${issue.reason}`;$('witness').append(el);}
  $('trace').replaceChildren();
  for (const sample of r.samples) {const tile=document.createElement('span');tile.className='tile'+(sample.holds?'':' fail');tile.title=JSON.stringify(sample.assignment)+': '+sample.holds;tile.setAttribute('aria-label',tile.title);$('trace').append(tile);}
  for (const [id,items] of [['limits',r.limits],['next',r.next_steps]]) {$(id).replaceChildren();for(const text of items){const li=document.createElement('li');li.textContent=text;$(id).append(li);}}
  $('record').textContent=`${r.method}\nEngine ${r.engine_version}\nSource SHA-256: ${r.engine_sha256}\nSpec SHA-256: ${r.spec_sha256}\nReplay: python3 reproduce.py report.json`;
}
function download(kind) {
  if (!result) return;
  const blob = new Blob([kind==='json'?JSON.stringify(result.report,null,2):result.markdown],{type:kind==='json'?'application/json':'text/markdown'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`report.${kind}`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
}
$('download-json').onclick=()=>download('json');$('download-md').onclick=()=>download('md');
addVariable();
fetch('/api/examples').then(r=>{if(!r.ok)throw new Error();return r.json();}).then(items=>{examples=items;for(const x of items){const option=document.createElement('option');option.value=x.id;option.textContent=x.title;$('example').append(option);}}).catch(()=>{$('error').textContent='Could not load examples. Reload the local server page.';});
