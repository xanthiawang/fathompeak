import {catalog, selectedModel, priceCondition, endpoint, estimateNumber, estimateCosts, costLabel} from './catalog.js?v=d40-20261018';
import {icons} from './icons.js';
export const icon = (name) => icons[name] || icons.play;
export const escapeHTML = (value) => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const roles = {personal:'个人账户', admin:'企业管理员', member:'企业成员'};
export const tasks = {ask:['自由问答','从一个问题，开始新的思路。'],write:['写作与改写','把想法写清楚，让表达更自然。'],summary:['文本总结','粘贴长文本，整理重点与脉络。'],translate:['翻译','让表达跨越语言。']};
export const pageInfo = {
 home:['01','从价格，到接入','模型与 Token 是销售主线。先选模型、核对计费，再充值并接入自己的工具。体验帮助选型，购买后在 API 接入中完成配置。',['查看模型参考价','核对适用价格与条件','充值并配置 API']],
 estimate:['01','先算清，再充值','用量与单价分开输入。历史输出参考与手填公开价测算分开展示，完整价格表接入前不生成成交报价。',['选择模型与预计用量','核对价格来源与折后预算','充值后按实际用量计费']],
 model:['01','价格，逐项看清','区分历史目录参考价、当前适用价与折扣。未配置价格不推算，充值金额不换算成固定 Token 数。',['确认模型与计费项','充值账户额度','继续 API 接入']],
 api:['02','把额度用进应用','API Key、接入地址与模型名称组成交付入口。未连接账户时不生成密钥，也不展示虚假的可用状态。',['创建并安全保存 Key','配置地址与模型','首次调用后核对用量']],
 connect:['02','接入，有明确下一步','按现有官网 OpenAI 兼容文档展示参数。API Key 在真实账户创建后获取，当前只复制非敏感配置。',['选择接入模型','配置工具或应用','核对请求与消费记录']],
 work:['03','试用，为了选型','在线试用用于体验模型，作为 API 采购的辅助入口。保留模型意向与本设备草稿，不伪造响应。',['确认模型','输入测试内容','接入自己的应用']],
 login:['05','登录：先认人，再绑微信','微信只做快捷登录，不单独建号。先用微信手机号快速验证，或手机号 / 邮箱验证码，找到已有账号，再把当前微信绑上去。三种结果：手机号已注册就绑定原账号；新手机号就建号并绑定；手机号的账号已绑别的微信，就提示用验证码登录后换绑。',['验证手机号或邮箱','找到或新建账号','绑定当前微信']],
 'login-code':['05','验证码登录','用户拒绝微信手机号授权、或当初用邮箱注册时走这里。验证通过同样绑定当前微信；GitHub 用户需先在网页端绑定手机号或邮箱。',['输入手机号或邮箱','验证码校验','绑定当前微信']],
 security:['05','一个账号，多种登录','手机号、邮箱、微信、GitHub 都挂在同一个账号下。每种方式只能绑一个账号，至少保留一种；GitHub 只能在网页端授权绑定。',['查看已绑定方式','绑定或更换','至少保留一种']],
 oasis:['04','我的绿洲','调用模型时冒出能量，收满 4 份长成一棵树，绿洲从枯地逐步复苏。邀请好友合种是第二个坑位，好友首次调用后双方各得 ¥20。',['调用产生能量','收能量种树','邀请好友合种']],
 invite:['04','邀请好友','好友实名并完成首次调用后，双方各得 ¥20 代金券。奖励挂在注册、实名、调用这些真实行为上，不挂在分享动作上，避开微信诱导分享规则。',['发送邀请','好友实名注册','首次调用后双方到账']],
 purchase:['03','充值调用额度','购买统一账户额度，所选模型只是接入意向。个人与企业均享公开价 4 折起，按模型实际用量扣费。',['填写充值金额','核对账户与计费规则','到账后创建 API Key']],
 confirm:['03','核对采购归属','确认金额与账户，清楚区分充值和模型消费。支付服务未接入时不能承诺到账或可调用。',['确认充值信息','支付后确认到账','进入 API 配置']],
 billing:['04','资金与用量，分别记','充值订单记录资金变化；调用明细记录 Token 和费用。二者共享账本，保留各自的查询入口。',['余额与充值','Token 用量与费用','订单及发票']],
 orders:['04','充值订单','查询支付、到账及售后；每次 API 请求记录在调用明细，不重复生成充值订单。',['筛选订单状态','确认到账','处理售后']],
 usage:['04','调用明细','按模型、调用来源查看 Token 和实际费用；没有账户数据时展示未连接状态。',['确认账户归属','筛选调用来源','核对 Token 与扣费']],
 account:['04','个人与企业，各有归属','余额、用量账单、订单发票和企业管理集中在此。企业成员不出现无权限的充值操作。',['账户与企业','优惠与采购咨询','帮助与安全']],
 team:['06','团队额度管理','管理员配置成员、额度和可用模型。当前未接入真实组织，保留准确的未连接状态。',['核对组织','分配权限与额度','查看调用账单']],
 service:['07','按 Token 使用模型','解释账户额度、模型计费和 API 接入的关系；基础设施业务通过企业咨询承接。',['充值账户额度','通过 API 或在线试用调用','按实际 Token 结算']]
};
const art = (name, extra='') => `<span class="art art-${name} ${extra}" aria-hidden="true"></span>`;
const row = (name,title,desc,attrs) => `<button class="task-row" ${attrs}><span class="icon-tile">${icon(name)}</span><span><strong>${title}</strong><small>${desc}</small></span><span class="arrow" aria-hidden="true">›</span></button>`;
const menu = (name,title,attrs,hint='') => `<button class="menu-row" ${attrs}>${icon(name)}<span>${title}</span>${hint?`<span class="hint">${hint}</span>`:''}<span class="arrow" aria-hidden="true">›</span></button>`;
const account = (s) => `<div class="account-line"><span class="account-kind">${icon(s.role==='personal'?'acct':'members')}${roles[s.role]}</span><button class="icon-btn" data-action="notifications" aria-label="通知">${icon('ad-alerts')}</button></div>`;
const back = (title='home',label='返回') => `<div class="back-row"><button data-nav="${title}">← ${label}</button></div>`;
const empty = (name,title,desc,button='') => `<div class="empty">${art(name)}<h2>${title}</h2><p>${desc}</p>${button}</div>`;
const purchaseAction = (s,text='充值') => s.role==='member'?`<button class="text-button" data-action="admin-help">联系管理员 →</button>`:`<button class="text-button" data-nav="purchase">${text} →</button>`;


