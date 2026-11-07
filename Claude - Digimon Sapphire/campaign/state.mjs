/** Pure campaign prototype. This is not yet connected to cartridge RAM/save sectors. */
export const STAT_KEYS = ['hp', 'attack', 'defense', 'spAttack', 'spDefense', 'speed'];
const clone = value => JSON.parse(JSON.stringify(value));
const fail = message => { throw new Error(message); };
const int = (n, min, max) => Number.isInteger(n) && n >= min && n <= max;
const zeros = () => Object.fromEntries(STAT_KEYS.map(key => [key, 0]));

export function validateCatalog(data) {
  if (data.schemaVersion !== 1) fail('Unsupported catalog version');
  for (const [id, form] of Object.entries(data.forms)) {
    if (form.id !== id || !STAT_KEYS.every(k => int(form.baseStats[k], 1, 255))) fail(`Invalid base stats: ${id}`);
    if (form.familyId && !data.families[form.familyId]) fail(`Unknown family: ${id}`);
    for (const next of form.digivolutions) {
      if (!data.forms[next.to] || data.forms[next.to].familyId !== form.familyId) fail(`Invalid digivolution: ${id}`);
      if (!int(next.minimumLevel,1,100) || !int(next.minimumBond,0,100)) fail(`Invalid requirement: ${id}`);
    }
  }
  for (const family of Object.values(data.families)) {
    if (!family.formIds.includes(family.recruitForm) || family.formIds.some(id => data.forms[id]?.familyId !== family.id)) fail(`Invalid family: ${family.id}`);
  }
  return true;
}

export function calculateStats(form, instance) {
  if (!int(instance.level, 1, 100)) fail('Level must be 1..100');
  if (!STAT_KEYS.every(k => int(instance.ivs[k], 0, 31) && int(instance.evs[k], 0, 252)) || Object.values(instance.evs).reduce((a,b) => a+b,0)>510) fail('Invalid IV/EV allocation');
  if (instance.nature.up && !STAT_KEYS.slice(1).includes(instance.nature.up)) fail('Invalid nature');
  if (instance.nature.down && !STAT_KEYS.slice(1).includes(instance.nature.down)) fail('Invalid nature');
  return Object.fromEntries(STAT_KEYS.map(key => {
    const value = Math.floor((2*form.baseStats[key]+instance.ivs[key]+Math.floor(instance.evs[key]/4))*instance.level/100);
    const neutral = instance.nature.up === instance.nature.down;
    const modifier = neutral ? 100 : key === instance.nature.up ? 110 : key === instance.nature.down ? 90 : 100;
    return [key, key === 'hp' ? value+instance.level+10 : Math.floor((value+5)*modifier/100)];
  }));
}

export function createPartner(data, {id, formId, owner, origin, level=5, bond=10}) {
  const form = data.forms[formId];
  if (!id || !form || !['tai','matt'].includes(owner) || !int(bond,0,100)) fail('Invalid partner');
  const p = {instanceId:id,familyId:form.familyId,formId,owner,origin,level,experience:level**3,bond,
    ivs:zeros(),evs:zeros(),nature:{up:null,down:null},moves:[],status:'healthy',heldItem:null};
  p.currentHp = calculateStats(form,p).hp;
  return p;
}

export function createCampaign(data, campaignId) {
  validateCatalog(data);
  if (typeof campaignId!=='string' || !/^[a-zA-Z0-9_-]{1,64}$/.test(campaignId)) fail('A stable campaign ID is required');
  const save = {schemaVersion:1,campaignId,revision:0,activeJourney:'tai',shared:{reunited:false},journeys:{}};
  for (const key of ['tai','matt']) {
    const config=data.protagonists[key], id=`${campaignId}:${key}:starter`;
    const starter=createPartner(data,{id,formId:config.starter,owner:key,origin:'starter'});
    save.journeys[key]={protagonist:key,revision:0,mapId:config.startMap,position:{x:5,y:5},followerPosition:{x:4,y:5},badges:[],
      flags:[],claimedRewards:[],pendingRewards:[],money:3000,inventory:{},partners:{[id]:starter},party:[id],storage:[],starterId:id,leadId:id,followerId:`${id}:follower`};
  }
  return save;
}

