# 绿洲消费成长与计算额度券 · 后端开发需求

版本：2026-10-18 · 需求归属：Zixin Wang / 沐仞科技

**请后端按本文件拆任务：复用现有计费，接出最终消费事件，提供绿洲状态，补齐领券与分次抵扣。前端只展示服务端状态，不计算真实余额或发放权益。**

- [在线交互原型](https://xanthiawang.github.io/fathompeak-site/?oasis=1#console-preview)
- 前端入口：[`index.html`](../../index.html)；绿洲逻辑：[`绿洲复苏_2026-10-18.js`](../../绿洲复苏_2026-10-18.js)；样式：[`绿洲复苏_2026-10-18.css`](../../绿洲复苏_2026-10-18.css)。
- 公开页面的成长演示操作位于“成长指南”；主页面只展示场景与进度。教程状态仍是本地演示，不是新的结算来源。
- 本仓库是静态前端，**不包含实际网关、支付、数据库服务端**。现在的消费/退款/券操作为试玩，不是真实交易。
- 本文件是待实现需求。标为“已有”的接口已在现网发布前端中定位调用；只有公开 `/api/status` 直接读过 HTTP 返回，其他接口未进行真实资金写入测试。请后端先确认服务端版本、权限和返回结构。

## 1. 要交付的业务闭环

1. 新账户没有合资格消费时，绿洲从枯萎状态开始。
2. 模型调用最终扣费后，真实合资格消费累计增长；离开页面也累计。
3. 后端根据活动配置自动养树、恢复水流、修复建筑、引入动物、扩建区域。**满区自动扩建，不需要用户点击才能继续积累。**
4. 达到里程碑，明确显示下一项奖励及还差多少；用户领取后获得账户绑定的计算额度券。
5. 后续合资格调用自动分次抵扣券，剩余额度保留；显示每次抵扣、剩余、到期和退款记录。
6. 退款冲正净消费与权益资格，同一里程碑不能重复发奖。

### 本期口径

| 项目 | 开发要求 / 待确认边界 |
|---|---|
| 增长来源 | 已最终结算、实际消耗的合资格实付资金部分；充值、赠送、券抵扣部分不算实付增长 |
| 金额精度 | 原生整数 quota + 换算/价格快照；JSON 大整数用字符串。不能逐笔四舍五入到“分” |
| 归属 | 个人付款归个人；组织付款归组织；同一笔不向个人和组织重复发现金权益 |
| 企业价格 | 复用原组织专属价格、分组倍率、时段与表达式计价；直接取网关终值，不在绿洲重算 |
| 券形态 | 本需求采用“计算额度券”：可分次用、不可转让/提现、使用部分不再产生实付奖励。面额/有效期/预算需业务配置 |
| 退款后的景观 | 保留历史最高已解锁景观；净消费和奖励资格按退款重算。重达旧门槛只恢复原权益 |
| 自动播种与扩建 | 服务端按进度自动处理，前端读 regions/trees；领取稀有种子不影响普通消费继续成长 |
| 后付/订阅 | 首期规则未确认前不发真实奖励；后付需回款到用量的分摊，订阅需避免套餐购买与用量双算 |
| 商业参数 | 原型中成长门槛、券面额和有效期均是演示配置，不可直接作为正式承诺。未发布有效活动时不发券 |
| 绿电说明 | 沿用结算中的时段折扣字段；不能由绿洲进度推导电站来源、实际植树或精确减碳 |

## 2. 现有接口：复用，不重复开发

以下“已有”是**现网前端调用点已确认**；请后端补齐内部路由/结构确认，不能据此跳过联调。

| 能力 | 已有方法与路径 | 用途与限制 | 证据 |
|---|---|---|---|
| 当前身份/余额 | `GET /api/user/self` | 登录身份及钱包展示；used_quota 不等于净实付成长 | E1/E4 |
| 展示单位 | `GET /api/status` | quota 单位和币种配置；历史结算必须保留当时快照 | E1 |
| 个人消费明细 | `GET /api/log/self`、`GET /api/log/self/stat` | 明细/统计展示，不能每刷新一次就发成长 | E2/E3 |
| 全站消费明细 | `GET /api/log`、`GET /api/log/stat` | 管理员追溯与对账，不能给普通客户全站权限 | E2/E3 |
| 异步任务 | `GET /api/task`、`GET /api/task/self`；绘图 `/api/mj`、`/api/mj/self` | 任务查询；完成状态仍需关联最终扣费 | E2/E3 |
| 组织 | `GET /api/organization/`、`GET /api/organization/{id}` | 付款主体与组织资料，归属须服务端验证 | E6 |
| 组织创建/修改 | `POST /api/organization/`、`PUT /api/organization/{id}` | 已有 payment_mode、channel_ids 等表单；保持原逻辑 | E6 |
| 渠道选择 | `GET /api/organization/channel-options` | 模型可见范围沿用组织绑定渠道 | E6 |
| 默认模型价 | `GET/PATCH /api/option/model_pricing` | GET 支持重复 model 参数；PATCH `{changes:[...]}` | E1 |
| 组织模型价 | `GET/PATCH /api/organization/{id}/model_pricing` | 同上，组织覆盖或继承 C 端 | E1 |
| 价格来源预览 | `GET /api/organization/{id}/billing-preview` | data.items 中 model_name、org_price_applied；不是实际消费结算接口 | E6 |
| 充值能力/报价/支付 | `GET /api/user/topup/info`；`POST /api/user/amount`、`POST /api/user/pay` | 保持原充值流程；充值成功不产生消费成长 | E4 |
| 充值订单 | `GET /api/user/topup/self`、`GET /api/user/topup` | 分别个人/管理员；不能当模型消费订单 | E4 |
| 兑换码兑换 | `POST /api/user/topup`，body `{key}` | 将代码额度加进余额；**不是领券或使用券** | E4 |
| 兑换码管理 | `GET/POST/PUT /api/redemption/`；`GET /api/redemption/{id}`；`GET /api/redemption/search` | 创建包含 name、quota、expired_time、count；不是完整的用户券账本 | E5 |
| 订阅 | `GET /api/subscription/self`、`GET /api/subscription/plans`、`PUT /api/subscription/self/preference` | preference body `{billing_preference}`；需确认与券的资金扣减顺序 | E7 |

补充字段：日志支持分页 p/page_size、type、时间、model_name、request_id、upstream_request_id，管理员还可筛 organization_id。前端类型枚举 `CONSUME=2`、`REFUND=6`；消费字段使用 quota、prompt_tokens、completion_tokens、other。other 已有 `green_power_discount_ratio`、`green_power_time_slot`、`billing_source` 等展示分支，历史完整性待后端确认。

**不允许复用错位：** 不用 `/api/user/topup/complete` 给用户发券；不把 `/api/user/amount` 当模型价格计算；不把可兑换代码过期当作已充值余额过期；不把普通日志统计当作发奖账本。

## 3. 要补的能力与开发顺序

以下接口是建议契约，不表示线上已有；如果服务端已有同等能力，提供映射并复用。

| 顺序 / 任务 | 后端交付 | 前端依赖 | 验收出口 |
|---|---|---|---|
| **P0-1 结算底座** | 定位最终扣款/退款事务；资金来源分摊；稳定 settlement_id；同事务 outbox；退款引用 | 可以先按下文契约开发适配层 | 能用脱敏真实记录解释一笔金额、来源、组织、价格及退款；有可重放事件 |
| **P0-2 真实成长** | 幂等成长分录、自动养树/环境阶段/扩建投影、state/activity/rewards 只读接口 | 替换 localStorage 金额状态，接入自动刷新和动画 | 零消费枯萎；真实扣费增长；刷新/跨设备一致；不重复增长 |
| **P0-3 奖励与券** | 活动规则和预算、领取幂等、券账本、reserve/commit/release/refund | 领券、剩余、使用记录、自动抵扣开关 | 达标→领取→调用抵扣→剩余→退款闭环；无超扣或重复领 |
| **P0-4 联调与上线** | 对账、权限、失败补偿、灰度开关、正式配置 | 去除真实模式的模拟消费/退款/核销入口 | 第 8 节验收通过；关闭活动不影响原模型计费 |
| **P1 扩展** | 后付回款分摊、订阅参与、历史回填、稀有种子包与运营重放台 | 按确定规则增加入口 | 不重复计算资金来源、旧消费不凭估算补权益 |

P0 按依赖顺序交付，不等最后一天再联调。前端可在 P0-1 时按类型契约开发；真实奖金/券发放必须等 P0-3、P0-4 验收完成。后端仓库尚未核对，暂不承诺具体人天。

## 4. 最小新增 API 契约

### 4.1 统一约定

- 复用正式登录/会话，普通用户只能访问本人/授权组织；组织 scope 参数必须检查成员权限。不能把登录用户与实际付款主体混为一谈。
- GET 支持 `scope=personal|organization`；组织请求同时传 `organization_id`，服务端校验。个人 scope 忽略/拒绝其他主体 ID；C 端虚拟组织 0 不能让所有用户共享绿洲。
- 响应采用 `{success:true,data:T,request_id:string}`；业务错误 `{success:false,code:string,message:string,request_id:string}`，配正确 HTTP 状态。若现有约定不同，后端统一后前端适配。
- 金额/累计 quota 为整数十进制字符串；展示币种金额为定点十进制字符串。时间统一 UTC ISO 8601；日志历史时间单位由适配层处理。
- 写请求带 `Idempotency-Key`。同 key 同 body 返回原结果，同 key 不同 body 返回 409。领域唯一键仍要防止客户端换 key 重复领。
- 权限错误 401/403；主体内找不到资源 404；版本/幂等冲突 409；不符合规则 422；限流 429；暂不可用 503。重试遵守 Retry-After 与退避。

### 4.2 用户端接口

| ID | 新增方法与路径 | 请求 | 返回 / 原子性要求 |
|---|---|---|---|
| N1 | `GET /api/oasis/state` | scope、organization_id | 下方 OasisState；无历史也返回枯萎空状态；未同步返回 pending/stale，不假装零消费 |
| N2 | `GET /api/oasis/activity` | scope、organization_id、cursor、limit | `{items,next_cursor}`；事件 id/time、消费或退款、合资格变动、关联结算引用；不返回上游秘密 |
| N3 | `GET /api/oasis/rewards` | scope、organization_id、cursor、limit | `{items,next_cursor}`；Reward，条件、当前进度、状态、价值和领取规则 |
| N4 | `POST /api/oasis/rewards/{id}/claim` | body `{scope,organization_id?,expected_state_version}`；Idempotency-Key | `{grant_id,reward,voucher?,state_version}`；重新核验消费、预算、归属；唯一(campaign,payer,milestone) |
| N5 | `GET /api/benefits/vouchers` | scope、organization_id、status、cursor、limit | `{items,next_cursor}`；Voucher 列表 |
| N6 | `GET /api/benefits/vouchers/{id}/transactions` | scope、organization_id、cursor、limit | 预留/使用/释放/退回/到期分录；金额及结算引用，不泄露其他主体 |
| N7 | `GET /api/benefits/preferences` | scope、organization_id | `{auto_apply,version}`；前端可读取初始开关 |
| N8 | `PUT /api/benefits/preferences` | `{scope,organization_id?,auto_apply,expected_version}`；Idempotency-Key | 保存并返回 N7 数据；组织需付款管理权限 |

**浏览器不调用券核销接口，也不发“消费已完成”通知。** 核销发生在原网关结算中；模型调用方式保持原协议。前端“去使用”跳现有 API/体验/批量入口，不模拟一笔真实扣款。

核心返回类型（类型契约，不是实际接口响应或账户数据）：

```ts
type IntString = string;       // /^-?[0-9]+$/；金额字段按需要限制非负
// version 是不透明版本标识，前端只比较相等；不能自行加一。
type OasisState = {
  state_version: string;
  scope: { type: 'personal' | 'organization'; payer_id: string };
  campaign: null | { id: string; rule_version: string; status: 'active' | 'paused' | 'ended' };
  sync: { status: 'ready' | 'pending' | 'stale'; updated_at: string; last_settlement_at: string | null };
  progress: {
    eligible_net_quota: IntString;
    pending_quota: IntString;
    historical_high_water_quota: IntString;
    currency: string;
    eligible_net_amount: string; // 后端给定点展示值，前端不以现汇率重算
  };
  active_region_id: string;
  regions: Array<{
    id: string; order: number;
    scene_stage: 'withered' | 'water' | 'habitat' | 'thriving';
    environment: { water: boolean; vegetation_level: number; building_level: number; animals: string[] };
    progress_ratio: number; // 0..1，后端投影给出
    trees: Array<{ id: string; slot_id: string; species: string; stage: 'seed'|'sprout'|'young'|'mature'; progress_ratio: number }>;
  }>;
  next_reward: null | { reward_id: string; title: string; remaining_eligible_quota: IntString; remaining_amount: string; currency: string };
  benefits_summary: { claimable_count: number; available_voucher_count: number };
};
type Reward = {
  id: string; campaign_id: string; milestone_id: string; title: string;
  state: 'locked'|'claimable'|'claimed'|'suspended'|'expired';
  condition_text: string; progress_ratio: number;
  benefit: { type: 'voucher'|'seed'|'badge'; amount?: string; currency?: string; description: string }[];
  terms_version: string; validity_text: string; unavailable_reason: string | null;
};
type Voucher = {
  id: string; grant_id: string; payer_id: string; scope: 'personal'|'organization';
  state: 'available'|'exhausted'|'suspended'|'expired';
  currency: string; face_amount: string; remaining_amount: string; reserved_amount: string;
  face_quota: IntString; remaining_quota: IntString; reserved_quota: IntString;
  // remaining 是未消耗额度且包含 reserved；当前可用 = remaining - reserved。
  starts_at: string; expires_at: string;
  applicability: { description: string; model_ids: string[] | null; minimum_charge_quota: IntString | null };
  terms_version: string; unavailable_reason: string | null;
};
```

环境 stage 是整体摘要，子项允许后端独立推进；前端映射固定资源，不接受后端任意 HTML。unknown species/stage 要有中性兜底并记录错误，不误显示满级。state、reward、voucher 多请求可能暂时不同步；领取结果应返回当前状态，前端随后重取相关资源。

关键错误 code 至少区分：`NOT_ELIGIBLE`、`REWARD_SUSPENDED`、`CAMPAIGN_PAUSED`、`BUDGET_EXHAUSTED`、`IDEMPOTENCY_CONFLICT`、`STATE_VERSION_CONFLICT`、`SCOPE_FORBIDDEN`。已领且属于同一主体时返回已有 grant，不生成第二份。

### 4.3 计费内部事件与券扣减

**这是内部协议，不开放给浏览器。** 可在现有后端模块实现，不要求先拆微服务。

| 事件/操作 | 最少要求 |
|---|---|
| `usage.settled` | event_id、schema_version、settlement_id、version、occurred_at、payer_type/id、user_id、organization_id、request_id/task_id、source_log_id、model、quota_delta、funding_allocations、eligible_paid_delta、pricing_snapshot、rule_version |
| `usage.adjusted` / `usage.refunded` | 同上 + original_settlement_id；累计退款不能超过原可退值；有符号分录，不删除原记录 |
| outbox / inbox | outbox 与最终资金变动同事务；消费者以 event_id 唯一处理，分录与投影同事务。乱序暂存/补齐，丢失可重放 |
| reserve | 按实际 payer、模型、币种、券有效期锁额度；并发原子条件更新，不允许超额冻结 |
| commit | 最终价格确定后实际核销，释放多余冻结；不足按原钱包/信用策略处理 |
| release | 失败/取消释放；超时清理前核查是否已结算，避免先释放后扣款 |
| refund | 按原 funding allocation 退回来源；券不能退成现金。到期后退回记账但不自动延长权益 |

funding_allocations 至少识别 `paid_balance / promotional_voucher / other_promotional / subscription / receivable / legacy_unknown`；分摊合计等于最终 charge。eligible_paid_delta 不包含券和其他赠送资金。后付回款/订阅未定口径前保留明确状态，不冒充实付。

若后台只有混合余额，必须补来源批次或等价资金子账。历史余额无法追溯的部分标为 unknown，不假造 paid。不能只靠 used_quota 或 type=2 日志启动自动发奖。

## 5. 活动配置、退款和运营

P0 最小运营接口（**新增建议**）：

- `GET /api/admin/oasis/campaigns`：活动列表。
- `POST /api/admin/oasis/campaigns`：创建草稿；包含受众、有效期、成长阈值、环境/树/区域规则、里程碑、券条款、预算和每主体上限。
- `PATCH /api/admin/oasis/campaigns/{id}`：仅改草稿，带 expected_version；已发布规则变更生成新版本。
- `POST /api/admin/oasis/campaigns/{id}/publish`：验证完整配置/预算，审计发布；未来结算按生效版本，不回写历史。
- `POST /api/admin/oasis/campaigns/{id}/pause`：暂停新增资格与领取，已发券按其条款有效；不停止原模型调用/计费。
- `GET /api/admin/oasis/reconciliation`：按时间/主体查结算、成长、奖励、券账差。

运营权限与普通用户分离；规则编辑、发布、补偿分别授权。活动总预算和每主体限额在并发领取时原子检查，不允许先展示成功再发现无预算。

退款规则：未领取取消资格；已领未用冻结；部分使用只冻结未用余额，已用部分记追偿/抵扣未来奖励的调整项，不能重新发同一 milestone。再次达标恢复旧权益而非复制。具体追偿政策上线前由业务确认。

券跨到期：预留时保存适用快照和 reservation 截止；超时任务重新核验。不能无限冻结券绕过有效期，也不能对已合法提交的冻结默默改价。优惠资金计入账单展示但不能变成新成长本金。

## 6. 前端具体怎么接

### 6.1 现有源码替换表

| 当前定位 | 真实模式接法 |
|---|---|
| `mountFPOasis({root,navigate,toast,getUser})` | 保留挂载、导航、UI；注入 `api` 和 `mode=demo|live`，真实身份来自正式登录 |
| `fresh/reduce/reconcile`、CONFIG/POLICY | 保留在 demo；live 不使用本地规则计算真实进度或奖励 |
| `scope/read/sync` + `fp-oasis-spend-v6` localStorage | live 改为 N1/N3/N5/N7；仅动效偏好可本地保存，付款归属以服务端为准 |
| `scene/growing/projects/render/animate` | 加 `mapOasisState()` 把 N1 转为显示结构，按新旧状态差异播放树、水、动物、建筑和扩建动画 |
| `spendDialog/consume/refund-dialog/redeem` | live 隐藏/禁用；真正消费和退款来自网关/账务，不留可伪造的浏览器金额入口 |
| `claim` | 调 N4，同一次操作持久化同一幂等键直至结果确定；成功后重取 N1/N3/N5 |
| `couponList/rewards` | 显示 N5 剩余额度、冻结、期限、范围；把“单次使用不找零”改为“可分次自动抵扣” |
| `ledger/activity` | N2 + N6；使用真实记录，区分同步中、失败、退款、券抵扣与实付 |
| 当前 `getUser().role` 判断 | 只能控制 UI 展示；领取/组织权限必须由后端再次检查 |

### 6.2 页面请求顺序与异常行为

1. 正式登录完成，确认可访问 scope；并行读取 N1/N3/N5/N7。未登录不读私有账，不用 admin 凭据做代理。
2. 进入页、切回前台、已有任务最终完成、领取成功时刷新。首版可前台每 15 秒轮询 N1（建议值，可调）；离屏停止、失败退避，状态没变化不重复播动画。
3. 切组织时取消旧请求并清空旧主体展示；校验返回 scope 和请求 generation，忽略旧响应，避免串账。异步旧状态不能覆盖新状态。
4. N1 pending/stale 显示“结算同步中”和更新时间，保留最后确认状态；网络失败不回退到枯萎、不生成繁荣默认值。
5. 领取成功显示券及剩额；超时不直接宣称失败或再生成新幂等键，应先查询 rewards/vouchers 或同键重试。
6. 模型调用后的扣款/券使用以服务端记录为准。体验页返回成功不直接调用本地成长 reducer。
7. 新账户 state 可正常为空；没有活动与活动暂停单独显示，不与网络错误混淆。正式模式任何关键配置未确认时，不展示可兑现的券承诺。
8. 保持品牌 UI 和蚀刻淡彩资源；减少动态只影响动画，不改变成长。手机/桌面共享同一账户状态。

### 6.3 部署与登录

正式控制台与 API 建议同站点反向代理/BFF，复用现有登录与刷新；现网封装使用 Bearer + withCredentials，具体 session/CSRF 策略由后端确认。GitHub Pages 保持公开演示，不内嵌 admin 凭据或共享令牌。跨域部署必须明确 origin、Cookie、CSRF 与刷新方案，不能只开通配 CORS。

## 7. 后端接单时先回填这些信息

| 必须返回的交付 | 内容 |
|---|---|
| 服务端基线 | 仓库、branch/commit、运行环境；最终扣费/预扣/异步终结/退款入口所在文件 |
| 接口核对表 | 第 2 节逐项标“可复用 / 字段不足 / 行为不同”；第 4–5 节标“已有等价实现 / 新增” |
| 契约 | OpenAPI 或同等正式文档，成功/错误/权限、分页、金额单位、时间单位、幂等语义 |
| 账本映射 | 原 quota 来源、实付/赠送拆分、payer、组织合同价、退款引用、订阅与应收逻辑 |
| 联调准备 | 测试环境、测试账号权限、脱敏真实样例与回放方式；不要在公开 GitHub 粘贴凭据或账户账单 |
| 上线参数 | 活动规则和券预算由业务确认；无法追溯的历史资金与未支持付款模式明确排除 |

前端可按类型先开发，但生产开关保持关闭，直到以上依赖确认且真实闭环验收完成。

## 8. 必须通过的验收（当前均待后端实施/联调）

| 编号 | 场景 | 通过条件 |
|---|---|---|
| A01 | 新用户/零消费 | 初始枯萎、零奖励；不载入演示繁荣存档 |
| A02 | 小额真实请求 | 原生 quota 累计精确，逐笔小于一分钱也不丢失 |
| A03 | 重复/乱序结算事件 | 只增长一次；乱序可恢复，重放不重新扣款 |
| A04 | 组织专属价、缓存/表达式价、时段边界 | 以实际终值和资金分摊增长，不用目录价估计 |
| A05 | 充值、赠送、券支付 | 不误计为实付成长；混合付款只计合资格实付部分 |
| A06 | 流式/异步失败、预扣调整 | 最终结算才增长，失败释放券预留，无重复奖励 |
| A07 | 树成长、满区、扩建 | 服务端自动推进水、动物、建筑和新区域；未访问页面也继续累计 |
| A08 | 并发领取与超时重试 | 一个主体一个里程碑一个 grant；预算不超支 |
| A09 | 分次抵扣/并发最后额度 | 用多少扣多少、余量保留，券不透支；显示实际剩余 |
| A10 | 部分退款、多次退款、超额退款 | 按原分摊冲回且不超原额；调整资格，不重复发券 |
| A11 | 券跨到期、悬挂冻结、退款后过期 | 按规则释放/核验；不凭空延长期限或退款成现金 |
| A12 | 换组织/离职/伪造 scope | 不串账、不越权、组织券不归个人 |
| A13 | 跨设备、断网、服务重启 | 服务端为准；待同步明确显示，对账可补回漏事件 |
| A14 | 灰度关闭/活动暂停 | 不破坏原模型计费；已发券按条款处理，新增奖励暂停 |

使用测试环境与授权的真实脱敏记录验证，不把演示输入当真实账务验收。金额一致性、重复发放为零是发布要求，不是本次已测结果。

## 9. 证据索引与范围

2026-10-18 只读核对：钱包、兑换码创建字段、消费日志、组织入口、绿电折扣设置及以下公开发布包。兑换码创建只打开弹窗未保存，未充值/兑换/支付/改配置。

- E1：[主包](https://admin.fathompeak.cn/static/js/index.34afbc6bb4.js)：认证请求封装、价格/配置调用、quota 显示转换；[公开状态接口](https://admin.fathompeak.cn/api/status)。
- E2：[日志 API 模块](https://admin.fathompeak.cn/static/js/async/1677.a33d6b6875.js)：动态构造 `/api/log[/self][/stat]` 和任务路径、类型枚举。
- E3：[日志页面](https://admin.fathompeak.cn/static/js/async/1444.739ba3b6fc.js)：筛选、模型/费用/绿电/订阅来源字段。
- E4：[钱包](https://admin.fathompeak.cn/static/js/async/2459.0c8d9e0b31.js)：`POST /api/user/topup {key}`，成功显示增加额度。
- E5：[兑换码管理](https://admin.fathompeak.cn/static/js/async/712.d8bfc6959f.js)：创建码参数与管理调用。
- E6：[组织管理](https://admin.fathompeak.cn/static/js/async/4394.2cf9e76155.js)、[详情](https://admin.fathompeak.cn/static/js/async/7987.c1ecd15c34.js)：组织付款模式、渠道及价格来源。
- E7：[订阅](https://admin.fathompeak.cn/static/js/async/193.8512e7e38f.js)：权益与扣费偏好。

发布包可能更新，以上 URL 是核对时版本。没有服务端源码，所以“需补”指满足本需求所缺的可确认契约；已有内部实现可复用，但要给出证据与映射。本文件不包含凭据、私有账户记录或发布包副本。

## 2026-10-28 奖励规则更新：买 100 送 100

- 每实付消费 ¥100（已结算的模型调用，扣除退款），长成一棵树，送 **100 万词元**。原来的 ¥3 / ¥5 / ¥10 试玩券里程碑作废。
- 第 3 棵树另得月辉种子；每 6 棵颁发绿洲纪念章（视觉奖励，无金额）。
- 100 万词元以「词元包」形式发到账户：调用时优先于余额抵扣，不可提现。
- 待定：词元包适用哪些模型（全部模型按输入输出合计计数，还是指定模型）；有效期；企业账户的词元包归组织还是归个人。
- 官网首页已加活动卡「买 100 送 100 · 大家都来用绿色词元，助力荒漠成绿洲」，按钮指向开始使用和控制台绿洲页。