// Explicit design scenario requested by the product owner, not a fetched balance.
const balancePreview = s => s.role==='member'?'—':'0.00';
const walletBody = s => `<div><span class="balance-label">${s.role==='member'?'企业分配额度':'账户余额'}</span><div class="wallet-amount"><span>¥</span>${balancePreview(s)}</div></div>${s.role==='member'?'<button class="secondary" data-action="admin-help">联系管理员 →</button>':'<button class="primary recharge-cta" data-nav="purchase">立即充值 <span aria-hidden="true">↗</span></button>'}`;
const wallet = s => `<section class="wallet-panel" aria-label="账户余额与充值">${walletBody(s)}</section>`;
const tree = (col,extra='') => `<span class="tree-sprite ${extra}" style="--col:${col*25}%" aria-hidden="true"></span>`;
const sceneOf = (o) => o.trees>=2?'revived':o.trees>=1?'camp':'withered';
const oasisCard = (s) => {const o=s.oasis;return `<button class="oasis-card" data-nav="oasis"><span class="oasis-thumb oasis-${sceneOf(o)}">${o.pending?`<span class="thumb-tag">${o.pending} 份能量待收</span>`:''}</span><span class="oasis-card-body"><span class="benefit-title"><span class="oasis-name">${icon('leaf')}${s.role==='member'?'我的绿洲':'邀好友，合种一棵树'}</span></span>${s.role==='member'?`<strong>${o.trees}<small>棵树已种下</small></strong><span class="oasis-card-meta">用绿电调用，让绿洲生长</span>`:`<strong><span>¥</span>20<small>代金券</small></strong><span class="oasis-card-meta">好友首次调用后，你和好友各得一张</span>`}<span class="benefit-link">进入我的绿洲 <span aria-hidden="true">↗</span></span></span></button>`;};
const inviteStrip = (s) => s.role==='member'?'':`<button class="invite-strip" data-nav="invite"><span><span class="benefit-title">邀请好友 · 一起种树</span><strong><span>¥</span>20 <small>双方各得</small></strong><span class="benefit-link">好友实名并首次调用后到账 <span aria-hidden="true">↗</span></span></span>${tree(4)}</button>`;
const benefits = (s) => `<section class="benefit-grid" aria-label="新用户与教育权益"><button class="benefit-card welcome-benefit" data-action="welcome-gift"><span class="benefit-title">注册礼包</span><strong><span>¥</span>68 <small>试用券</small></strong><span class="benefit-link">了解新用户礼包 <span aria-hidden="true">↗</span></span></button><button class="benefit-card education-benefit" data-action="education"><span class="benefit-title">教育优惠 ${icon('acct')}</span><p>学生、教师<br>与实验室专享</p><span class="benefit-link">查看认证与优惠 <span aria-hidden="true">↗</span></span></button></section>`;