export function validateSave(data, save) {
  if (save?.schemaVersion!==1 || !int(save.revision,0,Number.MAX_SAFE_INTEGER) || !['tai','matt'].includes(save.activeJourney)) fail('Unsupported or invalid save');
  if (typeof save.campaignId!=='string' || !save.campaignId || typeof save.shared?.reunited!=='boolean') fail('Invalid campaign metadata');
  const seen=new Set();
  for (const key of ['tai','matt']) {
    const j=save.journeys?.[key];
    if (!j || j.protagonist!==key || !int(j.revision,0,Number.MAX_SAFE_INTEGER) || typeof j.mapId!=='string') fail('Missing journey');
    if (!Array.isArray(j.badges) || j.badges.length>8 || new Set(j.badges).size!==j.badges.length || j.badges.some((b,i)=>b!==i+1)) fail('Invalid badges');
    if (!Array.isArray(j.party) || !Array.isArray(j.storage) || j.party.length>data.partyLimit || j.storage.length>data.storageLimit) fail('Invalid party or storage size');
    const owned=[...j.party,...j.storage];
    if (new Set(owned).size!==owned.length || owned.length!==Object.keys(j.partners).length || !j.party.includes(j.leadId) || !j.partners[j.starterId]) fail('Invalid partner placement');
    if (j.partners[j.starterId].origin!=='starter' || j.partners[j.starterId].familyId!==data.protagonists[key].starter) fail('Invalid original starter');
    for (const id of owned) {
      const p=j.partners[id], form=data.forms[p?.formId];
      if (seen.has(id) || !p || p.instanceId!==id || p.owner!==key || !form || p.familyId!==form.familyId || !int(p.bond,0,100)) fail('Invalid owned partner');
      seen.add(id); const stats=calculateStats(form,p);
      if (!int(p.currentHp,0,stats.hp)) fail('Invalid current HP');
    }
    if (!Array.isArray(j.claimedRewards) || new Set(j.claimedRewards).size!==j.claimedRewards.length || j.claimedRewards.some(b=>!j.badges.includes(b))) fail('Invalid rewards');
    if (!Array.isArray(j.pendingRewards) || new Set(j.pendingRewards).size!==j.pendingRewards.length || j.pendingRewards.some(b=>!j.badges.includes(b)||j.claimedRewards.includes(b))) fail('Invalid pending rewards');
  }
  if (save.shared.reunited && !['tai','matt'].every(k=>save.journeys[k].badges.length===8)) fail('Invalid reunion state');
  return true;
}
function transaction(data, save, expectedRevision, update) {
  validateSave(data,save);
  if (save.revision!==expectedRevision) fail('Stale save revision; reload before writing');
  const next=clone(save); const changed=update(next);
  if (!changed) return next;
  next.revision++; validateSave(data,next); return next;
}
function claim(data, save, key, badge) {
  const j=save.journeys[key], familyId=data.protagonists[key].badgeRewards[badge-1];
  if (j.claimedRewards.includes(badge)) return false;
  if (familyId && j.party.length>=data.partyLimit && j.storage.length>=data.storageLimit) {
    if (!j.pendingRewards.includes(badge)) j.pendingRewards.push(badge);
    return false;
  }
  if (familyId) {
    const id=`${save.campaignId}:${key}:badge-${badge}`;
    const partner=createPartner(data,{id,formId:data.families[familyId].recruitForm,owner:key,origin:`badge:${badge}`,level:Math.min(45,5+badge*4),bond:20});
    j.partners[id]=partner;
    (j.party.length<data.partyLimit ? j.party : j.storage).push(id);
  }
  j.claimedRewards.push(badge);j.pendingRewards=j.pendingRewards.filter(n=>n!==badge);
  return true;
}
/** Only the battle engine should dispatch this after a verified boss victory. */
export function awardBadge(data, save, key, badge, expectedRevision=save.revision) {
  if (!['tai','matt'].includes(key) || !int(badge,1,8)) fail('Invalid badge event');
  return transaction(data,save,expectedRevision,next=>{
    const j=next.journeys[key];
    if (j.badges.includes(badge)) return false; // Replaying a victory cannot duplicate a partner.
    if (badge!==j.badges.length+1) fail('Boss progression must be sequential');
    j.badges.push(badge);claim(data,next,key,badge);j.revision++;return true;
  });
}
export function claimPendingRewards(data,save,key,expectedRevision=save.revision) {
  if (!['tai','matt'].includes(key)) fail('Invalid journey');
  return transaction(data,save,expectedRevision,next=>{
    let changed=false;for(const badge of [...next.journeys[key].pendingRewards]) changed=claim(data,next,key,badge)||changed;
    if(changed)next.journeys[key].revision++;return changed;
  });
}
export function digivolve(data,save,key,instanceId,to,expectedRevision=save.revision) {
  return transaction(data,save,expectedRevision,next=>{
    const j=next.journeys[key],p=j?.partners[instanceId],edge=p&&data.forms[p.formId].digivolutions.find(e=>e.to===to);
    if(!edge || p.level<edge.minimumLevel || p.bond<edge.minimumBond || (edge.requiredCrest && !j.flags.includes(`crest:${edge.requiredCrest}`))) fail('Digivolution requirements not met');
    const oldMax=calculateStats(data.forms[p.formId],p).hp;
    p.formId=to;const newMax=calculateStats(data.forms[to],p).hp;
    p.currentHp=p.currentHp===0?0:Math.max(1,Math.floor(p.currentHp*newMax/oldMax));j.revision++;return true;
  });
}
/** A native map event will set mapId; arrival does not copy another journey's inventory. */
export function reunite(data,save,expectedRevision=save.revision) {
  return transaction(data,save,expectedRevision,next=>{
    if(next.shared.reunited)return false;
    if(!['tai','matt'].every(k=>next.journeys[k].badges.length===8 && next.journeys[k].mapId==='convergence_gate')) fail('Both journeys must collect all 8 Digital Keys and reach the Convergence Gate');
    next.shared.reunited=true;
    next.shared.fusionTriggered=false;
    return true;
  });
}
export function startFinalBattle(data,save,battleId) {
  validateSave(data,save);
  if(!save.shared.reunited || !battleId) fail('The reunion must happen first');
  return {battleId,campaignId:save.campaignId,saveRevision:save.revision,phase:'active',fusionUsed:false,fusion:null};
}
export function activateFusion(data,save,battle,recipeId='omegamon') {
  validateSave(data,save);const recipe=data.fusionRecipes[recipeId];
  if(!recipe || !save.shared.reunited || battle.phase!=='active' || battle.fusionUsed || battle.campaignId!==save.campaignId || battle.saveRevision!==save.revision) fail('Fusion is unavailable or the battle snapshot is stale');
  const partners=recipe.participants.map(req=>{
    const j=save.journeys[req.journey],p=j.partners[j.leadId];
    if(j.mapId!==recipe.requiredMap || j.badges.length<recipe.requiredBadgeCount || j.leadId!==j.starterId || p.formId!==req.form || p.familyId!==req.family || p.level<recipe.minimumLevel || p.bond<recipe.minimumBond || p.currentHp===0 || p.status!=='healthy') fail('Both original lead partners must have collected all 8 Digital Keys and be ready for fusion');
    return p;
  });
  const next=clone(battle),form=data.forms[recipe.resultForm];
  const merged=createPartner(data,{id:`${battle.battleId}:fusion`,formId:form.id,owner:'tai',origin:'dna_digivolution',level:Math.floor(partners.reduce((n,p)=>n+p.level,0)/partners.length),bond:100});
  next.fusionUsed=true;
  next.fusion={recipeId,partner:merged,sourceIds:partners.map(p=>p.instanceId),lockedSourceIds:partners.map(p=>p.instanceId)};
  save.shared.fusionTriggered=true;
  return next;
}
export function endFinalBattle(battle,outcome) {
  if(!['won','lost','fled'].includes(outcome) || battle.phase!=='active')fail('Invalid battle end');
  return {...clone(battle),phase:'ended',outcome,fusion:null};
}
export function serializeSave(data,save){validateSave(data,save);return JSON.stringify(save);}
export function loadSave(data,text){const save=JSON.parse(text);validateSave(data,save);return save;}
