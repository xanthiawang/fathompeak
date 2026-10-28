import {catalog, selectedModel, endpoint, emptyEstimate, estimateNumber, estimateCosts} from './catalog.js?v=d40-20261018';
import {icon,escapeHTML,roles,pageInfo,renderPage,modelRows,estimateResult} from './views.js?v=login2-20261028';
const $=selector=>document.querySelector(selector);
const screen=$('#screen'), sheet=$('#sheet');
const storageKey=role=>`fathompeak-mini-ui-20261018-draft-${role}`;
const state={auth:'in',loginTab:'personal',agree:false,loginScenario:'existing',binds:{phone:'138****8000',wechat:true,email:'',github:''},bindType:'',giftClaimed:false,oasis:{energy:0,pending:3,trees:0,cotree:false,source:['新人','新人','新人']},page:'home',role:'personal',task:'ask',draft:'',amount:'',from:'home',filter:'全部',usageFilter:'全部',paused:false,modelId:'',query:'',vendor:'全部',client:'tool',keyName:'',estimate:emptyEstimate(),estimateFrom:'home'};
let toastTimer,focusBeforeDialog;
function toast(message){const el=$('#toast');el.textContent=message;el.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>{el.hidden=true},3200);}
function readDraft(){try{const value=JSON.parse(localStorage.getItem(storageKey(state.role))||'null');state.draft=typeof value?.text==='string'?value.text:'';state.task=['ask','write','summary','translate'].includes(value?.task)?value.task:'ask';}catch(error){state.draft='';console.warn('Unable to restore local draft',error);toast('无法读取本设备草稿。');}}
function saveDraft(){try{if(state.draft)localStorage.setItem(storageKey(state.role),JSON.stringify({text:state.draft,task:state.task}));else localStorage.removeItem(storageKey(state.role));return true;}catch(error){console.warn('Unable to save local draft',error);toast('本设备存储不可用，请自行保留输入内容。');return false;}}
function openSheet(title,body,actions=''){focusBeforeDialog=document.activeElement;$('#sheet-content').innerHTML=`<div class="sheet-head"><h2 id="sheet-title">${title}</h2><button class="icon-btn" data-action="close" aria-label="关闭弹窗">×</button></div>${body}${actions?`<div class="sheet-actions">${actions}</div>`:''}`;sheet.showModal();}
function closeSheet(){sheet.close();}
sheet.addEventListener('close',()=>{if(focusBeforeDialog?.isConnected)focusBeforeDialog.focus();});
sheet.addEventListener('click',event=>{if(event.target===sheet){const r=sheet.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)closeSheet();}});
function saveIntent(){try{sessionStorage.setItem('fp-mini-intent-'+state.role,JSON.stringify({modelId:state.modelId,amount:state.amount}));}catch(error){console.warn('Unable to retain preview selection',error);}}
function readIntent(){try{const v=JSON.parse(sessionStorage.getItem('fp-mini-intent-'+state.role)||'null');state.modelId=catalog.some(m=>m.id===v?.modelId)?v.modelId:'';state.amount=typeof v?.amount==='string'?v.amount:'';}catch(error){state.modelId='';state.amount='';console.warn('Unable to restore preview selection',error);}}
const reviewPages=[['home','模型市场'],['estimate','算算费用'],['api','API 接入'],['work','体验'],['account','我的'],['invite','邀请好友'],['oasis','我的绿洲'],['login','登录与绑定'],['billing','用量账单'],['purchase','充值购买'],['team','企业管理']];
const navPages=[['home','models','模型市场'],['api','keys','API 接入'],['work','play','体验'],['account','acct','我的']];
function render({focus=true}={}){
 screen.innerHTML=renderPage(state);screen.scrollTop=0;
 const tab=['model','service','estimate'].includes(state.page)?'home':state.page==='connect'?'api':['purchase','confirm','orders','usage','billing','team','invite','oasis','login','login-code','security'].includes(state.page)?'account':state.page;
 $('#tab-bar').innerHTML=navPages.map(([id,ic,label])=>`<button data-nav="${id}" ${id===tab?'aria-current="page"':''}>${icon(ic)}<span>${label}</span></button>`).join('');
 $('#review-pages').innerHTML=reviewPages.map(([id,label],i)=>`<button data-review-page="${id}" ${id===state.page||(id==='purchase'&&state.page==='confirm')?'aria-current="page"':''}><span class="mono">0${i+1}</span>${label}</button>`).join('');
 const info=pageInfo[state.page]||pageInfo.home;$('#page-number').textContent=info[0];$('#context-title').textContent=info[1];$('#context-copy').textContent=info[2];$('#context-flow').innerHTML=info[3].map((step,i)=>`<div><span>0${i+1}</span>${step}</div>`).join('');
 if(focus)screen.focus({preventScroll:true});
}
function navigate(page){if(!(page in pageInfo))return;if(state.auth==='out'&&['account','billing','api','connect','orders','usage','team','invite','oasis','security','purchase'].includes(page))page='login';if(page==='purchase'&&state.page!=='confirm')state.from=state.page;state.page=page;render();}
function setRole(role){if(!(role in roles))return;saveDraft();state.role=role;state.amount='';state.modelId='';state.keyName='';state.estimate=emptyEstimate();state.estimateFrom='home';readIntent();state.filter='全部';state.usageFilter='全部';state.query='';state.vendor='全部';readDraft();$('#review-role').value=role;state.page='home';render();}
$('#review-role').addEventListener('change',event=>setRole(event.target.value));
$('#review-login')?.addEventListener('change',event=>{state.loginScenario=event.target.value;state.auth='out';state.agree=false;state.loginTab='personal';navigate('login');});
document.addEventListener('visibilitychange',()=>document.body.classList.toggle('page-hidden',document.hidden));
const toHalfWidth=v=>v.replace(/[\uFF10-\uFF19]/g,c=>String.fromCharCode(c.charCodeAt(0)-0xFEE0)).replace(/[\uFF0E\u3002]/g,'.');
const normalizeNumberInput=el=>{const v=toHalfWidth(el.value);if(v!==el.value){const pos=el.selectionStart;el.value=v;try{el.setSelectionRange(pos,pos);}catch(e){}}return v;};
document.addEventListener('input',event=>{
 if(event.target.dataset.estimate||event.target.id==='amount')normalizeNumberInput(event.target);
 if(event.target.dataset.estimate){state.estimate[event.target.dataset.estimate]=event.target.value;event.target.removeAttribute('aria-invalid');$('#estimate-error').textContent='';$('#estimate-result').innerHTML=estimateResult(state);}
 if(event.target.id==='task-input'){state.draft=event.target.value;$('#input-count').textContent=Array.from(state.draft).length;$('#draft-status').textContent=saveDraft()?(state.draft?'草稿已自动保存':'草稿会自动保存'):'未能保存，请保留输入';}
 if(event.target.id==='model-search'){state.query=event.target.value;$('#model-list').innerHTML=modelRows(state);}
 if(event.target.id==='key-name')state.keyName=event.target.value;
 if(event.target.id==='amount'){state.amount=event.target.value;saveIntent();event.target.removeAttribute('aria-invalid');$('#amount-error').textContent='';}
 if(event.target.id==='member-search'){const q=event.target.value.trim();$('#member-empty').innerHTML=q?`<div class="empty subtle"><h2>暂无匹配的成员记录</h2><p>换个姓名或工作邮箱试试。</p></div>`:renderPage({...state,page:'team'}).match(/<div id="member-empty">([\s\S]*?)<\/div><div class="notice">/)[1];}
});
document.addEventListener('change',event=>{
 if(event.target.id==='login-agree'){state.agree=event.target.checked;return;}
 if(event.target.id==='estimate-model'){
  state.estimate={...state.estimate,modelId:event.target.value,inputRate:'',outputRate:''};
  state.modelId=event.target.value;saveIntent();
  const top=screen.scrollTop;render({focus:false});screen.scrollTop=top;$('#estimate-model').focus({preventScroll:true});
  toast('已切换模型，单价已清空；预计用量已保留。');
 }
});
document.addEventListener('submit',event=>{
 if(event.target.id==='estimate-form'){
  event.preventDefault();const e=state.estimate;
  const missing=['input','output','inputRate','outputRate'].find(k=>{
   if(k.endsWith('Rate')&&estimateNumber(e[k.replace('Rate','')])===0&&e[k].trim()==='')return false;
   return estimateNumber(e[k])===null;
  });
  if(!e.modelId||missing){
   const target=!e.modelId?$('#estimate-model'):$('#estimate-'+missing);
   if(missing?.endsWith('Rate'))$('.estimate-rates').open=true;
   const labels={input:'输入用量',output:'输出用量',inputRate:'输入单价',outputRate:'输出单价'};
   $('#estimate-error').textContent=!e.modelId?'请先选择模型。':(String(e[missing]).trim()===''?`请填写${labels[missing]}。`:`${labels[missing]}需要是非负数字，最多 6 位整数和 6 位小数。`);
   target.setAttribute('aria-invalid','true');target.focus({preventScroll:true});$('#estimate-error').scrollIntoView({block:'center'});return;
  }
  $('#estimate-error').textContent='';$('#estimate-result').innerHTML=estimateResult(state);$('#estimate-result').scrollIntoView({behavior:'smooth',block:'start'});return;
 }

 if(event.target.id==='amount-form'){
  event.preventDefault();const value=$('#amount').value.trim();
  if(!/^(?:0|[1-9]\d{0,8})(?:\.\d{1,2})?$/.test(value)||Number(value)<=0){$('#amount-error').textContent=value===''?'请填写充值金额。':(Number(value)>999999999?'金额过大，请填写 9 位以内的整数部分。':'请填写大于 0 的金额，最多两位小数。');$('#amount').setAttribute('aria-invalid','true');$('#amount').focus();return;}
  state.amount=Number(value).toFixed(2);saveIntent();navigate('confirm');
 }
});
const actions={
 estimate(){
  state.estimateFrom=['model','account'].includes(state.page)?state.page:'home';
  if(state.modelId&&state.estimate.modelId!==state.modelId)state.estimate={...state.estimate,modelId:state.modelId,inputRate:'',outputRate:''};
  navigate('estimate');
 },
 'estimate-recharge'(){const r=estimateCosts(state.estimate);if(!r||!(r.discountCost>0))return;state.amount=Math.max(.01,Math.ceil(r.discountCost*100)/100).toFixed(2);saveIntent();state.from='estimate';navigate('purchase');toast('已按折后预算填入充值金额，可再修改。');},
 'show-models'(){const target=$('#market-heading');target?.scrollIntoView({behavior:'smooth',block:'start'});$('#model-search')?.focus({preventScroll:true});},
 'reset-models'(){state.query='';state.vendor='全部';render();actions['show-models']();},
 'pick-model'(){openSheet('选择接入模型',`<div class="picker-models">${catalog.map(m=>`<button class="menu-row" data-pick-model="${m.id}">${escapeHTML(m.name)}<span class="arrow">${m.id===state.modelId?'✓':'›'}</span></button>`).join('')}</div>`);},
 'create-key'(){openSheet('创建 API Key',`<p>密钥用于模型调用鉴权，按所属账户额度计费。</p><label class="form-field">Key 名称<input id="key-name" maxlength="60" placeholder="填写应用或项目名称" value="${escapeHTML(state.keyName)}" autocomplete="off"></label><p class="small">完整 Key 只在创建时显示一次，请妥善保存。</p>`, '<button class="primary full" data-action="key-created">创建</button><button class="secondary full" data-copy-link="console">复制网页控制台链接</button>');},
 'pricing-help'(){openSheet('计费说明','<p>个人与企业均享公开价 4 折起，具体折扣按模型与用量确定，通过账户余额按实际 Token 用量计费。</p>','<button class="secondary full" data-action="sales">咨询采购报价 →</button>');},
 'sales'(){openSheet('企业采购与合作','<p>说明所需模型、预计用量及响应要求，核对样例测试与采购报价。算电协同基座、一体机和节点合作通过商务咨询承接。</p>','<button class="primary full" data-copy-link="enterprise">复制企业采购页链接</button><button class="secondary full" data-action="close">继续查看模型</button>');},
 'welcome-gift'(){openSheet('注册礼包','<div class="gift-value">¥68 <span>模型试用券</span></div><p>新注册用户可领取 68 元试用券，用于体验模型。试用券与充值余额分开显示。</p>','<button class="primary full" data-action="gift-claimed">立即领取</button><button class="secondary full" data-nav="work">先看看模型体验 →</button>');},
 'education'(){openSheet('教育优惠','<p>面向学生、教师与实验室。个人和企业公开价 4 折起的优惠保持不变，教育专属权益通过资格认证确认。</p><div class="setup-steps"><div><b>01</b><span>选择身份<small>学生、教师或实验室</small></span></div><div><b>02</b><span>提交认证资料</span></div><div><b>03</b><span>查看专属权益</span></div></div>','<button class="primary full" data-action="close">开始认证</button><button class="secondary full" data-copy-link="edu">复制教育优惠链接</button>');},
 'api-docs'(){openSheet('接入文档','<p>查看鉴权、模型参数和客户端配置。</p>','<button class="primary full" data-copy-link="api">复制 API 文档链接</button>');},
 close:closeSheet,
 'key-created'(){closeSheet();toast('API Key 已创建，请妥善保存。');},
 'gift-claimed'(){state.giftClaimed=true;state.oasis.pending+=1;state.oasis.source.push('礼包');closeSheet();render({focus:false});toast('试用券已放入账户，绿洲多了 1 份能量。');},
 'oasis-share'(){const o=state.oasis,sc=o.trees>=2?'revived':o.trees>=1?'camp':'withered';openSheet('分享我的绿洲',`<div class="poster oasis-share"><div class="poster-scene oasis-${sc}"></div><span class="poster-brand">沐仞 · FathomPeak</span><b>${o.trees?`我在沐仞种下了 ${o.trees} 棵树`:'我在沐仞种下了一颗种子'}</b><p>每一次绿电调用，都让绿洲多一点生机。${state.role==='member'?'':'<br>来和我合种，你我各得 ¥20 代金券。'}</p><div class="poster-foot"><div class="poster-code" aria-label="小程序码"></div><small>微信扫码<br>进入沐仞小程序</small></div></div>`,`<button class="primary full" data-action="poster-saved">保存到相册</button>${state.role==='member'?'':'<button class="secondary full" data-action="invite-share">发给微信好友</button>'}`);},
 'wx-phone'(){if(!state.agree){toast('请先阅读并同意用户服务协议和隐私政策。');return;}openSheet('沐仞 申请','<div class="wx-auth"><p>获取你的手机号，用于登录和账号安全验证</p><div class="wx-phone">138****8000<small>微信绑定号码</small></div><button class="text-button" data-nav="login-code">使用其他手机号</button></div>','<button class="primary full" data-action="wx-allow">允许</button><button class="secondary full" data-action="wx-deny">不允许</button>');},
 'wx-deny'(){closeSheet();navigate('login-code');toast('可使用验证码登录。');},
 'wx-allow'(){const sc=state.loginScenario;if(sc==='conflict'){openSheet('该手机号已绑定其他微信','<p>手机号 138****8000 对应的沐仞账号已绑定另一个微信，暂时无法用当前微信登录。</p><p>可使用短信验证码登录，再在「我的 → 账号与安全」中更换绑定的微信。</p>','<button class="primary full" data-nav="login-code">验证码登录</button><button class="secondary full" data-nav="login-code">换个手机号</button>');return;}state.binds={...state.binds,phone:'138****8000',wechat:true};if(sc==='new'){openSheet('注册成功','<p>已为 138****8000 创建沐仞账号，并绑定当前微信，下次可直接登录。</p><p>新人礼包 ¥68 试用券待领取。</p>','<button class="primary full" data-action="login-done">进入沐仞</button>');return;}openSheet('登录成功','<p>该手机号已注册沐仞，已为你登录原账号，并绑定当前微信，下次可直接登录。</p><dl class="detail-list"><div><dt>账号</dt><dd>138****8000 · 个人账户</dd></div><div><dt>登录方式</dt><dd>手机号、微信</dd></div><div><dt>余额与 API Key</dt><dd>已同步</dd></div></dl>','<button class="primary full" data-action="login-done">进入沐仞</button>');},
 'send-code'(btn){if(btn){btn.disabled=true;let n=60;btn.textContent=n+' 秒后重发';const t=setInterval(()=>{n--;if(n<=0||!btn.isConnected){clearInterval(t);btn.disabled=false;btn.textContent='获取验证码';return;}btn.textContent=n+' 秒后重发';},1000);}toast('验证码已发送');},
 'code-login'(){const id=($('#login-id')?.value||'').trim(),code=($('#login-id-code')?.value||'').trim();if(!/^1\d{10}$/.test(id)&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(id)){toast('请输入正确的手机号或邮箱');$('#login-id')?.focus();return;}if(!/^\d{6}$/.test(code)){toast('请输入 6 位验证码。');$('#login-id-code')?.focus();return;}if(!state.agree){toast('请先阅读并同意用户服务协议和隐私政策。');return;}const isMail=id.includes('@');const shown=isMail?id.replace(/^(.).*(@.*)$/,'$1***$2'):id.replace(/^(\d{3})\d{4}(\d{4})$/,'$1****$2');state.binds={...state.binds,wechat:true,...(isMail?{email:shown}:{phone:shown})};openSheet('登录成功','<p>已登录 '+shown+'，当前微信已自动绑定，下次可直接登录。</p>','<button class="primary full" data-action="login-done">进入沐仞</button>');},
 'org-login'(){const id=($('#org-email')?.value||'').trim(),code=($('#org-email-code')?.value||'').trim();if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(id)){toast('请输入工作邮箱。');$('#org-email')?.focus();return;}if(!/^\d{6}$/.test(code)){toast('请输入 6 位验证码。');$('#org-email-code')?.focus();return;}if(!state.agree){toast('请先阅读并同意用户服务协议和隐私政策。');return;}state.auth='in';setRole('member');toast('登录成功');},
 'login-done'(){closeSheet();state.auth='in';navigate('home');toast('登录成功');},
 logout(){openSheet('确定退出登录？','<p>退出后需要重新登录才能使用账号功能。</p>','<button class="primary full" data-action="close">取消</button><button class="secondary full" data-action="confirm-logout">退出登录</button>');},
 'confirm-logout'(){closeSheet();state.auth='out';state.agree=false;navigate('login');},
 'unbind-wechat'(){if(!state.binds.phone&&!state.binds.email){toast('至少要保留一种登录方式。');return;}openSheet('解除绑定微信？','<p>解除绑定后，将无法使用该微信快捷登录沐仞，需使用手机号或邮箱验证码登录。</p>','<button class="primary full" data-action="close">取消</button><button class="secondary full" data-action="confirm-unbind">确认解除</button>');},
 'confirm-unbind'(){closeSheet();state.binds={...state.binds,wechat:false};render({focus:false});toast('已解除绑定');},
 bind(btn){const t=btn?.dataset?.bind||'phone';state.bindType=t;const label=t==='phone'?'手机号':'邮箱';openSheet((state.binds[t]?'更换':'绑定')+label,`<label class="form-field">${label}<input id="bind-id" placeholder="${t==='phone'?'11 位手机号':'常用邮箱'}"></label><label class="form-field">验证码<span class="code-row"><input id="bind-code" inputmode="numeric" maxlength="6" placeholder="6 位验证码"><button class="text-button" data-action="send-code">获取验证码</button></span></label><p class="small muted">该${label}如已绑定其他沐仞账号，将无法绑定。</p>`,'<button class="primary full" data-action="bind-done">确认</button>');},
 'bind-done'(){const t=state.bindType,id=($('#bind-id')?.value||'').trim(),code=($('#bind-code')?.value||'').trim();const ok=t==='phone'?/^1\d{10}$/.test(id):/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(id);if(!ok){toast(t==='phone'?'请输入正确的手机号。':'请输入正确的邮箱。');return;}if(!/^\d{6}$/.test(code)){toast('请输入 6 位验证码。');return;}const shown=t==='phone'?id.replace(/^(\d{3})\d{4}(\d{4})$/,'$1****$2'):id.replace(/^(.).*(@.*)$/,'$1***$2');state.binds={...state.binds,[t]:shown};closeSheet();render({focus:false});toast('绑定成功');},
 'bind-wechat'(){state.binds={...state.binds,wechat:true};render({focus:false});toast('绑定成功');},
 'collect-energy'(){const o=state.oasis;if(!o.pending)return;o.pending-=1;o.source.shift();o.energy+=1;const top=screen.scrollTop;if(o.energy>=4){o.energy=4;render({focus:false});screen.scrollTop=top;setTimeout(()=>{o.trees+=1;o.energy=0;render({focus:false});screen.scrollTop=top;toast(o.trees===1?'第一棵树长成了，绿洲开始复苏。':'又长成一棵树，绿洲更茂盛了。');},900);return;}render({focus:false});screen.scrollTop=top;toast(['种子发芽了。','长成树苗了。','长成一棵小树了。'][o.energy-1]||'收到 1 份能量。');},
 'invite-share'(){state.oasis.cotree=true;if(sheet.open)closeSheet();if(state.page==='oasis'){const top=screen.scrollTop;render({focus:false});screen.scrollTop=top;}toast('已发给好友。好友首次调用后，合种的树就会发芽。');},
 'invite-poster'(){openSheet('邀请海报','<div class="poster"><div class="poster-scene"></div><span class="poster-brand">沐仞 · FathomPeak</span><b>一起用，一起种一棵树</b><p>主流模型 API，公开价 4 折起。<br>注册实名并首次调用，你我各得 ¥20 代金券。</p><div class="poster-foot"><div class="poster-code" aria-label="小程序码"></div><small>微信扫码<br>进入沐仞小程序</small></div></div>','<button class="primary full" data-action="poster-saved">保存到相册</button><button class="secondary full" data-action="close">返回</button>');},
 'poster-saved'(){closeSheet();toast('海报已保存到相册。');},
 'referrer'(){openSheet('成为推荐官','<p>面向技术博主、AI 社群和合作伙伴。好友每次消费，你持续获得代金券返还，返还比例按合作约定。</p><dl class="detail-list"><div><dt>返还形式</dt><dd>代金券，抵扣模型调用</dd></div><div><dt>返还周期</dt><dd>好友注册后 12 个月</dd></div></dl>','<button class="primary full" data-action="referrer-applied">申请成为推荐官</button>');},
 'referrer-applied'(){closeSheet();toast('申请已提交，我们会尽快联系你。');},
 'invite-rules'(){openSheet('活动规则','<ul class="rule-list"><li>好友完成实名并首次调用后，双方各得 ¥20 代金券。</li><li>代金券只抵扣模型调用，不可提现或转让。</li><li>同一实名、同一设备只计一次。</li><li>邀请人数不限。</li></ul>','<button class="secondary full" data-action="close">知道了</button>');},
 'share-month'(){toast('已生成本月绿电账单卡片。');},
 'invite-sent'(){closeSheet();toast('邀请已发送。');},
 motion(){state.paused=!state.paused;$('.hero')?.classList.toggle('paused',state.paused);if(state.page==='account'){const top=screen.scrollTop;render({focus:false});screen.scrollTop=top;}toast(state.paused?'首页背景动态已暂停。':'首页背景动态已开启。');},
 models(){actions['pick-model']();},
 send(){if(!selectedModel(state)){actions['pick-model']();return;}if(!state.draft.trim()){toast('先写下你的问题或需要处理的文本。');$('#task-input').focus();return;}saveDraft();openSheet('余额不足','<p>充值后即可在线试用这个模型，按实际 Token 用量计费。</p>',`<button class="primary full" data-action="close">回到输入</button>${state.role==='member'?'<button class="secondary full" data-action="admin-help">了解企业额度</button>':'<button class="secondary full" data-nav="purchase">查看购买流程 →</button><button class="secondary full" data-nav="invite">邀请好友，双方各得 ¥20</button>'}`);},
 'clear-draft'(){if(!state.draft){toast('当前没有草稿。');return;}openSheet('清除草稿？','<p>清除后无法恢复。</p>','<button class="primary full" data-action="close">保留草稿</button><button class="secondary full" data-action="confirm-clear">确认清除</button>');},
 'confirm-clear'(){state.draft='';saveDraft();closeSheet();render();toast('草稿已清除。');},
 notifications(){openSheet('通知','<p>暂无新通知。到账、任务进度和额度提醒会显示在这里。</p>','<button class="secondary full" data-action="close">知道了</button>');},
 'admin-help'(){openSheet('由企业管理员分配','<p>企业成员使用管理员分配的额度。额度不足时，请联系本企业管理员；个人余额不会自动补扣企业消费。</p>','<button class="secondary full" data-action="close">返回</button>');},
 'order-help'(){openSheet('订单与售后','<p>每笔订单都会展示支付、到账、退款和开票状态。</p><p>如需咨询服务，可通过官网联系沐仞。</p>','<button class="primary full" data-copy-link="enterprise">复制官网联系页链接</button>');},
 'account-help'(){openSheet('账号与安全','<p>个人与企业使用独立登录入口，企业身份与角色由账户权限决定。</p>','<button class="secondary full" data-action="close">返回</button>');},
 help(){openSheet('我们在这里','<p>了解服务、计费和企业接入，可查看官网文档或联系沐仞团队。</p>','<button class="primary full" data-copy-link="docs">复制接入文档链接</button><button class="secondary full" data-copy-text="fathompeak@163.com" data-copy-label="联系邮箱">复制联系邮箱</button>');},
 api(){openSheet('让 AI 接入你的业务','<p>开发者可以通过网页控制台管理 API Key，并查看接入文档。也可以在小程序里在线试用模型。</p>','<button class="primary full" data-copy-link="docs">复制 API 文档链接</button><button class="secondary full" data-copy-link="console">复制网页控制台链接</button>');},
 invite(){openSheet('邀请团队成员','<p>管理员通过工作邮箱邀请成员，并为其配置角色和消费限额。</p><label class="form-field">工作邮箱<input type="email" placeholder="填写成员的工作邮箱" autocomplete="off"></label><label class="form-field">角色<select><option>企业成员</option></select></label>','<button class="primary full" data-action="invite-sent">发送邀请</button>');},
 about(){openSheet('沐仞 · FathomPeak','<p>栉风沐雨，登高万仞。</p><p>算电协同，词元出海。</p>','<button class="primary full" data-action="close">继续浏览</button>');},
};
document.addEventListener('click',async event=>{
 const button=event.target.closest('button,[data-nav]');if(!button)return;
 if(button.dataset.model){state.modelId=button.dataset.model;saveIntent();navigate('model');return;}
 if(button.dataset.pickModel){state.modelId=button.dataset.pickModel;saveIntent();closeSheet();render();return;}
 if(button.dataset.vendor){const top=screen.scrollTop;state.vendor=button.dataset.vendor;render({focus:false});screen.scrollTop=top;document.querySelector('[data-vendor="'+state.vendor+'"]').focus({preventScroll:true});return;}
 if(button.dataset.client){const top=screen.scrollTop;state.client=button.dataset.client;render({focus:false});screen.scrollTop=top;document.querySelector('[data-client="'+state.client+'"]').focus({preventScroll:true});return;}
 if(button.dataset.copyLink||button.dataset.copyText){const text=button.dataset.copyText||new URL('../#'+button.dataset.copyLink,location.href).href;const label=button.dataset.copyLabel||'链接';try{await navigator.clipboard.writeText(text);toast(`已复制${label}${button.dataset.copyLink?'，请在电脑浏览器中打开':''}。`);}catch(error){toast('未能复制：'+text);}return;}
 if(button.dataset.usagePreset){const v=button.dataset.usagePreset;['input','output'].forEach(k=>{state.estimate[k]=v;const el=$('#estimate-'+k);if(el){el.value=v;el.removeAttribute('aria-invalid');}});$('#estimate-error').textContent='';$('#estimate-result').innerHTML=estimateResult(state);return;}
 if(button.dataset.amountPreset){const el=$('#amount');el.value=button.dataset.amountPreset;state.amount=el.value;saveIntent();el.removeAttribute('aria-invalid');$('#amount-error').textContent='';return;}
 if(button.dataset.copy){const text=button.dataset.copy==='endpoint'?endpoint:selectedModel(state)?.name;if(!text)return;try{await navigator.clipboard.writeText(text);toast('已复制'+(button.dataset.copy==='endpoint'?'接入地址':'模型名称'));}catch(error){toast('未能复制，请手动选择配置文本。');}return;}
 if(button.dataset.nav){if(sheet.open)closeSheet();navigate(button.dataset.nav);return;}
 if(button.dataset.reviewPage){const page=button.dataset.reviewPage;if(page==='team'&&state.role!=='admin')setRole('admin');if(page==='estimate')state.estimateFrom='home';navigate(page);return;}
 if(button.dataset.loginTab){state.loginTab=button.dataset.loginTab;render({focus:false});return;}
 if(button.dataset.task){state.task=button.dataset.task;saveDraft();state.page='work';render();return;}
 if(button.dataset.filter){state.filter=button.dataset.filter;render();return;}
 if(button.dataset.usageFilter){state.usageFilter=button.dataset.usageFilter;render();return;}
 if(button.dataset.action){const action=button.dataset.action;if(sheet.open&&!['close','confirm-clear','send-code'].includes(action))closeSheet();actions[action]?.(button);}
});
readIntent();readDraft();render({focus:false});
