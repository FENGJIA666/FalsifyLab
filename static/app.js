'use strict';
const $ = id => document.getElementById(id);
const clone = value => JSON.parse(JSON.stringify(value));
const canonical = value => JSON.stringify(sortKeys(value));
function sortKeys(value) {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key,sortKeys(value[key])]));
  return value;
}
async function hash(value) {
  const bytes = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(value)));
  return [...new Uint8Array(bytes)].map(byte=>byte.toString(16).padStart(2,'0')).join('');
}
let revision=0, proposal=null, parent=null, selected=null, running=false, compileTicket=0;
const history=[];
function updateRun() { $('run').disabled=running || !proposal || !$('confirmed').checked; }
function invalidate() {
  revision++; compileTicket++; proposal=null;
  $('confirmed').checked=false; $('confirmed').disabled=true;
  $('proposal').hidden=true; $('proposal-empty').hidden=false; $('results').hidden=true;
  $('state').textContent='Start here'; $('error').textContent=''; $('notice').textContent=''; updateRun();
}
for (const id of ['claim','search-min','search-max','step']) $(id).addEventListener('input',invalidate);
$('confirmed').onchange=()=>{revision++;$('state').textContent=$('confirmed').checked?'Plan confirmed':'Plan ready';updateRun();};
async function post(url,data) {
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const body=await response.json();
  if (!response.ok) throw new Error(body.error || 'Request failed.');
  return body;
}
function field(container,label,text) {
  const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=text;container.append(dt,dd);
}
$('compile').onclick=async()=>{
  invalidate();const ticket=compileTicket;
  $('compile').textContent='Compiling…';
  try {
    const body=await post('/api/propose',{raw_text:$('claim').value,search_min:$('search-min').value,search_max:$('search-max').value,step:$('step').value});
    const p=body.proposal, unsigned=clone(p);delete unsigned.digest;
    if (await hash(unsigned)!==p.digest) throw new Error('Proposal digest mismatch. Compile again.');
    if(ticket!==compileTicket)return;
    proposal=clone(p);const i=p.interpretation,plan=p.plan,fields=$('model-fields');fields.replaceChildren();
    for(const [label,text] of [['Model',`${i.model}; rate = ${i.rate}; ${i.method}`],['Property',i.property],['Quantifier',i.quantifier],['Claim domain',`h ∈ [${i.claim_domain.h_min}, ${i.claim_domain.h_max}]`],['Assertion',i.assertion],['Initial-value reduction',i.reduction],['Units',i.units],['Search interval',`[${plan.search_min}, ${plan.search_max}], step ${plan.step}; ${plan.grid_points} grid points`],['Additional boundary probes',plan.boundary_probes.join(', ')],['Why these probes',plan.rationale],['Outside-claim policy',plan.outside_claim_policy],['Provenance',i.provenance]])field(fields,label,text);
    $('proposal-json').textContent=JSON.stringify(p,null,2);$('source').textContent=JSON.stringify({source:p.source,confirmation_digest:p.digest},null,2);
    $('proposal').hidden=false;$('proposal-empty').hidden=true;$('confirmed').disabled=false;$('state').textContent='Plan ready';
  }catch(error){if(ticket===compileTicket)$('error').textContent=error.message;}
  finally{$('compile').textContent='Compile claim →';updateRun();}
};
$('run').onclick=async()=>{
  if(!proposal || !$('confirmed').checked || running)return;
  const frozen=clone(proposal), frozenParent=parent?clone(parent):null, started=revision;
  running=true;updateRun();$('run').textContent='Generating exact evidence…';$('error').textContent='';
  try {
    const body=await post('/api/review',{proposal:frozen,confirmed_digest:frozen.digest,parent:frozenParent});
    const r=body.report;
    if(r.confirmed_digest!==frozen.digest || canonical(r.proposal)!==canonical(frozen) || canonical(r.parent)!==canonical(frozenParent))throw new Error('Response is not bound to the confirmed proposal and parent. Result rejected.');
    const unsigned=clone(r);delete unsigned.review_id;
    if(await hash(unsigned)!==r.review_id)throw new Error('Review fingerprint mismatch. Result rejected.');
    let entry=history.find(item=>item.report.review_id===r.review_id);
    if(!entry){entry={report:clone(r),markdown:body.markdown};history.push(entry);}
    renderHistory();
    if(revision===started && proposal?.digest===frozen.digest && $('confirmed').checked){show(entry);$('state').textContent='Evidence ready';}
    else $('notice').textContent='An earlier confirmed review was added to session history. Your current input is preserved.';
  }catch(error){if(revision===started)$('error').textContent=error.message;else $('notice').textContent=`Earlier review failed: ${error.message}`;}
  finally{running=false;$('run').textContent='Generate exact evidence ↗';updateRun();}
};
function paragraph(parentElement,text,className='') {const p=document.createElement('p');p.textContent=text;if(className)p.className=className;parentElement.append(p);return p;}
function witness(container,w) {
  if(!w){paragraph(container,'Review the search counts and mathematical analysis.','hint');return;}
  paragraph(container,`rate = ${w.rate}; h = ${w.h}; y = ${w.initial_y} → y_next = ${w.next_y}. Squared amplitude: ${w.squared_before} → ${w.squared_after}; difference = ${w.squared_difference}.`,'witness');
}
function show(entry) {
  selected=entry;const r=entry.report;
  $('review-claim').textContent=r.proposal.raw_claim;
  const comp=$('comparison');comp.replaceChildren();
  const grid=document.createElement('section'),analysis=document.createElement('section');
  const gh=document.createElement('h3');gh.textContent='Search evidence';grid.append(gh);
  paragraph(grid,r.grid.status.replaceAll('_',' '),'outcome');paragraph(grid,r.grid.coverage,'hint');
  if(r.grid.witnesses.length)r.grid.witnesses.forEach(w=>witness(grid,w));else witness(grid,null);
  const ah=document.createElement('h3');ah.textContent='Mathematical analysis';analysis.append(ah);
  paragraph(analysis,r.analysis.status.replaceAll('_',' '),'outcome');paragraph(analysis,`${r.analysis.coverage}: h ∈ [${r.analysis.domain.h_min}, ${r.analysis.domain.h_max}].`,'hint');
  paragraph(analysis,r.analysis.derivation);paragraph(analysis,`Condition: ${r.analysis.condition}; threshold h = ${r.analysis.threshold}.`);
  if(r.analysis.witness)witness(analysis,r.analysis.witness);
  paragraph(analysis,r.analysis.verification,'hint');paragraph(analysis,r.analysis.boundary_behavior,'hint');comp.append(grid,analysis);
  $('stats').replaceChildren();for(const [key,value]of Object.entries(r.grid.counts)){const d=document.createElement('div');d.className='stat';const b=document.createElement('b');b.textContent=value;d.append(b,document.createTextNode(({evaluated:'evaluated',in_claim:'claim points',violations:'counterexamples',outside_claim:'exploration points',outside_violations:'exploration witnesses'})[key] || key.replaceAll('_',' ')));$('stats').append(d);}
  $('outside').replaceChildren();if(r.grid.outside_exploration.length)r.grid.outside_exploration.forEach(w=>witness($('outside'),w));else paragraph($('outside'),'Exploration results are recorded with the search plan.','hint');
  $('trace').replaceChildren();for(const sample of r.grid.samples){const t=document.createElement('span');t.className='tile'+(sample.holds?'':' fail')+(sample.in_claim?'':' outside');t.textContent=sample.in_claim?(sample.holds?'✓':'◆'):'○';t.tabIndex=0;t.title=`h=${sample.h}; ${sample.in_claim?'inside':'outside'} claim; ${sample.holds?'satisfies claim':'counterexample identified'}`;t.setAttribute('aria-label',t.title);$('trace').append(t);}
  $('lineage').replaceChildren();const chain=[];for(let item=r;item;item=item.parent)chain.unshift(item);
  for(const item of chain){const box=document.createElement('div');box.className='history-card';paragraph(box,item===r?'Selected review':'Preserved ancestor','eyebrow');paragraph(box,item.proposal.raw_claim);paragraph(box,`Grid: ${item.grid.status.replaceAll('_',' ')}`);paragraph(box,`Analysis: ${item.analysis.status.replaceAll('_',' ')}`);paragraph(box,`ID ${item.review_id.slice(0,12)}`,'hint');$('lineage').append(box);}
  $('evidence-summary').replaceChildren();for(const item of r.evidence_summary){const li=document.createElement('li');li.textContent=item;$('evidence-summary').append(li);}
  $('record').textContent=`Review ID: ${r.review_id}\nConfirmed digest: ${r.confirmed_digest}\nParent: ${r.parent_id || 'none'}\nReplay: python3 reproduce.py report.json\n${JSON.stringify(r.proposal.source,null,2)}`;
  $('results').hidden=false;
}
function revise(entry) {
  const p=entry.report.proposal;parent=clone(entry.report);$('claim').value=p.raw_claim;$('search-min').value=p.plan.search_min;$('search-max').value=p.plan.search_max;$('step').value=p.plan.step;
  invalidate();$('parent-label').textContent=`Revision of ${parent.review_id.slice(0,12)} · original review preserved`;$('notice').textContent='Edit the claim or search plan, then compile and confirm your revision.';$('claim').focus();
}
function download(entry,kind) {
  const blob=new Blob([kind==='json'?JSON.stringify(entry.report,null,2):entry.markdown],{type:kind==='json'?'application/json':'text/markdown'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download=`falsifylab-${entry.report.review_id.slice(0,12)}.${kind}`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function renderHistory() {
  $('history').replaceChildren();for(const entry of [...history].reverse()){
    const box=document.createElement('article');box.className='history-card';paragraph(box,entry.report.proposal.raw_claim);paragraph(box,`${entry.report.review_id.slice(0,12)} · Grid: ${entry.report.grid.status.replaceAll('_',' ')} · Analysis: ${entry.report.analysis.status.replaceAll('_',' ')}`,'hint');
    const actions=document.createElement('div');actions.className='downloads';for(const [label,fn]of [['View saved review',()=>show(entry)],['Revise this claim',()=>revise(entry)],['Save JSON + parents',()=>download(entry,'json')]]){const button=document.createElement('button');button.textContent=label;button.onclick=fn;actions.append(button);}box.append(actions);$('history').append(box);
  }
}
$('new').onclick=()=>{parent=null;invalidate();$('parent-label').textContent='New investigation';$('notice').textContent='Your current claim is ready to explore. Existing session history is preserved.';};
$('download-json').onclick=()=>{if(selected)download(selected,'json');};
$('download-md').onclick=()=>{if(selected)download(selected,'md');};
$('revise').onclick=()=>{if(selected)revise(selected);};
