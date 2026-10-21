import {catalog, selectedModel, endpoint, emptyEstimate, estimateNumber} from './catalog.js?v=d40-20261018';
import {icon,escapeHTML,roles,pageInfo,renderPage,modelRows,estimateResult} from './views.js?v=acct-20261018';
const $=selector=>document.querySelector(selector);
const screen=$('#screen'), sheet=$('#sheet');
const storageKey=role=>`fathompeak-mini-ui-20261018-draft-${role}`;
const state={page:'home',role:'personal',task:'ask',draft:'',amount:'',from:'home',filter:'全部',usageFilter:'全部',paused:false,modelId:'',query:'',vendor:'全部',client:'tool',keyName:'',estimate:emptyEstimate(),estimateFrom:'home'};
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
const reviewPages=[['home','模型市场'],['estimate','算算费用'],['api','API 接入'],['work','体验'],['account','我的'],['billing','用量账单'],['purchase','充值购买'],['team','企业管理']];
const navPages=[['home','models','模型市场'],['api','keys','API 接入'],['work','play','体验'],['account','acct','我的']];
function render({focus=true}={}){
 screen.innerHTML=renderPage(state);screen.scrollTop=0;
 const tab=['model','service','estimate'].includes(state.page)?'home':state.page==='connect'?'api':['purchase','confirm','orders','usage','billing','team'].includes(state.page)?'account':state.page;
 $('#tab-bar').innerHTML=navPages.map(([id,ic,label])=>`<button data-nav="${id}" ${id===tab?'aria-current="page"':''}>${icon(ic)}<span>${label}</span></button>`).join('');
 $('#review-pages').innerHTML=reviewPages.map(([id,label],i)=>`<button data-review-page="${id}" ${id===state.page||(id==='purchase'&&state.page==='confirm')?'aria-current="page"':''}><span class="mono">0${i+1}</span>${label}</button>`).join('');
 const info=pageInfo[state.page]||pageInfo.home;$('#page-number').textContent=info[0];$('#context-title').textContent=info[1];$('#context-copy').textContent=info[2];$('#context-flow').innerHTML=info[3].map((step,i)=>`<div><span>0${i+1}</span>${step}</div>`).join('');
 if(focus)screen.focus({preventScroll:true});
}
function navigate(page){if(!(page in pageInfo))return;if(page==='purchase'&&state.page!=='confirm')state.from=state.page;state.page=page;render();}
function setRole(role){if(!(role in roles))return;saveDraft();state.role=role;state.amount='';state.modelId='';state.keyName='';state.estimate=emptyEstimate();state.estimateFrom='home';readIntent();state.filter='全部';state.usageFilter='全部';state.query='';state.vendor='全部';readDraft();$('#review-role').value=role;state.page='home';render();}
$('#review-role').addEventListener('change',event=>setRole(event.target.value));
document.addEventListener('visibilitychange',()=>document.body.classList.toggle('page-hidden',document.hidden));
document.addEventListener('input',event=>{
 if(event.target.dataset.estimate){state.estimate[event.target.dataset.estimate]=event.target.value;event.target.removeAttribute('aria-invalid');$('#estimate-error').textContent='';$('#estimate-result').innerHTML=estimateResult(state);}
 if(event.target.id==='task-input'){state.draft=event.target.value;$('#input-count').textContent=Array.from(state.draft).length;$('#draft-status').textContent=saveDraft()?(state.draft?'草稿已保存 · 仅本设备':'草稿仅保存在本设备'):'未能保存，请保留输入';}
 if(event.target.id==='model-search'){state.query=event.target.value;$('#model-list').innerHTML=modelRows(state);}
 if(event.target.id==='key-name')state.keyName=event.target.value;
 if(event.target.id==='amount'){state.amount=event.target.value;saveIntent();event.target.removeAttribute('aria-invalid');$('#amount-error').textContent='';}
 if(event.target.id==='member-search'){const q=event.target.value.trim();$('#member-empty').innerHTML=q?`<div class="empty subtle"><h2>暂无匹配的成员记录</h2><p>企业成员数据尚未接入。<br>搜索内容仅用于当前界面筛选。</p></div>`:renderPage({...state,page:'team'}).match(/<div id="member-empty">([\s\S]*?)<\/div><div class="notice">/)[1];}
});
document.addEventListener('change',event=>{
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
   $('#estimate-error').textContent=!e.modelId?'请先选择模型。':'请补齐有效用量与单价：非负数字，最多 6 位整数与 6 位小数。';
   target.setAttribute('aria-invalid','true');target.focus();return;
  }
  $('#estimate-error').textContent='';$('#estimate-result').innerHTML=estimateResult(state);$('#estimate-result').scrollIntoView({behavior:'smooth',block:'start'});return;
 }

 if(event.target.id==='amount-form'){
  event.preventDefault();const value=$('#amount').value.trim();
  if(!/^(?:0|[1-9]\d{0,8})(?:\.\d{1,2})?$/.test(value)||Number(value)<=0){$('#amount-error').textContent='请填写大于 0 的金额，最多两位小数。';$('#amount').setAttribute('aria-invalid','true');$('#amount').focus();return;}
  state.amount=Number(value).toFixed(2);saveIntent();navigate('confirm');
 }
});
const actions={
 estimate(){
  state.estimateFrom=['model','account'].includes(state.page)?state.page:'home';
  if(state.modelId&&state.estimate.modelId!==state.modelId)state.estimate={...state.estimate,modelId:state.modelId,inputRate:'',outputRate:''};
  navigate('estimate');
 },
 'show-models'(){const target=$('#market-heading');target?.scrollIntoView({behavior:'smooth',block:'start'});$('#model-search')?.focus({preventScroll:true});},
 'reset-models'(){state.query='';state.vendor='全部';render();actions['show-models']();},
 'pick-model'(){openSheet('选择接入模型',`<p>官网目录快照 · 2026-10-13。可调用范围以账户开通为准。</p><div class="picker-models">${catalog.map(m=>`<button class="menu-row" data-pick-model="${m.id}">${escapeHTML(m.name)}<span class="arrow">${m.id===state.modelId?'✓':'›'}</span></button>`).join('')}</div>`);},
 'create-key'(){openSheet('创建 API Key',`<p>密钥用于模型调用鉴权，按所属账户额度计费。</p><label class="form-field">Key 名称<input id="key-name" maxlength="60" placeholder="填写应用或项目名称" value="${escapeHTML(state.keyName)}" autocomplete="off"></label><div class="notice">当前未连接真实账户，无法创建或读取密钥。</div>`, '<button class="primary full" disabled>连接账户后创建</button><a class="secondary full" href="../#console" target="_blank" rel="noopener">打开网页控制台 ↗</a>');},
 'pricing-help'(){openSheet('折扣与计费','<p>个人与企业均享公开价 4 折起，具体折扣按模型与用量确定，通过账户余额按实际 Token 用量计费。</p><p>当前目录展示的是 2026-10-13 的历史输出参考价，尚未同步完整的折扣价格表。输入、输出及缓存单价以正式计费表为准；历史参考价不再额外叠加折扣。</p>','<button class="secondary full" data-action="sales">咨询采购报价 →</button>');},
 'sales'(){openSheet('企业采购与合作','<p>说明所需模型、预计用量及响应要求，核对样例测试与采购报价。算电协同基座、一体机和节点合作通过商务咨询承接。</p>','<a class="primary full" href="../#enterprise" target="_blank" rel="noopener">前往企业采购 ↗</a><button class="secondary full" data-action="close">继续查看模型</button>');},
 'welcome-gift'(){openSheet('注册礼包 · 方案预览','<div class="gift-value">¥68 <span>模型试用券</span></div><p>拟为新注册用户提供 68 元试用券，用于体验模型。试用券与充值现金余额分开显示，不计入现金余额。</p><dl class="detail-list"><div><dt>发放条件</dt><dd>拟注册后领取，条件待确认</dd></div><div><dt>有效期 / 适用模型</dt><dd>待活动规则确认</dd></div><div><dt>与折扣优惠的关系</dt><dd>抵扣顺序与范围待确认</dd></div></dl><div class="notice">当前仅展示礼包方案，未发券、未到账。</div>','<button class="primary full" disabled>礼包待开放</button><button class="secondary full" data-nav="work">先看看模型体验 →</button>');},
 'education'(){openSheet('教育优惠','<p>面向学生、教师与实验室。个人和企业公开价 4 折起的优惠保持不变，教育专属权益通过资格认证确认。</p><div class="setup-steps"><div><b>01</b><span>选择身份<small>学生、教师或实验室</small></span></div><div><b>02</b><span>提交认证资料<small>所需材料和审核标准待确认</small></span></div><div><b>03</b><span>查看专属权益<small>优惠内容、叠加规则和有效期待配置</small></span></div></div>','<button class="primary full" disabled>认证服务待接入</button><a class="secondary full" href="../#edu" target="_blank" rel="noopener">查看官网教育方案 ↗</a>');},
 'api-docs'(){openSheet('接入文档','<p>查看鉴权、模型参数和客户端配置。当前预览不发送模型请求；接入前按正式文档确认账户权限与兼容范围。</p>','<a class="primary full" href="../#api" target="_blank" rel="noopener">查看 API 文档 ↗</a>');},
 close:closeSheet,
 motion(){state.paused=!state.paused;$('.hero')?.classList.toggle('paused',state.paused);actions.menu();},
 models(){openSheet('选择模型','<div class="notice">模型目录尚未接入</div><p>正式服务会在这里展示可用模型、能力和计费规则。当前不预设可用性或价格。</p>','<button class="secondary full" data-action="close">继续编辑</button>');},
 send(){if(!selectedModel(state)){actions['pick-model']();return;}if(!state.draft.trim()){toast('先写下你的问题或需要处理的文本。');$('#task-input').focus();return;}saveDraft();openSheet('想法已保留','<p>当前为界面预览，尚未连接模型服务。内容只保存在本设备，没有发出模型请求。</p>',`<button class="primary full" data-action="close">回到输入</button>${state.role==='member'?'<button class="secondary full" data-action="admin-help">了解企业额度</button>':'<button class="secondary full" data-nav="purchase">查看购买流程 →</button>'}`);},
 'clear-draft'(){if(!state.draft){toast('当前没有本地草稿。');return;}openSheet('清除本地草稿？','<p>只清除当前预览身份在本设备保存的输入内容。清除后无法恢复。</p>','<button class="primary full" data-action="close">保留草稿</button><button class="secondary full" data-action="confirm-clear">确认清除</button>');},
 'confirm-clear'(){state.draft='';saveDraft();closeSheet();render();toast('已清除当前身份的本地草稿。');},
 notifications(){openSheet('通知','<p>目前没有可读取的通知。到账、任务进度和额度提醒会在正式服务接入后显示。</p>','<button class="secondary full" data-action="close">知道了</button>');},
 'admin-help'(){openSheet('由企业管理员分配','<p>企业成员使用管理员分配的额度。额度不足时，请联系本企业管理员；个人余额不会自动补扣企业消费。</p><div class="notice">当前未连接企业账户，暂无管理员联系信息。</div>','<button class="secondary full" data-action="close">返回</button>');},
 'order-help'(){openSheet('订单与售后','<p>真实订单会展示支付、到账、退款和开票状态。当前未创建订单。</p><p>如需咨询服务，可通过官网联系沐仞。</p>','<a class="primary full" href="../#enterprise" target="_blank" rel="noopener">前往官网 ↗</a>');},
 'account-help'(){openSheet('账户与安全','<p>此预览尚未连接账户。个人与企业使用独立登录入口，企业身份与角色由真实账户权限决定。</p>','<button class="secondary full" data-action="close">返回</button>');},
 help(){openSheet('我们在这里','<p>了解服务、计费和企业接入，可查看官网文档或联系沐仞团队。</p>','<a class="primary full" href="../#docs" target="_blank" rel="noopener">查看接入文档 ↗</a><a class="secondary full" href="mailto:fathompeak@163.com">邮件联系沐仞</a>');},
 api(){openSheet('让 AI 接入你的业务','<p>开发者可以通过网页控制台管理 API Key，并查看接入文档。也可以在小程序里在线试用模型。</p>','<a class="primary full" href="../#docs" target="_blank" rel="noopener">查看 API 文档 ↗</a><a class="secondary full" href="../#console" target="_blank" rel="noopener">打开网页控制台 ↗</a>');},
 invite(){openSheet('邀请团队成员','<p>管理员通过工作邮箱邀请成员，并为其配置角色和消费限额。</p><label class="form-field">工作邮箱<input type="email" placeholder="填写成员的工作邮箱" autocomplete="off"></label><label class="form-field">角色<select><option>企业成员</option></select></label><div class="notice">企业账户尚未连接。此表单仅供界面评审，不保存或发送邀请。</div>','<button class="primary full" disabled>邀请服务尚未开通</button>');},
 about(){openSheet('沐仞 · FathomPeak','<p>栉风沐雨，登高万仞。</p><p>这是一份小程序交互 UI 预览，沿用现有官网色卡、字体与排线插画。可以浏览界面及保存本地草稿，生成和支付尚未接入。</p>','<button class="primary full" data-action="close">继续浏览</button>');},
 menu(){const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;openSheet('更多',`<button class="menu-row" data-action="motion" aria-pressed="${state.paused||reduced}" ${reduced?'disabled':''}>${icon('play')}${reduced?'已遵循系统：减少动态':state.paused?'开启背景动态':'暂停背景动态'}<span class="hint">${state.paused||reduced?'已暂停':'播放中'}</span></button><button class="menu-row" data-nav="service">${icon('models')}服务说明<span class="arrow">›</span></button><button class="menu-row" data-action="help">${icon('play')}帮助与联系<span class="arrow">›</span></button><button class="menu-row" data-action="about">${icon('batch')}关于预览<span class="arrow">›</span></button>`);}
};
document.addEventListener('click',async event=>{
 const button=event.target.closest('button,[data-nav]');if(!button)return;
 if(button.dataset.model){state.modelId=button.dataset.model;saveIntent();navigate('model');return;}
 if(button.dataset.pickModel){state.modelId=button.dataset.pickModel;saveIntent();closeSheet();render();return;}
 if(button.dataset.vendor){const top=screen.scrollTop;state.vendor=button.dataset.vendor;render({focus:false});screen.scrollTop=top;document.querySelector('[data-vendor="'+state.vendor+'"]').focus({preventScroll:true});return;}
 if(button.dataset.client){const top=screen.scrollTop;state.client=button.dataset.client;render({focus:false});screen.scrollTop=top;document.querySelector('[data-client="'+state.client+'"]').focus({preventScroll:true});return;}
 if(button.dataset.copy){const text=button.dataset.copy==='endpoint'?endpoint:selectedModel(state)?.name;if(!text)return;try{await navigator.clipboard.writeText(text);toast('已复制'+(button.dataset.copy==='endpoint'?'接入地址':'模型名称'));}catch(error){toast('未能复制，请手动选择配置文本。');}return;}
 if(button.dataset.nav){if(sheet.open)closeSheet();navigate(button.dataset.nav);return;}
 if(button.dataset.reviewPage){const page=button.dataset.reviewPage;if(page==='team'&&state.role!=='admin')setRole('admin');if(page==='estimate')state.estimateFrom='home';navigate(page);return;}
 if(button.dataset.task){state.task=button.dataset.task;saveDraft();state.page='work';render();return;}
 if(button.dataset.filter){state.filter=button.dataset.filter;render();return;}
 if(button.dataset.usageFilter){state.usageFilter=button.dataset.usageFilter;render();return;}
 if(button.dataset.action){const action=button.dataset.action;if(sheet.open&&!['close','confirm-clear'].includes(action))closeSheet();actions[action]?.();}
});
readIntent();readDraft();render({focus:false});
