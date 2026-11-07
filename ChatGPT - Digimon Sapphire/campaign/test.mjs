import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import * as game from './state.mjs';
const data=JSON.parse(readFileSync(new URL('./digimon.json',import.meta.url)));
const fresh=()=>game.createCampaign(data,'test_profile');
const clone=value=>JSON.parse(JSON.stringify(value));
function ready(){let s=fresh();for(const who of ['tai','matt'])for(let badge=1;badge<=8;badge++)s=game.awardBadge(data,s,who,badge);for(const who of ['tai','matt']){const j=s.journeys[who],p=j.partners[j.starterId];j.mapId='convergence_gate';p.formId=who==='tai'?'wargreymon':'metalgarurumon';p.level=50;p.bond=90;p.currentHp=game.calculateStats(data.forms[p.formId],p).hp;}return game.reunite(data,s);}
test('37 forms, eight families, valid paths and GBA mappings',()=>{assert(game.validateCatalog(data));assert.equal(Object.keys(data.forms).length,37);assert.equal(Object.keys(data.families).length,8);for(const form of Object.values(data.forms))assert(Number.isInteger(form.gbaSlot));});
test('HP formula and neutral nature have expected values',()=>{const p=game.createPartner(data,{id:'a',formId:'agumon',owner:'tai',origin:'starter',level:50});assert.equal(p.currentHp,105);assert.equal(game.calculateStats(data.forms.agumon,p).attack,65);p.nature={up:'attack',down:'defense'};assert.equal(game.calculateStats(data.forms.agumon,p).attack,71);assert.equal(game.calculateStats(data.forms.agumon,p).defense,40);});
test('IV/EV boundaries reject impossible allocations',()=>{const p=fresh().journeys.tai.partners['test_profile:tai:starter'];p.ivs.hp=32;assert.throws(()=>game.calculateStats(data.forms.agumon,p));p.ivs.hp=0;for(const k of game.STAT_KEYS)p.evs[k]=252;assert.throws(()=>game.calculateStats(data.forms.agumon,p));});
test('Tai badge changes never mutate Matt or the input save',()=>{const s=fresh(),before=JSON.stringify(s);const n=game.awardBadge(data,s,'tai',1);assert.equal(JSON.stringify(s),before);assert.deepEqual(n.journeys.matt,s.journeys.matt);assert.equal(n.journeys.tai.party.length,2);});
test('Duplicate victory is idempotent; skipped badges are rejected',()=>{const s=game.awardBadge(data,fresh(),'tai',1);assert.deepEqual(game.awardBadge(data,s,'tai',1),s);assert.throws(()=>game.awardBadge(data,s,'tai',3));});
test('Stale revisions cannot overwrite newer progress',()=>{const s=game.awardBadge(data,fresh(),'tai',1);assert.throws(()=>game.awardBadge(data,s,'matt',1,0),/Stale/);});
test('Both teams recruit all eight families; overflow goes to storage',()=>{const s=ready();for(const j of Object.values(s.journeys)){assert.equal(j.party.length,6);assert.equal(j.storage.length,2);assert.equal(new Set(Object.values(j.partners).map(p=>p.familyId)).size,8);assert.equal(j.claimedRewards.length,8);}});
test('Full storage queues a reward and later claims it exactly once',()=>{const small={...data,partyLimit:1,storageLimit:0};let s=game.awardBadge(small,fresh(),'tai',1);assert.deepEqual(s.journeys.tai.pendingRewards,[1]);assert.equal(s.journeys.tai.claimedRewards.length,0);s=game.claimPendingRewards(data,s,'tai');assert.equal(s.journeys.tai.party.length,2);assert.deepEqual(game.claimPendingRewards(data,s,'tai'),s);});
test('Reunion requires BOTH eight-badge journeys at the gate',()=>{assert.throws(()=>game.reunite(data,fresh()));let s=fresh();for(let i=1;i<=8;i++)s=game.awardBadge(data,s,'tai',i);s.journeys.tai.mapId='convergence_gate';assert.throws(()=>game.reunite(data,s));});
test('Fusion consumes no source partners and cannot activate twice',()=>{
  const s=ready(),before=clone(s);
  before.shared.fusionTriggered = true; // Expected state after fusion
  const battle=game.startFinalBattle(data,s,'final-1');
  const fused=game.activateFusion(data,s,battle);
  assert.equal(fused.fusion.partner.formId,'omegamon');
  assert.equal(fused.fusion.lockedSourceIds.length,2);
  // Compare save state without fusionTriggered
  const sWithoutFusion = clone(s);
  sWithoutFusion.shared.fusionTriggered = before.shared.fusionTriggered;
  assert.deepEqual(sWithoutFusion, before);
  assert.equal(s.shared.fusionTriggered,true);
  assert.throws(()=>game.activateFusion(data,s,fused));
});
test('Recruited copies cannot replace the protagonists\' original partners',()=>{const s=ready(),j=s.journeys.tai;const copy=Object.values(j.partners).find(p=>p.origin!=='starter');copy.formId='wargreymon';copy.familyId='agumon';copy.level=50;copy.bond=100;copy.currentHp=1;j.leadId=copy.instanceId;assert.throws(()=>game.activateFusion(data,s,game.startFinalBattle(data,s,'final-2')),/original lead/);});
test('Fainted, low-bond, and stale-snapshot fusion attempts fail',()=>{for(const change of [s=>s.journeys.tai.partners[s.journeys.tai.starterId].currentHp=0,s=>s.journeys.matt.partners[s.journeys.matt.starterId].bond=79]){const s=ready();change(s);assert.throws(()=>game.activateFusion(data,s,game.startFinalBattle(data,s,'final-3')));}const s=ready(),b=game.startFinalBattle(data,s,'final-4');s.revision++;assert.throws(()=>game.activateFusion(data,s,b),/stale/);});
test('Victory, loss, and escape all remove the temporary fusion',()=>{const s=ready();for(const outcome of ['won','lost','fled']){const b=game.activateFusion(data,s,game.startFinalBattle(data,s,'final-'+outcome));assert.equal(game.endFinalBattle(b,outcome).fusion,null);}});
test('Save round-trip preserves both journeys; bad versions and duplicate IDs fail',()=>{const s=ready();assert.deepEqual(game.loadSave(data,game.serializeSave(data,s)),s);const bad=clone(s);bad.schemaVersion=999;assert.throws(()=>game.loadSave(data,JSON.stringify(bad)));const duplicate=clone(s);duplicate.journeys.tai.party.push(duplicate.journeys.tai.party[0]);assert.throws(()=>game.validateSave(data,duplicate));});
test('Digivolution gates level/bond/crest and retains fainted state',()=>{let s=fresh();const j=s.journeys.tai,p=j.partners[j.starterId];assert.throws(()=>game.digivolve(data,s,'tai',p.instanceId,'greymon'));p.level=20;p.bond=30;p.currentHp=0;s=game.digivolve(data,s,'tai',p.instanceId,'greymon');assert.equal(s.journeys.tai.partners[p.instanceId].currentHp,0);assert.equal(s.journeys.tai.partners[p.instanceId].formId,'greymon');});
