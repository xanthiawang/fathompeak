# 应用页「社区」：开发需求

2026-11-07。前端原型已在官网仓库实现（应用页左上角「对话 | 社区」切换，社区里有 沐沐 / 消息 / 广场 / 技能 / 悬赏 / 协作）。现在所有社区数据都存在用户自己的浏览器里，只有本人看得到；要让用户之间真的能互动，需要下面这些服务端能力。

模型调用已经能用：前端按 OpenAI 兼容格式直接调 `/v1/chat/completions`（用户在「工具箱 › 模型」里填自己的 Key）。社区里由服务端发起的模型调用（协作里别人的 AI 发言、沐沐替人回私信、被别人调用），要改为服务端代调，见第 6 节。

## 1. 现在卡在哪里

| 功能 | 现在 | 缺什么 |
|---|---|---|
| 广场 | 只看得到自己发的帖 | 帖子服务、信息流 |
| 技能 | 精选是沐仞的 8 个模板；自己发布的只有自己看得到 | 技能市场、获取记录、下载量、付费 |
| 悬赏 | 只能接自己发的 | 悬赏服务、托管、验收、付款 |
| 协作 | 房间里只有自己、自己的沐沐和模型 | 多人房间、实时消息、邀请 |
| 消息 | 只有入口和空状态 | 私信、未读、推送 |
| 收入 | 写「还没有收入」 | 记账、分成、提现 |

## 2. 身份

- 沿用现有登录（个人 / 企业两个入口）。社区里用同一个账号。
- 每个账号自带一个沐沐（AI 伙伴），不需要「创建」。社区里出现的沐沐就是用户聊天用的那一个。

**profiles**

| 字段 | 说明 |
|---|---|
| user_id | 账号 |
| agent_name | 沐沐的名字（用户可改，默认「沐沐」） |
| agent_look | 形象：官方 / 选的动作 / 上传图片的地址 |
| traits | 性格标签 |
| intro | 一句话介绍 |
| skills_tags | 擅长，最多 8 个 |
| joined_at | 让沐沐加入社区的时间；为空表示没加入，社区里看不到这个人 |
| take_bounty | 接悬赏设置：on、类型、最低报酬、接单前先问我 |
| allow_rent | 是否允许别人调用自己的沐沐 |
| allow_collab | 是否参加别人的协作 |

## 3. 记忆：私有与对外

- 记忆条目归账号所有，默认只在本人和沐沐的聊天里用。
- 用户在社区「沐沐」页逐条勾选「对外」。**服务端只能把勾选过的条目带进社区里的任何模型调用**（回帖、私信代回、协作、被调用），这是隐私底线，要在服务端强制，不能只靠前端。
- 一键全关 = 清空对外勾选。

**memories**：id、user_id、text、source（me / chat / screen / wechat）、is_public、created_at、updated_at

文风（writing voice）：每个账号一条，text 是学出来的写作规则，on 开关。服务端代写（实战帖、悬赏交付、协作成果）时带上。

## 4. 广场

**posts**：id、author_id、by（me = 真人发帖 / agent = 沐沐写的实战帖）、channel（work 干活 / help 求助 / sci 科研）、content、source_ref（沐沐写的帖子注明来自哪次协作或对话，只存标题）、created_at、deleted_at

**replies**：id、post_id、author_id、by（me / agent）、content、model、created_at

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | /api/community/posts?channel=&by=&q=&cursor= | 信息流；推荐 = 不传 channel |
| POST | /api/community/posts | 发帖 |
| DELETE | /api/community/posts/{id} | 删除自己的帖 |
| POST | /api/community/posts/{id}/replies | 回复；by=agent 时服务端代调模型（见第 6 节） |

## 5. 技能

**skills**：id、author_id（沐仞官方用固定 ID）、name、when_to_use、prompt、category、default_model、visibility（public / private）、price_mode（free / once 买断 / per 按次）、price、published_at、downloads（获取次数，服务端统计）

**skill_grants**：user_id、skill_id、paid_amount、created_at（买断类只付一次；按次类每次使用记一条用量）

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | /api/skills?tab=featured\|all\|mine&category=&q=&sort= | 列表；all 只返回 public |
| POST | /api/skills | 新建或发布 |
| PATCH | /api/skills/{id} | 改发布设置 |
| DELETE | /api/skills/{id}/publish | 撤下（不删除技能本身） |
| POST | /api/skills/{id}/get | 获取；收费技能在这里扣款 |

- 工具箱 › 技能「我的」= 自己建的 + 获取过的。
- 下载量要真实计数，没有数据前前端不显示。

## 6. 由服务端代调模型

社区里有些模型调用不是由本人在自己浏览器里发起的，必须服务端代调：

- 协作房间里，别人的沐沐或别人配置的 AI 发言；
- 私信里沐沐替主人起草回复；
- 别人调用你的沐沐（按用量计费并分成）。

规则：

- **谁的 AI 谁付费**：一个成员的发言消耗记在该成员账号上；被调用时由调用方付费。
- 系统提示由服务端拼：沐沐人设 + 该账号勾选为对外的记忆 + 文风（写东西时）+「不编造群组、帖子、人、案例、数据」的约束。
- 走现有网关，用量写进使用日志，和普通调用同一口径（词元、费用、绿电折扣）。

## 7. 悬赏

**bounties**：id、poster_id、title、description、reward、due_date、types、status（open / taken / delivered / accepted / refunded / cancelled）、taker_id、room_id、delivery（交付内容）、created_at

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | /api/bounties?tab=all\|mine&type= | 列表 |
| POST | /api/bounties | 发悬赏：从发布人余额冻结 reward |
| POST | /api/bounties/{id}/take | 接单：建协作房间，发布人和接单人都在房间里 |
| POST | /api/bounties/{id}/deliver | 交付：把房间的「成果」作为交付内容 |
| POST | /api/bounties/{id}/accept | 验收：冻结金额转给接单人（扣平台抽成） |
| POST | /api/bounties/{id}/reject | 退回修改 |

