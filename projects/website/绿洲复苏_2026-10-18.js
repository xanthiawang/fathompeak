/* Public interaction prototype. All events and coupons are demonstrations; no billing API. */
(function (global) {
  'use strict';
  const VERSION=6, NEED=100, STEP=25;
  const CONFIG=Object.freeze({id:'demo-spend-20261018',centsPerGrowth:1000,water:100,camp:150,birds:200,maxNetCents:1000000});
  const SPECIES={sun:{name:'暖阳树',kind:'常规',desc:'圆叶与赭金果实，留住每一份日常的积累。'},moon:{name:'月辉树',kind:'珍藏',desc:'银绿窄叶与月牙果实。三棵成熟后领取珍藏种子，下一棵自动种下。'}};
  const STAGES=['种子','发芽','树苗','成树','成熟'];
  /* 买 100 送 100（2026-10-28）：每实付消费 ¥100 长成一棵树，每棵送 100 万词元；第 3 棵加月辉种子，每 6 棵加纪念章 */
  const TOKENS=1000000, REWARD_CENTS=10000, perTree=n=>({n,cents:0,tokens:TOKENS,title:'买 100 送 100',detail:'100 万词元'+(n%10===0?' + 绿洲纪念章':'')+(n===30?' + 月辉种子':''),...(n===30?{rare:true}:{}),...(n%10===0?{badge:true}:{})});
  const POLICY=[perTree(1),perTree(2),perTree(3)];
  const regionName=i=>['营地','溪畔','林地'][i%3]+(i>2?' · '+(Math.floor(i/3)+1):'');
  const fresh=()=>({version:VERSION,policy:CONFIG.id,revision:0,netCents:0,highWaterCents:0,trees:[],regions:[{id:0,name:regionName(0),water:false,camp:false,birds:false}],current:null,rareSeeds:0,badges:[],events:[],rewards:[],receipts:[],log:[],motion:'system'});
  const mature=s=>s.trees.filter(t=>t.energy===NEED).length;
  const current=s=>s.trees.find(t=>t.id===s.current);
  const stage=t=>Math.min(4,Math.floor(t.energy/STEP));
  const progress=(s,r)=>s.trees.filter(t=>t.region===r).reduce((n,t)=>n+t.energy,0)/(NEED*2);
  const localMature=(s,r)=>s.trees.filter(t=>t.region===r&&t.energy===NEED).length;
  const environment=(s,r)=>Math.floor(progress(s,r)*100);
  const money=c=>(c/100).toFixed(2);
  const yuan=g=>(g*CONFIG.centsPerGrowth/100).toLocaleString('en-US');
  const eligible=(s,r)=>s.netCents>=r.n*REWARD_CENTS;
  function parseMoney(value){const m=/^(\d{1,5})(?:\.(\d{1,2}))?$/.exec(String(value).trim());if(!m)throw Error('请输入最多两位小数的正金额。');const cents=Number(m[1])*100+Number((m[2]||'').padEnd(2,'0'));if(cents<=0||cents>CONFIG.maxNetCents)throw Error('试玩金额范围为 ¥0.01–¥10,000。');return cents;}
  function reduce(previous,a,now=Date.now()) {
    const s=JSON.parse(JSON.stringify(previous));
    const note=(title,detail)=>s.log.unshift({title,detail,at:now});
    const fail=m=>{throw new Error(m)};
    const reconcile=()=>{
      const oldHigh=s.highWaterCents;s.highWaterCents=Math.max(oldHigh,s.netCents);
      const growth=s.highWaterCents/CONFIG.centsPerGrowth,count=Math.ceil(growth/NEED);
      for(let i=0;i<count;i++){
        const region=Math.floor(i/2),energy=Math.min(NEED,(s.highWaterCents-i*NEED*CONFIG.centsPerGrowth)/CONFIG.centsPerGrowth);
        if(!s.regions[region]){s.regions.push({id:region,name:regionName(region),water:false,camp:false,birds:false});note('开放'+regionName(region),'新增消费自动开启区域，旧景观保留');}
        let t=s.trees[i];if(!t){const rare=s.rareSeeds>0&&s.netCents>=3*NEED*CONFIG.centsPerGrowth;if(rare)s.rareSeeds--;t={id:CONFIG.id+'-tree-'+i,type:rare?'moon':'sun',region,slot:i%2,energy:0,at:now,name:''};s.trees.push(t);note('种下'+SPECIES[t.type].name,'消费自动播种 · '+regionName(region));}
        if(t.energy<NEED&&energy===NEED){t.matureAt=now;note('一棵树成熟了',SPECIES[t.type].name+'留在'+regionName(region));}t.energy=energy;
      }
      s.current=s.trees.find(t=>t.energy<NEED)?.id||null;
      for(const r of s.regions){const local=Math.min(200,Math.max(0,growth-r.id*200));for(const p of ['water','camp','birds']){if(!r[p]&&local>=CONFIG[p]){r[p]=true;note(({water:'溪水自动接通',camp:'木桥与营地焕新',birds:'溪畔小鸟安家'})[p],r.name+' · 消费里程碑');}}}
      const milestones=[...POLICY];for(let n=POLICY.length+1;n<=Math.floor(s.highWaterCents/REWARD_CENTS);n++)milestones.push(perTree(n));
      for(const m of milestones){if(s.highWaterCents>=m.n*REWARD_CENTS&&!s.rewards.some(r=>r.n===m.n)){s.rewards.push({...m,id:CONFIG.id+'-milestone-'+m.n,status:'ready',at:now});note('解锁奖励',m.detail+'，可自行领取，成长继续');}}
      for(const r of s.rewards)r.suspended=r.status!=='used'&&!eligible(s,r);
    };
    if(a.type==='consume'||a.type==='refund') {
      if(!a.id||typeof a.id!=='string'||a.id.length>160||a.status!=='settled'||!Number.isSafeInteger(a.cents)||a.cents<=0||a.cents>CONFIG.maxNetCents)fail('仅接受有效的已结算模拟流水，金额用整数分。');
      const prior=s.events.find(e=>e.id===a.id);
      if(prior){if(prior.kind!==a.type||prior.cents!==a.cents||(prior.original||'')!==(a.original||''))fail('流水 ID 冲突：金额或类型与原记录不同。');return previous;}
      if(a.type==='refund'){
        const original=s.events.find(e=>e.id===a.original&&e.kind==='consume');if(!original)fail('退款必须关联原消费流水。');
        const returned=s.events.filter(e=>e.kind==='refund'&&e.original===a.original).reduce((n,e)=>n+e.cents,0);if(returned+a.cents>original.cents)fail('累计退款不能超过原消费。');
      }
      const next=s.netCents+(a.type==='consume'?a.cents:-a.cents);if(!Number.isSafeInteger(next)||next<0||next>CONFIG.maxNetCents)fail('试玩净消费已超出 ¥10,000 范围，请重置后继续。');
      s.events.push({id:a.id,kind:a.type,cents:a.cents,status:'settled',...(a.type==='refund'?{original:a.original}:{}),at:now});s.netCents=next;
      note(a.type==='consume'?'模拟消费已结算':'模拟退款已冲正','¥'+money(a.cents)+' · 净消费 ¥'+money(s.netCents));reconcile();
    } else if(a.type==='claim') {
      if(a.role==='member')fail('组织奖励由管理员领取和使用。');
      const r=s.rewards.find(r=>r.id===a.id);if(!r||r.status!=='ready'||!eligible(s,r))fail('这份奖励已经领取，或净消费尚未达到门槛。');
      r.status='available';r.claimedAt=now;r.expiresAt=now+14*86400000;if(r.rare)s.rareSeeds++;if(r.badge&&!s.badges.includes(r.n))s.badges.push(r.n);
      note('领取'+r.title,'100 万词元'+(r.rare?' + 月辉种子':'')+'，调用时优先抵扣');
    } else if(a.type==='redeem') {
      if(a.role==='member')fail('组织奖励由管理员领取和使用。');
      const r=s.rewards.find(r=>r.id===a.id);if(!r||r.status!=='available'||!eligible(s,r))fail('这张券已使用，或退款后暂不可用。');
      if(r.expiresAt<=now)fail('这张试玩券已过期。');
      if(!Number.isInteger(a.total)||a.total<=0||a.total>10000||!['chat','batch'].includes(a.model))fail('请选择有效的试玩订单。');
      const discount=Math.min(a.total,r.cents);r.status='used';r.usedAt=now;
      s.receipts.push({id:'receipt-'+r.id,coupon:r.id,total:a.total,discount,due:a.total-discount,model:a.model,at:now});
      note('试玩抵扣完成','原额 ¥'+money(a.total)+' − 券 ¥'+money(discount)+' = 演示应付 ¥'+money(a.total-discount)+'；没有真实扣款，未提交支付结算');
    } else if(a.type==='motion') {
      if(!['system','reduce'].includes(a.value))fail('无效的动效设置。');s.motion=a.value;
    } else if(a.type==='rename') {
      const t=s.trees.find(t=>t.id===a.id);if(!t)fail('没有找到这棵树。');t.name=String(a.name||'').trim().slice(0,20);
    } else fail('无法识别这次操作。');
    s.revision++;return s;
  }
  const engine={fresh,reduce,mature,current,stage,progress,environment,localMature,POLICY,NEED,CONFIG,parseMoney,eligible};
  if(typeof module!=='undefined'&&module.exports)module.exports=engine;
  if(!global.document)return;
  global.mountFPOasis=function({root,navigate,toast,getUser}) {
    if(!root)return;
    const E=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const B=(label,a,v='',primary=false,disabled=false)=>`<button type="button" class="btn ${primary?'black':'gray'} sm" data-og="${a}" data-value="${E(v)}" ${disabled?'disabled':''}>${label}</button>`;
    const ART='art/oasis/oasis-growth_etched_2026-10-18.webp', START='art/oasis/oasis-region-withered_etched_2026-10-18.webp', GREEN='art/oasis/oasis-region-revived_etched_2026-10-18.webp', CAMP='art/oasis/oasis-region-camp_etched_2026-10-18.webp', BIRD='art/oasis/oasis-bird_etched_2026-10-18.webp';
    const art=(t,extra='')=>`<span class="og-art ${extra} ${t.type==='moon'?'rare':''}" role="img" aria-label="${SPECIES[t.type].name} · ${STAGES[stage(t)]}" style="background-image:url('${ART}');--col:${stage(t)*25}%"></span>`;
    const dlg=document.getElementById('oaDlg'), title=document.getElementById('oaDlgT'), body=document.getElementById('oaDlgB');
    const media=matchMedia('(prefers-reduced-motion: reduce)');
    let s=fresh(),key='',view=0,busy=false,storageError='',previewBefore=false,returnFocus=null;
    const role=()=>getUser()?.role||'personal';

    const scope=()=>{const u=getUser()||{};return 'fp-oasis-spend-v6:'+((u.role==='admin'||u.role==='member')?'org:'+String(u.org||'preview-org'):'person:'+String(u.email||u.phone||'preview-personal'));};
    const reduced=()=>s.motion==='reduce'||media.matches;
    function read(){try{const raw=localStorage.getItem(key);if(!raw)return fresh();const v=JSON.parse(raw);if(!v||v.version!==VERSION||v.policy!==CONFIG.id||!['trees','regions','rewards','events','receipts','log','badges'].every(k=>Array.isArray(v[k]))||!v.regions.length||!['netCents','highWaterCents','rareSeeds','revision'].every(k=>Number.isSafeInteger(v[k])&&v[k]>=0)||v.netCents>v.highWaterCents||v.highWaterCents>CONFIG.maxNetCents||v.trees.some(t=>!t||!SPECIES[t.type]||!Number.isFinite(t.energy)||t.energy<0||t.energy>NEED||!Number.isInteger(t.region)||!v.regions[t.region])||v.regions.some((r,i)=>!r||r.id!==i)||v.rewards.some(r=>!r||!['ready','available','used'].includes(r.status)||!Number.isSafeInteger(r.n)||r.n<1)||v.events.some(e=>!e||!['consume','refund'].includes(e.kind)||!Number.isSafeInteger(e.cents)||e.cents<=0)||v.log.some(l=>!l)||v.receipts.some(r=>!r))throw Error('存档格式不匹配');storageError='';return v;}catch(err){storageError='试玩存档暂时无法读取，请在设置中重置试玩或检查浏览器存储权限。';return fresh();}}
    function sync(){const next=scope();if(next!==key){key=next;s=read();view=current(s)?.region??s.regions.length-1;previewBefore=false;render();}}
    function close(){if(dlg.open)dlg.close();const fallback=root.querySelector('[data-og="rules"]');(returnFocus?.isConnected?returnFocus:fallback)?.focus({preventScroll:true});}
    function modal(h,html){returnFocus=document.activeElement;title.textContent=h;body.innerHTML=html;if(!dlg.open)dlg.showModal();else dlg.querySelector('button')?.focus({preventScroll:true});}
    const date=t=>new Date(t).toLocaleDateString('zh-CN',{month:'numeric',day:'numeric'});
    const uid=()=>crypto.randomUUID();
    async function act(action){
      if(busy)return false;sync();busy=true;root.setAttribute('aria-busy','true');const activeKey=key;
      const run=()=>{if(scope()!==activeKey)throw Error('账户已切换，请重试。');s=read();if(storageError&&action.type!=='reset')throw Error(storageError);const previous=s;
        const next=action.type==='reset'?fresh():reduce(s,{...action,role:role()});
        try{localStorage.setItem(activeKey,JSON.stringify(next));}catch(err){throw Error('未能保存试玩进度，这次操作没有生效。请检查浏览器存储空间。');}
        s=next;return previous;};
      try{const prev=navigator.locks?await navigator.locks.request(activeKey,run):run();
        if(action.type==='consume'&&s.highWaterCents>prev.highWaterCents)view=s.regions.length-1;
        if(action.type==='reset'){view=0;storageError='';}
        previewBefore=false;render();if(['consume'].includes(action.type))root.querySelector('.og-world')?.scrollIntoView({block:'nearest',behavior:'instant'});animate(action,prev);return true;
      }catch(err){toast(err.message);return false;}finally{busy=false;root.removeAttribute('aria-busy');}
    }
    function animate(action,prev){
      if(reduced()||action.type!=='consume'||s.highWaterCents===prev.highWaterCents)return;
      const world=root.querySelector('.og-world');
      root.querySelectorAll('.og-tree .og-art').forEach(el=>el.animate([{opacity:.35,transform:'scale(.85)'},{opacity:1,transform:'scale(1.04)',offset:.75},{opacity:1,transform:'scale(1)'}],{duration:1100,easing:'ease-out'}));
      for(const [field,selector] of [['water','.og-green'],['camp','.og-camp'],['birds','.og-bird']])if(s.regions[view][field]&&!prev.regions[view]?.[field])root.querySelector(selector)?.animate([{opacity:0},{opacity:1}],{duration:1800,easing:'ease-in-out'});
      if(s.regions.length>prev.regions.length)world?.animate([{transform:'translateX(25px)',opacity:.3},{transform:'translateX(0)',opacity:1}],{duration:900,easing:'ease-out'});
    }
    function scene(){
      const region=s.regions.find(r=>r.id===view)||s.regions[0],p=progress(s,region.id),trees=s.trees.filter(t=>t.region===region.id),c=current(s);
      const phase=region.birds?'繁盛 · 生命来访':region.camp?'安居 · 营地建成':region.water?'成荫 · 溪流接通':p?'生根 · 树木成长':'初始 · 枯萎待复苏';
      const tabs=s.regions.map(r=>`<button type="button" data-og="region" data-value="${r.id}" aria-current="${r.id===view?'true':'false'}">${E(r.name)}${r.birds?' ✓':''}</button>`).join('');
      const planted=trees.map(t=>`<button type="button" data-og="tree" data-value="${E(t.id)}" data-tree-id="${E(t.id)}" class="og-tree slot-${t.slot}" aria-label="${E(t.name||SPECIES[t.type].name)}，${STAGES[stage(t)]}">${art(t)}<span class="og-tree-label">${E(t.name||SPECIES[t.type].name)} · ${STAGES[stage(t)]}</span></button>`).join('');
      const empty=trees.length===0?`<span class="og-empty-message">从这里开始，第一笔消费会种下一颗种子</span>`:'';
      const bubble='';
      const flow=region.water?`<svg class="og-flow" viewBox="0 0 100 100" aria-hidden="true"><path d="M74 29 Q63 31 58 37 Q43 41 46 47 Q49 51 59 55 L69 61"/><ellipse cx="78" cy="29" rx="6" ry="1.5"/></svg>`:'';
      const visitors=region.birds?`<button type="button" class="og-bird" data-og="bird" aria-label="看看来访的溪畔小鸟"><img loading="lazy" decoding="async" src="${BIRD}" alt="溪畔小鸟停在溪边"><span>新朋友 · 溪畔小鸟</span></button>`:'';
      return `<section class="og-map"><div class="og-region-tabs" aria-label="绿洲区域">${tabs}<button type="button" data-og="next" class="og-next">下一片的条件 ↗</button></div><div class="og-world ${previewBefore?'og-before':''} ${region.water?'has-water':''}" aria-label="${E(region.name)}，${phase}"><img loading="lazy" decoding="async" class="og-bg" src="${START}" alt="泉边营地的蚀刻近景"><img loading="lazy" decoding="async" class="og-bg og-green ${region.water?'':'og-local-green'}" src="${GREEN}" style="opacity:${region.water?1:p}" alt="" aria-hidden="true">${region.camp?`<img loading="lazy" decoding="async" class="og-bg og-camp" src="${CAMP}" alt="修整后的木屋、桥梁与鸟屋">`:''}<span class="og-world-caption">${E(region.name)}<small>${previewBefore?'最初的样子':phase}</small></span><div class="og-evolution">${flow}${planted}${empty}${bubble}${visitors}</div></div><div class="og-map-footer"><div><b>${environment(s,region.id)}%</b><span>区域复苏 · 虚拟景观</span></div><button type="button" class="og-text-button" data-og="before" aria-pressed="${previewBefore}">${previewBefore?'回到现在':'看看最初'}</button></div><div class="og-scene-note" aria-live="polite">${region.birds?'溪水、营地和小鸟都已到来。后续消费自动开启下一片，这里永久保留。':region.camp?'木屋与桥梁已经修好。达到本区 ¥'+yuan(CONFIG.birds)+' 的成长门槛，小鸟就会安家。':region.water?'溪流已经接通。达到本区 ¥'+yuan(CONFIG.camp)+' 的成长门槛，木屋与桥梁将焕新。':p?'树正在生根。达到本区 ¥'+yuan(CONFIG.water)+' 的成长门槛，溪水将自动接通。':'这里还在枯萎中。消费会自动养树、接通水流、修复营地，迎来新的生命。'}</div></section>`;
    }
    function projects(){
      const r=s.regions[view],steps=[['water','溪流接通',100],['camp','木桥与营地焕新',150],['birds','小鸟安家',200]];
      return `<section class="og-panel og-projects"><span class="og-kicker">环境自动复苏 / RESTORE</span><ol>${steps.map(([id,name,amount],i)=>`<li class="${r[id]?'done':''}"><span class="og-step-dot">${r[id]?'✓':i+1}</span><div><b>${name}</b><small>${r[id]?'已达成 · 景观保留':'本区累计 ¥'+yuan(amount)+' 自动出现'}</small></div></li>`).join('')}</ol><small class="og-fine">两棵树成熟后，下一份成长会自动开启新的区域。</small></section>`;
    }
    function growing(){
      const c=current(s),n=mature(s),nextTree=(n+1)*NEED*CONFIG.centsPerGrowth;
      return `<section class="og-panel og-grow-panel"><span class="og-kicker">计算带来成长 / GROW</span><h3>${s.netCents?'让这片绿意，继续生长':'从一颗种子开始'}</h3><p>${c?SPECIES[c.type].name+' · '+STAGES[stage(c)]+' · '+c.energy+'/100 成长值':'每一份计算积累，都能成为新的绿意。'}<br>距下一棵成熟还差 ${Math.max(0,nextTree-s.netCents)/CONFIG.centsPerGrowth} 成长值。</p>${c?`<progress max="100" value="${c.energy}" aria-label="当前树的成长进度"></progress>`:''}${B('看看如何成长','rules','',true)}<div class="og-pending"><span>成熟树</span><b>${n}</b><span>已开放区域</span><b>${s.regions.length}</b></div>${s.netCents<s.highWaterCents?'<p class="og-refund-note">成长进度已调整，原有景观仍为你保留。</p>':''}</section>`;
    }
    const rewardLabel=detail=>detail.replace(/算力试玩券/g,'计算额度券').replace(/试玩券/g,'计算额度券');
    function rewardPanel(){
      const count=mature(s),ready=s.rewards.filter(r=>r.status==='ready'&&!r.suspended),next=s.rewards.find(r=>r.suspended&&r.status!=='used')||POLICY.find(m=>s.netCents<m.n*REWARD_CENTS&&!s.rewards.some(r=>r.n===m.n&&r.status==='used'))||perTree(Math.floor(s.netCents/REWARD_CENTS)+1);
      return `<section class="og-panel og-reward-panel"><span class="og-kicker">成长的回馈 / REWARD</span><h3>${ready.length?'已解锁 '+ready.length+' 份回馈':'下一份奖励，正在生长'}</h3><p>${rewardLabel(ready.length?ready[0].detail:next.detail)}</p><ol class="og-milestones">${POLICY.map(m=>`<li class="${eligible(s,m)?'done':''}"><span>${eligible(s,m)?'✓':m.n}</span><div><b>累计消费 ¥${m.n*100}</b><small>${rewardLabel(m.detail)}</small></div></li>`).join('')}</ol><button type="button" class="og-text-button" data-og="rewards">查看成长奖励 →</button></section>`;
    }
    function activity(){
      return `<div class="og-bottom-links">${B('我的森林 · '+mature(s)+' 棵','forest')}${B('成长记录 · '+s.log.length,'history')}${B('成长指南','rules')}${B('动效设置','settings')}</div>`;
    }
    function outside(){
      const r=document.getElementById('oaRailT');if(r)r.textContent='绿洲 · '+mature(s)+' 棵成熟';
      const nav=document.querySelector('.cs-nav [data-p="oasis"]');if(nav){let badge=nav.querySelector('.oa-n');const pending=s.rewards.filter(r=>r.status==='ready'&&!r.suspended).length;if(pending){if(!badge){badge=document.createElement('span');badge.className='bt-n mono oa-n';nav.append(badge);}badge.textContent=pending;badge.setAttribute('aria-label',pending+'份试玩奖励待领取');}else badge?.remove();}
      const w=document.getElementById('oaWallet'),empty=document.getElementById('oaWalletEmpty');if(w){w.hidden=false;if(empty)empty.hidden=true;w.innerHTML=`<div class="og-wallet"><b>绿洲奖励 · 买 100 送 100</b><p>每消费 ¥100 送 100 万词元，调用时优先于余额抵扣。</p>${couponList()}${s.receipts.length?'<p>已保存 '+s.receipts.length+' 笔试玩核销回执。</p>':''}</div>`;}
    }
    function render(){root.className='oa og '+(reduced()?'og-reduced':'');root.innerHTML=`${storageError?'<p role="alert">'+E(storageError)+'</p>':''}<div class="og-intro"><span>每消费 100 元，送 100 万词元；每消费 1,000 元，绿洲里长出一棵树。</span></div><div class="og-layout">${scene()}<aside class="og-side">${growing()}${projects()}${rewardPanel()}</aside></div>${activity()}<div class="og-sr" id="ogLive" aria-live="polite"></div>`;outside();}
    function couponList(){
      if(!s.rewards.length)return '<p>还没有可领取的词元。</p>';
      return s.rewards.map(r=>{const expired=r.status==='available'&&r.expiresAt<=Date.now(),status=expired?'已过期':r.suspended?'退款后暂不可用':({ready:'待领取',available:'可用',used:'已使用'})[r.status];return `<article class="og-coupon"><div class="og-coupon-value">100万<small>词元</small></div><div><b>${E(r.title)} · ${status}</b><p>${r.rare?'含月辉种子 · ':r.badge?'含绿洲纪念章 · ':''}累计消费 ¥${r.n*100} · 调用时优先于余额抵扣，不可提现。</p><small>${r.claimedAt?'已领取 · '+date(r.claimedAt):'可以领取'}</small></div>${r.status==='ready'&&!r.suspended?B('领取','claim',r.id,true,role()==='member'):''}</article>`;}).join('');
    }
    function rewards(){modal('买 100 送 100',`<p>每消费 100 元，送 100 万词元，调用时优先于余额抵扣。每消费 1,000 元，绿洲里长出一棵树。</p>${role()==='member'?'<p>你正在查看组织试玩空间，奖励由管理员领取和使用。</p>':''}${couponList()}${(s.badges||[]).length?`<div class="og-badges">${s.badges.map(n=>`<span>✧ 绿洲纪念章 · ${n}棵成熟</span>`).join('')}</div>`:''}${s.receipts.map(r=>`<div class="og-receipt"><b>试玩核销回执 · ${E(r.id)}</b><p>演示订单 ¥${(r.total/100).toFixed(2)} − 抵扣 ¥${(r.discount/100).toFixed(2)} = 演示应付 ¥${(r.due/100).toFixed(2)}</p><small>没有真实调用或扣款 · ${date(r.at)}</small></div>`).join('')}`);}
    function rules(){modal('成长指南',`<div class="og-guide"><p class="og-guide-note"><b>先在教程里，看看一片绿洲如何长大。</b><br>下方操作模拟成长进程，不发起模型调用或扣费。当前网站尚未连接真实结算，教程奖励不计入真实钱包。</p><ol class="og-guide-steps"><li><b>计算积累，种子生根</b><p>接入真实结算后，符合规则的实付消费会自动积累成长。离开页面也能继续养树。</p></li><li><b>树木成熟，环境复苏</b><p>溪流接通、木桥与营地焕新，小鸟随之到来。种满后自动开启下一片区域，老树和风景会留下。</p></li><li><b>买 100 送 100</b><p>每实付消费 ¥100 送 100 万词元。每 ¥1,000 长成一棵树，同时颁发一枚绿洲纪念章；第 3 棵树另得月辉种子。</p></li></ol><section class="og-guide-play"><b>亲手推进一次成长</b><p>每 ¥10 消费 = 1 成长值，100 成长值长成一棵树。当前累计 ${s.netCents/CONFIG.centsPerGrowth} 成长值；点击后回到场景看变化。</p><div class="og-actions">${B('积累 25 成长值','consume','25000',true)}${B('积累 75 成长值','consume','75000')}${B('积累 50 成长值','consume','50000')}</div><div class="og-actions">${B('自定义演示消费','spend-dialog')}${B('体验奖励流程','rewards')}</div></section><details class="og-guide-details"><summary>查看教程规则</summary><p>每 ¥10 消费 = 1 成长值，100 成长值（¥1,000）长成一棵树；本区累计 100 接通溪流、150 修复营地、200 迎来小鸟。再积累成长时自动扩区。</p><p>每累计消费 ¥100 送 100 万词元；每长成一棵树颁发一枚纪念章，第 3 棵树另得月辉种子，用于下一棵自动播种的树。</p><p>充值、赠送额度和券抵扣不计实付成长。退款降低净进度，历史景观保留；未用奖励暂停，补回后恢复同一份奖励。</p><p>当前用券只演示抵扣回执，不提交支付。绿洲是虚拟景观，不代表实际植树或核验减排。</p></details><details class="og-guide-details"><summary>更多教程操作</summary><div class="og-actions">${B('演示流水与退款','ledger')}${B('重新开始教程','reset')}</div></details></div>`);}
    function spendDialog(){modal('模拟已结算消费',`<p>输入一笔最终净实付金额，观察树、水流、营地和动物自动变化。不会真实扣费。</p><label class="og-field">模拟净实付金额（元）<input class="in" id="ogSpendAmount" inputmode="decimal" value="250" autocomplete="off"></label><small>每 ¥10 = 1 成长值；单笔及累计净消费最高 ¥10,000，均为试玩配置。</small><div class="og-actions">${B('确认模拟消费','spend-confirm','',true)}${B('取消','close')}</div>`);}
    function ledger(){modal('模拟消费流水与退款',`<p>净消费 ¥${money(s.netCents)} · 景观历史最高 ¥${money(s.highWaterCents)}。退款只冲正所选原消费，不会让已成形的景观枯萎。</p>${s.events.length?s.events.map(e=>{const refunded=s.events.filter(x=>x.kind==='refund'&&x.original===e.id).reduce((n,x)=>n+x.cents,0);return `<article class="og-receipt"><b>${e.kind==='consume'?'模拟消费':'退款冲正'} ¥${money(e.cents)}</b><small> · ${date(e.at)}</small><p>${E(e.id)}</p>${e.kind==='consume'?`<small>可退 ¥${money(e.cents-refunded)}</small>${e.cents>refunded?B('模拟退款','refund-dialog',e.id):''}`:'<small>关联 '+E(e.original)+'</small>'}</article>`;}).reverse().join(''):'<p>尚无模拟消费。</p>'}`);}

    function settings(){modal('动效设置',`<p>默认尊重系统的“减少动态”设置。减少动态后，成长、奖励和环境状态仍然完整显示。</p><div class="og-actions">${B(s.motion==='system'?'✓ 跟随系统':'跟随系统','motion','system')}${B(s.motion==='reduce'?'✓ 减少动态':'减少动态','motion','reduce')}</div>`);}
    async function click(e){
      const b=e.target.closest('[data-og]');if(!b)return;sync();const a=b.dataset.og,v=b.dataset.value;
      if(a==='region'){view=+v;previewBefore=false;render();root.querySelector(`[data-og="region"][data-value="${v}"]`)?.focus({preventScroll:true});return;}
      if(a==='before'){previewBefore=!previewBefore;render();root.querySelector('[data-og=before]')?.focus({preventScroll:true});return;}
      if(a==='spend-dialog'){spendDialog();return;}
      if(a==='consume'||a==='spend-confirm'){let cents;try{cents=a==='consume'?Number(v):parseMoney(document.getElementById('ogSpendAmount').value);}catch(err){toast(err.message);return;}if(await act({type:'consume',id:uid(),status:'settled',cents})){close();toast('教程进度已更新，看看绿洲的新变化。');root.querySelector('[data-og="rules"]')?.focus({preventScroll:true});}return;}
      if(a==='ledger'){ledger();return;}
      if(a==='refund-dialog'){const event=s.events.find(x=>x.id===v);if(!event)return;const left=event.cents-s.events.filter(x=>x.original===v).reduce((n,x)=>n+x.cents,0);modal('模拟退款冲正',`<p>最多可退 ¥${money(left)}。景观保留，未使用奖励按净消费重新校验。</p><label class="og-field">退款金额（元）<input class="in" id="ogRefundAmount" inputmode="decimal" value="${money(left)}"></label><div class="og-actions">${B('确认模拟退款','refund-confirm',v,true)}${B('取消','ledger')}</div>`);return;}
      if(a==='refund-confirm'){let cents;try{cents=parseMoney(document.getElementById('ogRefundAmount').value);}catch(err){toast(err.message);return;}if(await act({type:'refund',id:uid(),status:'settled',original:v,cents})){ledger();toast('退款冲正已保存，奖励资格已重新检查。');}return;}
      if(a==='bird'){root.querySelector('.og-bird img')?.animate(reduced()?[]:[{transform:'translateY(0)'},{transform:'translateY(-16px) rotate(-5deg)'},{transform:'translateY(0)'}],{duration:650});modal('溪畔来客 · 溪畔小鸟',`<div class="og-visitor"><img loading="lazy" decoding="async" src="${BIRD}" alt="蚀刻淡彩溪畔小鸟"><div><span class="og-kicker">访客图鉴 / 01</span><h3>在这里，安个家。</h3><p>溪流、树荫和鸟屋都准备好了，它成为了这片绿洲的第一位住客。</p><small>虚拟收藏 · 已记录在成长手记中</small></div></div><div class="og-actions">${B('回到绿洲','close','',true)}${B('看看成长记录','history')}</div>`);return;}
      if(a==='next'){modal('下一片：'+regionName(s.regions.length),`<p>每个区域容纳两棵树。完成本区 ¥${yuan(200)} 的成长后，下一笔超过历史最高净消费的部分，会自动开启新区域。无需额外支付扩建费用。</p><p>距开始下一片还有 ¥${money(Math.max(1,s.regions.length*200*CONFIG.centsPerGrowth-s.netCents+1))} 演示净消费。所有旧区域均保留。</p>${B('回到最新区域','active','',true)}`);return;}
      if(a==='active'){close();view=current(s)?.region??s.regions.length-1;render();return;}
      if(a==='rewards'){rewards();return;}
      if(a==='claim'){if(await act({type:'claim',id:v})){const r=s.rewards.find(r=>r.id===v);if(r.rare)modal('月辉来信 · 珍藏种子已入藏',`<div class="og-celebrate">${art({type:'moon',energy:100})}<p>这是月辉树长成后的样子。种子已经放进背包，下一棵自动播种时会使用它。</p><p>这棵树的 100 万词元也已到账，调用时优先抵扣。</p></div><div class="og-actions">${B('回到绿洲继续成长','active','',true)}${B('查看奖励','rewards')}</div>`);else{rewards();toast(r.badge?'纪念章已入藏，100 万词元已到账。':'已领取 100 万词元，调用时优先抵扣。');}}return;}
      if(a==='use'){const r=s.rewards.find(r=>r.id===v);if(!r||r.status!=='available')return;modal('演示一次代金券抵扣',`<p>仅演示结算过程，不调用模型，也不扣真实余额。</p><label class="og-field">演示订单类型<select id="ogOrderModel" class="in"><option value="chat">模型推理 · 演示</option><option value="batch">批量推理 · 演示</option></select></label><label class="og-field">演示订单金额<select id="ogOrderTotal" class="in"><option value="500">¥5.00</option><option value="200">¥2.00</option><option value="1200">¥12.00</option></select></label><p>将使用 ¥${r.cents/100} 试玩券，最多抵至订单金额；一次用完，不找零。</p><div id="ogQuote" class="og-receipt" data-cents="${r.cents}" aria-live="polite">订单 ¥5.00 − 试玩券 ¥${(Math.min(500,r.cents)/100).toFixed(2)} = 演示应付 ¥${(Math.max(0,500-r.cents)/100).toFixed(2)}</div><div class="og-actions">${B('确认演示抵扣','redeem',r.id,true)}${B('取消','rewards')}</div>`);return;}
      if(a==='redeem'){const total=Number(document.getElementById('ogOrderTotal').value),model=document.getElementById('ogOrderModel').value;if(await act({type:'redeem',id:v,total,model})){rewards();toast('演示抵扣完成，回执已保存；没有真实扣款。');}return;}
      if(a==='forest'){modal('我的森林 · 每棵都留下',s.trees.length?`<div class="og-forest">${s.trees.map(t=>`<button type="button" data-og="tree" data-value="${E(t.id)}">${art(t)}<b>${E(t.name||SPECIES[t.type].name)}</b><small>${E(regionName(t.region))} · ${STAGES[stage(t)]}</small></button>`).join('')}</div>`:'<p>从第一颗种子开始。扩建后，旧区域和树木会一直保留。</p>');return;}
      if(a==='tree'){const t=s.trees.find(t=>t.id===v);if(!t)return;modal(t.name||SPECIES[t.type].name,`<div class="og-celebrate">${art(t)}<p>${SPECIES[t.type].desc}</p></div><p>${E(regionName(t.region))} · ${STAGES[stage(t)]} · 成长 ${t.energy}/100</p><label class="og-field">给它起名<input id="ogTreeName" class="in" maxlength="20" value="${E(t.name)}" placeholder="${SPECIES[t.type].name}"></label>${B('保存名字','rename',t.id,true)}`);return;}
      if(a==='rename'){const name=document.getElementById('ogTreeName').value;if(await act({type:'rename',id:v,name}))close();return;}
      if(a==='history'){modal('成长记录',s.log.length?`<ol class="og-history">${s.log.map(l=>`<li><b>${E(l.title)}</b><p>${E(l.detail)}</p><small>${date(l.at)}</small></li>`).join('')}</ol>`:'<p>种子生根、环境变化和每份回馈，都会留在这里。</p>');return;}
      if(a==='rules'){rules();return;}
      if(a==='settings'){settings();return;}
      if(a==='motion'){if(await act({type:'motion',value:v}))settings();return;}
      if(a==='reset'){modal('重新开始本空间试玩？',`<p>仅清空当前个人或组织空间的本地绿洲试玩：树、模拟消费流水和奖励记录。其他空间及真实账户不受影响。</p><div class="og-actions">${B('确认重置试玩','reset-confirm','',true)}${B('取消','close')}</div>`);return;}
      if(a==='reset-confirm'){if(await act({type:'reset'}))close();return;}
      if(a==='go'){close();navigate(v);return;}
      if(a==='close')close();
    }
    root.addEventListener('click',click);dlg.addEventListener('click',e=>{if(e.target===dlg)close();else click(e);});
    dlg.addEventListener('change',e=>{if(e.target.id==='ogOrderTotal'){const q=document.getElementById('ogQuote'),amount=Number(e.target.value),discount=Math.min(amount,Number(q.dataset.cents));q.textContent=`订单 ¥${(amount/100).toFixed(2)} − 试玩券 ¥${(discount/100).toFixed(2)} = 演示应付 ¥${((amount-discount)/100).toFixed(2)}`;}});
    document.getElementById('oaWallet')?.addEventListener('click',click);
    document.querySelectorAll('[data-oa-top]').forEach(b=>b.addEventListener('click',()=>b.dataset.oa==='rules'?rules():settings()));
    window.addEventListener('storage',e=>{if(e.key===key){s=read();view=Math.min(view,s.regions.length-1);render();if(dlg.open)close();}});
    media.addEventListener('change',render);
    global.fpOasis={sync};sync();
    const identity=document.getElementById('btOrgN');if(identity)new MutationObserver(sync).observe(identity,{subtree:true,childList:true,characterData:true});
  };
})(typeof window!=='undefined'?window:globalThis);
