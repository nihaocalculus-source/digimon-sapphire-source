const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const names = {sihappiere:'Digimon Sapphire',ruby:'Digimon Ruby'};
let toastTimer, activeGame=null, started=false, launchTrigger=null, confirmation=null;
let availability={sihappiere:false,ruby:false};

function updateNavigation(){
 const section=location.hash==='#field-guide'?'#field-guide':'#portal';
 $$('.nav[href^="#"]').forEach(link=>{
  const current=link.getAttribute('href')===section;
  link.classList.toggle('active',current);
  if(current)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');
 });
}
window.addEventListener('hashchange',updateNavigation);
updateNavigation();

function toast(message){$('#toast').textContent=message;$('#toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),5000);}
function confirmExit(){
 if(confirmation)return Promise.resolve(false);
 $('#confirm-modal').showModal();$('#confirm-cancel').focus();
 return new Promise(resolve=>confirmation=resolve);
}
function resolveConfirmation(value){$('#confirm-modal').close();const resolve=confirmation;confirmation=null;resolve?.(value);}
$('#confirm-ok').addEventListener('click',()=>resolveConfirmation(true));
$('#confirm-cancel').addEventListener('click',()=>resolveConfirmation(false));
$('#confirm-modal').addEventListener('cancel',event=>{event.preventDefault();resolveConfirmation(false);});

$$('[data-game]').forEach(button=>{
 button.disabled=true;
 button.addEventListener('click',()=>{
  const game=button.dataset.game;
  if(!availability[game])return;
  activeGame=game;started=false;launchTrigger=button;
  $('#player-title').textContent=names[game];
  $('#player-save-status').textContent='Save Data captures your current position.';
  const frame=document.createElement('iframe');frame.src='player.html?game='+game;frame.title=names[game]+' emulator';frame.allow='autoplay; fullscreen; gamepad';frame.allowFullscreen=true;
  $('#player-frame').replaceChildren(frame);$('#player-modal').showModal();
 });
});
async function closePlayer(){
 if(started&&!await confirmExit())return;
 $('#player-modal').close();$('#player-frame').replaceChildren();started=false;activeGame=null;launchTrigger?.focus();
}
$('#close-player').addEventListener('click',closePlayer);
$('#player-modal').addEventListener('cancel',event=>{event.preventDefault();closePlayer();});
window.addEventListener('beforeunload',event=>{if(started){event.preventDefault();event.returnValue='';}});
window.addEventListener('message',event=>{
 if(event.origin!==location.origin||event.source!==$('#player-frame iframe')?.contentWindow||event.data?.game!==activeGame)return;
 if(event.data.type==='game-started')started=true;
 if(event.data.type==='checkpoint-status' && event.data.capturedAt)$('#player-save-status').textContent='Checkpoint stored '+new Date(event.data.capturedAt).toLocaleTimeString();
 if(event.data.type==='checkpoint-status' && event.data.status==='storage-error')toast('Checkpoint storage failed. Open Save Data and download your JSON backup.');
});

async function checkGames(){
 try{
  const response=await fetch('/api/health',{cache:'no-store'});if(!response.ok)throw Error();
  const health=await response.json();if(health.app!=='digimon-sihappiere')throw Error();
  availability={sihappiere:health.games?.sihappiere===true,ruby:health.games?.ruby===true};
  for(const game of Object.keys(names)){
   $$(`[data-game="${game}"]`).forEach(button=>button.disabled=!availability[game]);
   $(`[data-status="${game}"]`).textContent=availability[game]?'GBA · READY TO PLAY':'GAME FILE NOT INSTALLED';
  }
  $('#system-status').textContent=availability.sihappiere&&availability.ruby?'● DIGITAL GATE READY':'GAME FILE MISSING';
 }catch{
  $('#system-status').textContent='LAUNCHER NEEDED';
  $$('[data-status]').forEach(element=>element.textContent='OPEN THE LAUNCHER');
  toast('Double-click Launch Digimon Sapphire.command to start the local arcade.');
 }
}
checkGames();