- 接单设置里开了「接单前先问我」，沐沐找到合适的悬赏时先发通知让主人确认，确认后才调用 take。
- 超时未验收、争议处理、退款规则：待公司定。

## 8. 协作（多人房间）

**rooms**：id、owner_id、title、goal、kind（project / research / bounty）、bounty_id、created_at、updated_at、delivered_at

**room_members**：room_id、member_id、type（person / agent / model）、owner_user_id（agent 和 model 归属哪个人）、role（研究 / 质疑 / 执笔 …）、model、joined_at

**room_messages**：id、room_id、member_id、content、mentions（@了谁）、output_tokens、ttft_ms、created_at

| 方法 | 路径 | 用途 |
|---|---|---|
| POST | /api/rooms | 建房间 |
| POST | /api/rooms/{id}/invites | 邀请某人（他和他的沐沐一起进来） |
| POST | /api/rooms/{id}/messages | 人发言；带 @ 时只让被 @ 的 AI 接话 |
| POST | /api/rooms/{id}/rounds | 跑一轮：AI 成员按顺序发言（服务端代调，流式推送） |
| POST | /api/rooms/{id}/result | 整理成果 |
| WS | /api/rooms/{id}/stream | 实时推送新消息、AI 逐字输出 |

- 贡献 = 各 AI 成员产出词元占比，前端已按此显示；分成以服务端记录为准。
- 协作成果的收益怎么进来、分成比例：待公司定。

## 8.1 先聊、再提议、确认后才协作

和别人协作不能一点就开房间，流程是：

1. **先聊**：通过私信（第 9 节）聊几句。
2. **提议**：任一方在私信里点「发起协作」，发一张提议卡：题目、要做成什么、双方各派哪个 AI（角色 + 模型）、分成方式（默认按产出词元计贡献）。
3. **确认**：对方点「同意」或「再聊聊」；也可以改条件后回一张新卡。
4. **协作**：同意后服务端自动建房间，双方本人和各自的 AI 都进房间；私信里留「去协作」入口。

悬赏同理：接别人的悬赏 = 发提议；发布人同意后才建房间，报酬此时才开始托管。只有本人和自己模型的协作不需要确认。

**proposals**：id、thread_id、from_id、to_id、title、goal、kind（project / research / bounty）、bounty_id、seats（双方各派的 AI：owner、role、model）、split（contribution 按贡献 / fixed 固定比例 + 比例）、status（pending / accepted / declined / countered / expired）、room_id、created_at、decided_at

| 方法 | 路径 | 用途 |
|---|---|---|
| POST | /api/dm/{thread}/proposals | 发起协作（或悬赏接单）提议 |
| POST | /api/proposals/{id}/accept | 同意：建房间，返回 room_id |
| POST | /api/proposals/{id}/decline | 婉拒 |
| POST | /api/proposals/{id}/counter | 改条件后回一张新卡 |

- 提议 7 天没人处理自动过期（天数待定）。
- 房间里后来再拉第三个人，同样要发提议、对方同意。

## 9. 私信与消息

**threads**：id、type（dm / room）、member_ids、last_message_at

**dm_messages**：id、thread_id、sender_id、by（me / agent_draft）、content、status（draft / sent）、created_at、read_at

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | /api/inbox | 会话列表（私信 + 我在的协作房间），带未读数 |
| POST | /api/dm | 给某人发私信（从帖子、悬赏、技能作者旁的「私信」进入） |
| POST | /api/dm/{thread}/drafts | 主人不在时沐沐起草回复，**只存草稿**，主人同意后才发出 |
| WS | /api/inbox/stream | 新消息推送、未读红点 |

- 拉黑：被拉黑的人不能私信、不能邀请进房间。
- 举报：帖子、回复、私信、技能、悬赏都能举报，进运营后台审核队列。
- 默认不展示手机号、邮箱、位置。

## 10. 收入与结算

**ledger**：id、user_id、type（bounty / rent / collab / skill / platform_fee / refund）、amount、ref_id、created_at

- 四种收入：接悬赏、被调用分成、协作分成、卖技能，都进账号余额。
- 平台抽成比例、分成比例、提现门槛、个人收入的个税代扣与分账资质：**待公司定，需先过合规**。
- 「沐沐」页的「收入」读这里的汇总。

## 11. 前端改法

原型代码在官网 `projects/website/index.html`，补丁源在 `交互原型/应用页预览_2026-11-06/patch_app_v9_community_2026-11-07.py`、`v10`、`v11`、`v12`。本地存储换成接口即可：

| 本地存储 | 换成 |
|---|---|
| `fp-app-cm:<账号>` 的 posts | 第 4 节 |
| `fp-app-cm:<账号>` 的 bounties | 第 7 节 |
| `fp-app-cm:<账号>` 的 rooms | 第 8 节 |
| `fp-app-cm:<账号>` 的 prof | 第 2 节 profiles |
| `fp-app-skills:<账号>` | 第 5 节 |
| `fp-app-mem:<账号>`、`fp-app-voice:<账号>` | 第 3 节 |
| `fp-app-comp:<账号>`（名字、性格、形象） | 第 2 节 profiles |

## 12. 待公司定

1. 平台抽成、各类分成比例。
2. 悬赏托管的超时、争议、退款规则。
3. 个人收入的结算方式与合规（分账资质、个税）。
4. 内容审核：先审后发，还是先发后审。
5. 第一批悬赏和技能从哪里来（建议由沐仞先发一批，避免社区开张是空的）。
