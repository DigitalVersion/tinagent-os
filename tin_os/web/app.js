let sessions=[];
const $=(id)=>document.getElementById(id);
const esc=(value)=>String(value??'').replace(/[&<>"']/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function toast(message,error=false){const el=$('toast');el.textContent=message;el.className='toast show'+(error?' error':'');clearTimeout(toast.timer);toast.timer=setTimeout(()=>el.className='toast',3500)}
async function api(path,options={}){const response=await fetch(path,{headers:{'Content-Type':'application/json',...(options.headers||{})},...options});const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);return data}

function setModuleState(name,data){const el=$(name+'-state');if(!el)return;el.className=data.ready?'ready':data.installed?'':'missing';el.textContent=data.ready?`Ready on port ${data.port}`:data.installed?'Installed · press Start':'Not installed · run install/install-ai-apps.sh'}
async function loadStatus(){try{const data=await api('/api/status');$('live-dot').className='live';$('node-name').textContent=data.node;$('summary').textContent=`${data.running} running · ${data.sessions - data.running} idle`;$('live-dot').title='Live';setModuleState('opencode',data.modules.opencode);setModuleState('pi',data.modules.pi)}catch(error){$('live-dot').className='error';$('summary').textContent='Offline';toast(error.message,true)}}
async function loadSessions(){try{sessions=await api('/api/sessions');renderSessions()}catch(error){$('session-grid').innerHTML=`<div class="empty">${esc(error.message)}</div>`}}
async function loadAll(){await Promise.all([loadStatus(),loadSessions()])}

function renderSessions(){const query=$('search').value.trim().toLowerCase();const view=sessions.filter((item)=>`${item.name} ${item.command} ${item.path} ${item.output}`.toLowerCase().includes(query));if(!view.length){$('session-grid').innerHTML='<div class="empty">No matching sessions.</div>';return}$('session-grid').innerHTML=view.map((item)=>`<article class="session"><div class="session-head"><div><h3>${esc(item.name)}</h3><div class="meta">${esc(item.command||'shell')} · ${esc((item.path||'').split('/').pop()||item.path||'home')}</div></div><span class="state ${item.running?'':'idle'}">${item.running?'RUNNING':'IDLE'}</span></div><pre>${esc(item.output||'No output yet.')}</pre><div class="session-actions"><button onclick="copyAttach('${esc(item.name)}')">Copy attach</button><button class="danger" onclick="removeSession('${esc(item.name)}')">Stop</button></div></article>`).join('')}

async function startModule(name,button){const popup=window.open('about:blank','_blank');button.disabled=true;button.dataset.label=button.textContent;button.textContent='Starting…';try{const data=await api(`/api/modules/${name}/start`,{method:'POST',body:'{}'});toast(`${name==='opencode'?'OpenCode Web':'Pi Web'} is ready`);if(popup)popup.location=data.url;else location.href=data.url;await loadStatus()}catch(error){if(popup)popup.close();toast(error.message,true)}finally{button.disabled=false;button.textContent=button.dataset.label}}

async function createSession(){const raw=prompt('Session name:',`work-${Date.now().toString(36).slice(-4)}`);if(!raw)return;const agent=prompt('Start with bash, opencode, pi, claude, or codex:','bash')||'bash';try{await api('/api/sessions',{method:'POST',body:JSON.stringify({name:raw.trim(),agent:agent.trim()})});toast(`Session ${raw} is ready`);await loadAll()}catch(error){toast(error.message,true)}}
async function removeSession(name){if(!confirm(`Stop session "${name}"? Running work will be interrupted.`))return;try{await api(`/api/sessions/${encodeURIComponent(name)}`,{method:'DELETE'});toast(`Stopped ${name}`);await loadAll()}catch(error){toast(error.message,true)}}
function copyAttach(name){const command=`tmux attach -t ${name}`;if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(command).then(()=>toast('Attach command copied')).catch(()=>prompt('Copy this command:',command))}else{prompt('Copy this command:',command)}}

loadAll();setInterval(loadAll,5000);