export function modelRows(s) {
 const q=(s.query||'').trim().toLowerCase();
 const list=catalog.filter(m=>(s.vendor==='全部'||m.vendor===s.vendor)&&(!q||(m.name+' '+m.vendor).toLowerCase().includes(q)));
 return list.length?list.map(m=>`<button class="model-row" data-model="${m.id}"><span class="model-title">${m.name}<small>${m.vendor} · ${m.type.join(' / ')}</small></span><span class="model-price"><b>¥${m.mkt.toFixed(2)}</b><small>公开参考价 · 输出</small></span><span class="model-condition">${priceCondition(m)}<span class="ours">沐仞价 4 折起</span></span><span class="model-arrow" aria-hidden="true">↗</span></button>`).join(''):'<div class="empty subtle"><h2>没有匹配的模型</h2><p>试试其他名称，或清除筛选条件。</p><button class="secondary" data-action="reset-models">清除筛选</button></div>';
}
function home(s) {
 return `<section class="hero api-hero hero-wallet ${s.paused?'paused':''}" aria-label="模型 API 与账户余额"><div class="ambient" aria-hidden="true"></div><h1>更低的成本，<br>接入你的 AI。</h1><p>主流模型 API · 按 Token 计费<br>个人与企业，公开价 <b class="discount"><span>4</span> 折起</b><br><button class="text-button" data-action="pricing-help">计费说明 ↗</button></p>${art('key')}<div class="hero-balance">${walletBody(s)}</div></section>
 ${benefits(s)}
 ${oasisCard(s)}
 <button class="quiet-card trail-card estimate-entry" data-action="estimate"><span><span class="entry-title">充值前，先算算费用</span><span class="entry-desc">选模型、填预计用量，对比公开价和折后预算。</span><span class="entry-link">开始测算 →</span></span>${art('tag')}</button>
 <div class="section-head" id="market-heading"><h2>模型市场</h2></div>
 <label class="search-field">${icon('models')}<input type="search" id="model-search" placeholder="搜索模型或厂商" aria-label="搜索模型或厂商" value="${escapeHTML(s.query||'')}"></label>
 <div class="pills vendor-pills" aria-label="模型厂商">${['全部',...new Set(catalog.map(m=>m.vendor))].map(v=>`<button data-vendor="${v}" aria-pressed="${s.vendor===v}">${v}</button>`).join('')}</div>
 <p class="catalog-note">以下为公开参考价（输出），沐仞价 4 折起。</p><div class="model-list" id="model-list">${modelRows(s)}</div>
 <div class="quiet-card trail-card"><div><h3>用量较大？单独报价。</h3><p>企业与团队按模型、用量和服务要求采购。</p><button class="text-button" data-action="sales">咨询企业采购 →</button></div>${art('sign')}</div>
 <div class="menu-group">${menu('play','在线试用模型','data-nav="work"','辅助选型')}${menu('orders','计费说明','data-action="pricing-help"')}</div>`;
}
function model(s) {
 const m=selectedModel(s);
 if(!m)return `${back()}<h1 class="page-title">先选一个模型</h1><button class="primary" data-nav="home">查看模型市场</button>`;
 return `${back('home','模型市场')}<h1 class="page-title model-heading">${m.name}</h1><p class="page-subtitle">${m.vendor} · ${m.type.join(' / ')} · 目录上下文 ${m.ctx}</p><div class="price-panel"><span>公开参考价 · 输出</span><div><b class="mono">¥${m.mkt.toFixed(2)}</b><small>/ 百万 Token</small></div><p>${priceCondition(m)} · 2026-10-13</p><p class="ours">沐仞价：公开价 4 折起</p></div><button class="secondary full" data-action="estimate">算算这个模型的费用 →</button><p class="model-description">${m.desc}</p><dl class="detail-list"><div><dt>适用折扣</dt><dd>个人与企业均享公开价 4 折起</dd></div></dl><div class="notice">充值到统一账户余额，按调用时适用价格扣费。选择此模型不代表购买该模型专属套餐。</div><div class="purchase-footer">${s.role==='member'?'<button class="primary full" data-action="admin-help">联系管理员分配额度</button>':'<button class="primary full" data-nav="purchase">充值并接入此模型 →</button>'}<button class="text-button full" data-nav="connect">已有额度？查看 API 配置 →</button></div><div class="menu-group">${menu('play','在线试用此模型','data-nav="work"')}${menu('members','咨询企业报价','data-action="sales"')}</div>`;
}
export function estimateResult(s) {
 const e=s.estimate,m=catalog.find(m=>m.id===e.modelId),result=m?estimateCosts(e):null;
 const output=estimateNumber(e.output);
 return `<section class="estimate-result" aria-label="费用对比"><h2>同模型，算算能省多少</h2><p class="input-note">${result?'按你填写的公开单价测算 · 未核验':'补齐用量与官方单价后，显示折后预算。'}</p><dl class="estimate-comparison"><div><dt>公开价预算</dt><dd>${result?costLabel(result.publicCost):'—'}</dd></div><div class="estimate-discount"><dt>沐仞 4 折预算</dt><dd>${result?costLabel(result.discountCost):'—'}</dd></div><div><dt>预计节省</dt><dd>${result?costLabel(result.saving):'—'}</dd></div></dl>${result&&result.discountCost>0&&s.role!=='member'?`<button class="primary full estimate-recharge" data-action="estimate-recharge">按 ${costLabel(Math.max(.01,Math.ceil(result.discountCost*100)/100))} 充值 →</button>`:''}<p class="input-note">按最低 4 折估算，实际折扣以模型与用量为准。不含缓存与阶梯计价。</p></section>
 ${m?`<details class="estimate-reference"><summary>查看公开参考价</summary><p>${m.name} · ${m.seen}<br>${priceCondition(m)} · ¥${m.mkt.toFixed(2)} / 百万 Token</p><p>输出小计：<strong>${output===null?'—':costLabel(output*m.mkt)}</strong></p></details>`:''}`;
}
function estimate(s) {
 const e=s.estimate;
 const field=(key,label,placeholder)=>`<label class="form-field" for="estimate-${key}">${label}<input id="estimate-${key}" data-estimate="${key}" inputmode="decimal" autocomplete="off" maxlength="13" placeholder="${placeholder}" value="${escapeHTML(e[key])}" aria-describedby="estimate-help estimate-error"></label>`;
 return `${back(s.estimateFrom||'home',({model:'模型详情',account:'我的'})[s.estimateFrom]||'模型市场')}<h1 class="page-title">算算费用</h1><p class="page-subtitle">选一个模型，看看预计花多少、能省多少。</p>
 <form id="estimate-form" novalidate><label class="form-field" for="estimate-model">选择模型<select id="estimate-model" aria-label="选择模型"><option value="">请选择模型</option>${catalog.map(m=>`<option value="${m.id}" ${m.id===e.modelId?'selected':''}>${m.name}</option>`).join('')}</select></label>
 <fieldset class="estimate-fields"><legend>预计用量 <span>百万 Token</span></legend><div class="estimate-inputs">${field('input','输入用量','填写输入量')}${field('output','输出用量','填写输出量')}</div><div class="pills quick-usage" aria-label="快速填写用量"><span class="quick-label">快速填写</span>${[1,10,100].map(v=>`<button type="button" data-usage-preset="${v}" aria-label="输入、输出各 ${v} 百万 Token">各 ${v}</button>`).join('')}</div><p class="input-note">单位：百万 Token（1 = 100 万）。没有该项用量时填写 0。</p></fieldset>
 <details class="estimate-rates" open><summary>官方公开单价 <span>必填 · 元 / 百万 Token</span></summary><p class="input-note">在模型厂商官网的价格页，找到同一模型、同一计费档的输入价和输出价填在这里。</p><div class="estimate-inputs">${field('inputRate','输入单价','元 / 百万 Token')}${field('outputRate','输出单价','元 / 百万 Token')}</div></details>
 <p class="input-note" id="estimate-help">支持非负数字，最多 6 位整数与 6 位小数；用量为 0 的项目可不填单价。</p><p class="field-error" id="estimate-error" role="alert"></p><button class="primary full" type="submit">计算费用</button></form>
 <div id="estimate-result" aria-live="polite" aria-atomic="true">${estimateResult(s)}</div><div class="estimate-footer">${s.role==='member'?'<button class="secondary full" data-action="admin-help">联系管理员分配额度</button>':'<button class="secondary full" data-nav="purchase">直接去充值</button>'}<button class="text-button full" data-action="pricing-help">查看计费说明</button><p class="input-note">${s.role==='member'?'企业成员的额度由管理员分配。':'算出结果后，可以把折后预算一键带入充值金额；充值仍进入统一账户余额。'}</p></div>`;
}
function api(s) {
 const m=selectedModel(s);
 return `${account(s)}<h1 class="page-title">API 接入</h1><p class="page-subtitle">把模型能力，接入你自己的工具和应用。</p>${wallet(s)}<div class="section-head"><h2>我的 API Key</h2></div><div class="quiet-card key-empty">${art('key')}<h3>还没有 API Key</h3><p>完整 Key 只在创建时显示一次，请妥善保存。</p><button class="secondary" data-action="create-key">创建 API Key</button></div><div class="section-head"><h2>接入准备</h2></div><div class="setup-steps"><div><b>01</b><span>充值调用额度<small>按模型实际 Token 用量扣费</small></span></div><div><b>02</b><span>创建 API Key<small>用于调用鉴权，额度属于账户</small></span></div><div><b>03</b><span>配置地址与模型<small>${m?m.name:'选择模型后查看接入参数'}</small></span></div></div><button class="secondary full" data-nav="connect">查看接入配置 →</button><div class="menu-group">${menu('models','选择接入模型','data-action="pick-model"',m?'已选模型':'')}${menu('play','在线试用','data-nav="work"')}${menu('orders','接入文档','data-action="api-docs"')}</div>`;
}
function connect(s) {
 const m=selectedModel(s);
 return `${back('api','API 接入')}<h1 class="page-title">接入你的应用</h1><p class="page-subtitle">OpenAI 兼容配置 · 地址、密钥、模型，三项完成接入准备。</p><div class="config-card"><label>Base URL</label><code>${endpoint}</code><button class="text-button" data-copy="endpoint">复制地址</button></div><div class="config-card"><label>API Key</label><p>创建 Key 后填入这里。</p><button class="text-button" data-action="create-key">创建 Key →</button></div><div class="config-card"><label>模型名称</label><code>${m?m.name:'尚未选择模型'}</code><div class="config-actions">${m?'<button class="text-button" data-copy="model">复制模型名</button>':''}<button class="text-button" data-action="pick-model">${m?'更换':'选择'}模型</button></div></div><div class="section-head"><h2>用在哪里</h2></div><div class="pills" aria-label="接入方式"><button data-client="tool" aria-pressed="${s.client==='tool'}">客户端工具</button><button data-client="code" aria-pressed="${s.client==='code'}">自己的应用</button></div>${s.client==='code'?`<div class="quiet-card"><h3>服务端配置</h3><p>将 Base URL 和模型名称写入应用配置；API Key 存入服务端环境变量，避免放进网页或小程序前端。</p><button class="text-button" data-action="api-docs">查看调用示例 →</button></div>`:`<div class="quiet-card"><h3>支持自定义 API 的客户端</h3><p>官网列有 Cherry Studio、Lobe Chat、DeepChat 等接入指引。添加 OpenAI 兼容服务商，再填写上述三项；菜单和兼容性以具体版本为准。</p><button class="text-button" data-action="api-docs">查看客户端教程 →</button></div>`}<p class="input-note">配置来自现有官网文档。当前未做在线调用验证；模型能否调用以账户开通范围为准。</p><button class="text-button full" data-nav="billing">接入后，查看用量账单 →</button>`;
}
function billing(s) {
 return `${back('account','我的')}<h1 class="page-title">用量账单</h1><p class="page-subtitle">充值、Token 消耗与费用，在这里核对。</p><div class="balance-card"><div class="label">${s.role==='member'?'企业分配额度':'账户余额'}</div><div class="amount">${s.role==='member'?'—':'¥0.00'}</div><div class="foot">${purchaseAction(s)}</div></div><div class="summary-grid"><div><small>本月 Token</small><b>—</b><p>暂无调用</p></div><div><small>本月消费 · ¥</small><b>—</b><p>暂无消费</p></div></div><section class="share-card">${tree(4)}<div class="share-head"><span>${new Date().getMonth()+1} 月 · 我的绿电账单</span><button class="text-button" data-action="share-month">分享 ↗</button></div><div class="share-stats"><div><small>用了</small><b>—</b><p>Token</p></div><div><small>比官方价省</small><b>—</b><p>元</p></div><button data-nav="oasis"><small>种下</small><b>${s.oasis.trees}</b><p>棵树 ›</p></button></div></section><div class="menu-group">${menu('usage','调用明细','data-nav="usage"','Token 与费用')}${menu('orders','充值订单','data-nav="orders"','支付与到账')}${menu('bill','发票与售后','data-action="order-help"')}</div><div class="notice">充值订单记录资金入账；调用明细按模型记录输入、输出 Token 与实际扣费。</div><div class="section-head"><h2>模型消费</h2></div><div class="empty subtle"><h2>还没有调用记录</h2><p>开始调用后，这里按模型汇总用量与费用。</p><button class="secondary" data-nav="api">前往 API 接入</button></div>`;
}
function work(s) {
 const [name,description]=tasks[s.task]; const m=selectedModel(s);
 return `${account(s)}<h1 class="page-title">体验模型</h1><p class="page-subtitle">先体验模型，再接入应用。${m?m.name:description}</p><div class="pills" aria-label="任务类型">${Object.entries(tasks).map(([id,t])=>`<button data-task="${id}" aria-pressed="${id===s.task}">${t[0]}</button>`).join('')}</div>
 <div class="composer-card"><label class="composer-label" for="task-input"><span>${name} · 输入内容</span><span class="mono" id="input-count">${Array.from(s.draft).length}</span></label><textarea id="task-input" placeholder="${s.task==='summary'?'粘贴需要总结的文本…':s.task==='write'?'写下想表达的内容，或粘贴需要修改的文字…':s.task==='translate'?'粘贴需要翻译的文本，并说明目标语言…':'写下你的问题，或尚未成形的想法…'}">${escapeHTML(s.draft)}</textarea><div class="composer-bottom"><button class="model-trigger" data-action="pick-model">${icon('models')}${m?m.name:'选择模型'} <span aria-hidden="true">⌄</span></button><button class="send-button" data-action="send" aria-label="开始任务">↑</button></div></div>
 <div class="draft-meta"><span id="draft-status">${s.draft?'已恢复草稿':'草稿会自动保存'}</span><button data-action="clear-draft">清除草稿</button></div>
 <div class="balance-strip"><div><span class="balance-label">${roles[s.role]} · 可用额度</span><span class="balance-value">${s.role==='member'?'—':'¥0.00'}</span></div>${purchaseAction(s)}</div>
 <div class="section-head"><h2>任务记录</h2><span class="muted">属于当前账户</span></div><div class="empty subtle"><span class="icon-tile">${icon('play')}</span><h2>从第一个问题开始</h2><p>完成的任务和结果会保留在这里，<br>随时回来，接着往下想。</p></div>`;
}
function purchase(s) {
 if(s.role==='member')return `${back('account')}<h1 class="page-title">企业额度</h1>${empty('key','由管理员统一分配','请联系企业管理员补充或调整你的可用额度。','<button class="primary" data-action="admin-help">联系管理员</button>')}`;
 return `${back(s.from||'home')}<h1 class="page-title">充值 Token 调用额度</h1><p class="page-subtitle">充值至账户余额，按模型实际 Token 用量扣费。</p><div class="steps"><b>01 填写金额</b><span>02 核对信息</span><span>03 支付与到账</span></div>
 <div class="balance-card"><div class="label">${roles[s.role]} · 可用额度</div><div class="amount">${s.role==='member'?'—':'¥0.00'}</div>${art('tag')}</div>
 <form id="amount-form" novalidate><label class="field-label" for="amount">充值金额</label><div class="pills quick-amounts" aria-label="常用金额">${[100,500,1000].map(v=>`<button type="button" data-amount-preset="${v}">¥${v}</button>`).join('')}</div><div class="amount-input"><span aria-hidden="true">¥</span><input id="amount" name="amount" inputmode="decimal" autocomplete="off" placeholder="填写金额" value="${escapeHTML(s.amount)}" aria-describedby="amount-help amount-error"></div><p class="input-note" id="amount-help">人民币账户余额；不同模型单价不同，不换算成固定 Token 数。</p><p class="field-error" id="amount-error" role="alert"></p><dl class="detail-list"><div><dt>归属账户</dt><dd>${roles[s.role]}</dd></div><div><dt>接入意向</dt><dd>${selectedModel(s)?.name||'稍后选择模型'}</dd></div><div><dt>适用价格</dt><dd>公开价 4 折起</dd></div></dl><div class="purchase-footer"><button class="primary full" type="submit">下一步，核对信息 <span aria-hidden="true">→</span></button></div></form>`;
}
function confirm(s){
 return `${back('purchase','修改金额')}<h1 class="page-title">确认充值信息</h1><p class="page-subtitle">确认归属账户，再继续下一步。</p><div class="steps"><span>01 填写金额</span><b>02 核对信息</b><span>03 支付与到账</span></div><div class="quiet-card"><span class="muted small">本次填写金额</span><div class="page-title mono">¥${escapeHTML(s.amount)}</div><span class="small muted">充值到账户余额</span></div><dl class="detail-list"><div><dt>归属账户</dt><dd>${roles[s.role]}</dd></div><div><dt>充值内容</dt><dd>账户余额</dd></div><div><dt>接入意向</dt><dd>${selectedModel(s)?.name||'稍后选择模型'}</dd></div><div><dt>模型单价与折扣</dt><dd>公开价 4 折起</dd></div><div><dt>支付方式</dt><dd>微信支付</dd></div></dl><div class="purchase-footer"><button class="primary full" data-nav="orders">微信支付</button><button class="text-button full" data-nav="connect">先查看 API 接入配置 →</button></div>`;
}
function orders(s){
 return `${back('account','我的')}<h1 class="page-title">充值订单</h1><p class="page-subtitle">购买、到账与售后，都有迹可循。</p><div class="pills" aria-label="订单状态">${['全部','待支付','处理中','已完成','退款'].map(f=>`<button data-filter="${f}" aria-pressed="${s.filter===f}">${f}</button>`).join('')}</div>${empty('tag',s.filter==='全部'?'你的订单，会在这里':'暂无'+s.filter+'订单','充值后，在这里查看购买记录、到账状态与售后进度。',s.role==='member'?'<button class="secondary" data-nav="api">API 接入</button>':'<button class="primary" data-nav="purchase">去充值 →</button>')}<div class="menu-group">${menu('usage','查看 AI 消费明细','data-nav="usage"')}${menu('sec','订单与售后帮助','data-action="order-help"')}</div>`;
}
function accountView(s){
 return `<section class="account-hero" aria-label="账户概览"><div class="account-art" aria-hidden="true"></div><div class="profile"><div class="avatar" aria-hidden="true">沐</div><div><h1>${roles[s.role]}</h1><p>${s.role==='personal'?'个人使用，独立管理。':s.role==='admin'?'企业服务，统一管理。':'专注任务，额度由企业分配。'}</p></div></div><div class="hero-balance">${walletBody(s)}</div></section>${benefits(s)}${oasisCard(s)}<div class="menu-group">${s.role!=='member'?menu('members','邀请好友','data-nav="invite"','双方各得 ¥20'):''}${menu('usage','用量账单','data-nav="billing"','Token 与费用')}${menu('bill','算算费用','data-action="estimate"','充值前预估')}${menu('orders','充值订单','data-nav="orders"')}${menu('bill','发票与售后','data-action="order-help"')}${s.role==='admin'?menu('members','成员与额度','data-nav="team"'):''}${s.role==='member'?menu('members','我的企业额度','data-action="admin-help"'):''}${menu('keys','API 接入','data-nav="api"')}</div><div class="menu-group">${menu('sec','账户与安全','data-nav="security"',s.binds.wechat?'手机号 · 微信':'手机号')}${menu('members','企业采购与合作','data-action="sales"')}${menu('play','帮助与联系','data-action="help"')}</div><div class="menu-group">${menu('models','服务说明','data-nav="service"')}${menu('home','首页背景动态','data-action="motion"',s.paused?'已暂停':'播放中')}${menu('batch','关于沐仞','data-action="about"')}</div><p class="input-note" style="text-align:center;margin-top:24px">${s.role==='personal'?'个人与企业使用独立登录入口。':'当前页面仅呈现企业账户信息。'}</p>`;
}
function oasis(s){
 const o=s.oasis, stage=Math.min(o.energy,4), scene=sceneOf(o);
 const names=['种子','发芽','树苗','成树','成熟'];
 const balls=Array.from({length:o.pending},(_,i)=>`<button class="energy-ball" style="--x:${[14,44,56,84][i%4]}%;--y:${[30,16,58,22][i%4]}%" data-action="collect-energy" aria-label="收取 1 份能量">+1<small>${o.source[i]||'调用'}</small></button>`).join('');
 return `${back('account','我的')}<h1 class="page-title">我的绿洲</h1><div class="title-row"><p class="page-subtitle">每一次绿电调用，都让绿洲多一点生机。</p><button class="text-button" data-action="oasis-share">分享 ↗</button></div>
 <section class="oasis-scene oasis-${scene}" aria-label="绿洲">${Array.from({length:Math.min(o.trees,4)},(_,i)=>`<span class="oasis-slot grown" style="left:${[56,12,90,58][i]}%;top:${[88,52,80,38][i]}%">${tree(4)}</span>`).join('')}${balls}<span class="oasis-slot slot-a">${tree(stage)}<span class="slot-tag">${names[stage]} · ${stage}/4</span></span><span class="oasis-slot slot-b">${o.cotree?tree(1,'co'):''}<span class="slot-tag">${o.cotree?'与好友合种':'等好友合种'}</span></span></section>
 <div class="oasis-progress"><div><span class="muted small">这棵树</span><b>${names[stage]}</b></div><div class="dots" aria-label="能量 ${stage} / 4">${[0,1,2,3].map(i=>`<i class="${i<stage?'on':''}"></i>`).join('')}</div><span class="muted small">${o.pending?`有 ${o.pending} 份能量待收`:'暂无待收能量'}</span></div>
 <div class="summary-grid"><div><small>已种下</small><b>${o.trees}</b><p>棵树</p></div><div><small>与好友合种</small><b>${o.cotree?1:0}</b><p>棵树</p></div></div>
 <div class="section-head"><h2>能量从哪里来</h2></div><div class="setup-steps"><div><b>01</b><span>调用模型<small>每次用绿电 Token 调用，绿洲里会冒出能量</small></span></div><div><b>02</b><span>收满 4 份<small>种子长成一棵树，绿洲随之复苏</small></span></div><div><b>03</b><span>邀请好友合种<small>好友首次调用后，双方各得 ¥20 代金券</small></span></div></div>
 <div class="purchase-footer">${s.role==='member'?'':'<button class="primary full" data-nav="invite">邀请好友合种</button>'}<button class="secondary full" data-action="oasis-share">生成分享卡</button><button class="text-button full" data-nav="work">去调用模型 →</button></div>`;
}
const agree = (s) => `<label class="agree"><input type="checkbox" id="login-agree" ${s.agree?'checked':''}><span>我已阅读并同意《用户服务协议》和《隐私政策》</span></label>`;
const codeField = (id,label,ph) => `<label class="form-field">${label}<input id="${id}" placeholder="${ph}" autocomplete="username"></label><label class="form-field">验证码<span class="code-row"><input id="${id}-code" inputmode="numeric" maxlength="6" placeholder="6 位验证码" autocomplete="one-time-code"><button class="text-button" data-action="send-code">获取验证码</button></span></label>`;
function login(s){
 const org=s.loginTab==='org';
 return `<section class="account-hero login-hero" aria-label="登录"><div class="account-art" aria-hidden="true"></div><div class="profile"><div class="avatar" aria-hidden="true">沐</div><div><h1>登录沐仞</h1><p>手机号、邮箱、微信、GitHub，<br>登录的都是同一个账号。</p></div></div></section>
 <div class="seg" role="tablist" aria-label="登录类型"><button role="tab" data-login-tab="personal" aria-selected="${!org}">个人登录</button><button role="tab" data-login-tab="org" aria-selected="${org}">企业登录</button></div>
 ${org?`${codeField('org-email','工作邮箱','管理员为你添加的工作邮箱')}${agree(s)}<div class="purchase-footer"><button class="primary full" data-action="org-login">登录企业账号</button></div><p class="input-note">企业账号由管理员添加，不能在这里注册。</p><button class="text-button" data-action="sales">还没有企业账号？申请开通 →</button>`
 :`<div class="purchase-footer"><button class="primary full" data-action="wx-phone">${icon('wechat')} 微信手机号快捷登录</button><button class="secondary full" data-nav="login-code">手机号或邮箱验证码登录</button></div>${agree(s)}
 <div class="quiet-card login-rule"><h3>已经有沐仞账号？</h3><p>用注册时的手机号或邮箱登录，会直接找到原账号，并把这个微信绑定上去。余额、API Key 和绿洲都还在，不会多出一个新账号。</p></div>
 <p class="input-note">GitHub 注册的账号，请先在网页控制台绑定手机号或邮箱，再回来登录。</p>`}`;
}
function loginCode(s){
 return `${back('login','返回')}<h1 class="page-title">验证码登录</h1><p class="page-subtitle">输入注册沐仞时用的手机号或邮箱。</p>${codeField('login-id','手机号或邮箱','手机号或邮箱')}${agree(s)}<div class="purchase-footer"><button class="primary full" data-action="code-login">登录</button></div><p class="input-note">验证通过后，当前微信会绑定到这个账号，下次直接进入。没有注册过的手机号或邮箱，会新建一个个人账号。</p>`;
}
function security(s){
 const b=s.binds;
 const row=(ic,name,val,act)=>`<div class="bind-row">${icon(ic)}<span><strong>${name}</strong><small>${val}</small></span>${act}</div>`;
 return `${back('account','我的')}<h1 class="page-title">账户与安全</h1><p class="page-subtitle">下面这些方式，登录的都是同一个沐仞账号。</p>
 <div class="menu-group bind-list">${row('phone','手机号',b.phone||'未绑定',`<button class="text-button" data-action="bind" data-bind="phone">${b.phone?'更换':'绑定'}</button>`)}${row('wechat','微信',b.wechat?'已绑定当前微信':'未绑定',b.wechat?'<button class="text-button" data-action="unbind-wechat">解绑</button>':'<button class="text-button" data-action="bind-wechat">绑定当前微信</button>')}${row('mail','邮箱',b.email||'未绑定',`<button class="text-button" data-action="bind" data-bind="email">${b.email?'更换':'绑定'}</button>`)}${row('github','GitHub',b.github||'未绑定','<button class="text-button" data-copy-link="console">去网页端绑定</button>')}</div>
 <p class="input-note">一个手机号、一个邮箱、一个微信，各自只能绑定一个沐仞账号。至少保留一种登录方式。</p>
 <div class="purchase-footer"><button class="secondary full" data-action="logout">退出登录</button></div>`;
}
function invite(s){
 if(s.role==='member')return `${back('account','我的')}<h1 class="page-title">邀请好友</h1>${empty('key','企业成员不参与邀请奖励','企业成员使用企业分配的额度，邀请奖励发放到个人账户。','<button class="secondary" data-nav="account">返回我的</button>')}`;
 return `${back('account','我的')}<section class="invite-card"><div class="invite-art" aria-hidden="true"></div><span class="label">邀请好友</span><h1>一起用，<br>一起种一棵树。</h1><p>好友实名并完成首次调用后，你们各得 ¥20 代金券，绿洲里多一棵合种的树。</p></section>
 <div class="invite-reward"><div><small>你得</small><b>¥20</b></div><div><small>好友得</small><b>¥20</b></div><div><small>邀请人数</small><b>不限</b></div></div>
 <div class="purchase-footer"><button class="primary full" data-action="invite-share">发给微信好友</button><button class="secondary full" data-action="invite-poster">生成邀请海报</button></div>
 <div class="section-head"><h2>怎么得奖励</h2></div><div class="setup-steps"><div><b>01</b><span>发送邀请<small>微信好友，或海报二维码</small></span></div><div><b>02</b><span>好友注册并实名<small>个人账户或企业账户均可</small></span></div><div><b>03</b><span>好友完成首次调用<small>双方各得 ¥20，绿洲多一棵树</small></span></div></div>
 <button class="summary-grid summary-link" data-nav="oasis"><div><small>已邀请</small><b>0</b><p>位好友</p></div><div><small>一起种下</small><b>${s.oasis.cotree?1:0}</b><p>棵树 · 去绿洲 ›</p></div></button>
 <div class="section-head"><h2>邀请记录</h2></div><div class="empty subtle"><h2>还没有邀请记录</h2><p>好友接受邀请后，注册、实名和首次调用的进度会显示在这里。</p></div>
 <div class="menu-group">${menu('members','成为推荐官','data-action="referrer"','好友消费持续返券')}${menu('orders','活动规则','data-action="invite-rules"')}</div>`;
}
function team(s){
 if(s.role!=='admin')return `${back('account')}<h1 class="page-title">团队管理</h1>${empty('key','需要管理员权限','成员与额度由企业管理员统一管理。','<button class="secondary" data-nav="account">返回我的账户</button>')}`;
 return `${back('account','我的账户')}<h1 class="page-title">团队，共同向前。</h1><p class="page-subtitle">统一管理成员，让每一份额度各得其所。</p><div class="summary-grid"><div><small>企业可用额度</small><b>—</b><p>由管理员分配</p></div><div><small>已加入成员</small><b>—</b><p>暂无成员</p></div></div><div class="quiet-card"><h3>团队拼量价</h3><p>成员用量合并计算。团队用量越大，全员适用的价格档位越低。</p><button class="text-button" data-action="sales">咨询价格档位 →</button></div><div class="section-head"><h2>成员与权限</h2><button class="text-button" data-action="invite">邀请成员 ＋</button></div><label class="search-field"><span aria-hidden="true">⌕</span><input id="member-search" type="search" placeholder="查找姓名或工作邮箱" aria-label="查找成员"></label><div id="member-empty">${empty('boxes','在这里，组建团队','邀请成员后，角色与可用额度会显示在这里。','<button class="secondary" data-action="invite">查看邀请方式 →</button>')}</div><div class="notice">成员可使用分配额度。购买、调整限额与停用成员由管理员操作；个人消费独立记账。</div>`;
}
function usage(s){return `${back('billing','用量账单')}<h1 class="page-title">调用明细</h1><p class="page-subtitle">${roles[s.role]} · 逐模型核对 Token 与费用。</p><div class="pills" aria-label="消费记录类型">${['全部','API 调用','在线试用'].map(f=>`<button data-usage-filter="${f}" aria-pressed="${s.usageFilter===f}">${f}</button>`).join('')}</div>${empty('book','每次调用，都有记录','每次调用后显示模型、输入与输出 Token、实际费用及结算状态。','<button class="primary" data-nav="api">前往 API 接入 →</button>')}<p class="input-note">充值记录在充值订单页查看。</p>`;}
function service(s){return `${back()}<h1 class="page-title">买额度，用模型。</h1><p class="page-subtitle">通过沐仞 API，将模型能力接入自己的应用；也可以在线试用。</p><dl class="detail-list"><div><dt>购买内容</dt><dd>模型调用额度</dd></div><div><dt>调用凭证</dt><dd>账户下创建的 API Key</dd></div><div><dt>计费方式</dt><dd>按输入、输出等实际用量</dd></div><div><dt>适用折扣</dt><dd>个人与企业均享 4 折起</dd></div></dl><div class="notice">同一充值金额可消耗的 Token 数因模型、输入/输出比例与适用价格不同而变化。</div><div class="purchase-footer"><button class="primary full" data-nav="home">查看模型与价格 →</button></div><div class="section-head"><h2>企业与基础设施</h2></div><div class="menu-group">${menu('members','企业 Token 采购','data-action="sales"')}${menu('batch','算电协同群智基座','data-action="sales"')}${menu('models','FPTM 词元一体机','data-action="sales"')}${menu('home','能源与算力节点合作','data-action="sales"')}</div>`;}
export function renderPage(s){const views={home,model,estimate,api,connect,billing,work,purchase,confirm,orders,account:accountView,team,usage,service,invite,oasis,login,'login-code':loginCode,security};return `<article class="page">${(views[s.page]||home)(s)}</article>`;}
