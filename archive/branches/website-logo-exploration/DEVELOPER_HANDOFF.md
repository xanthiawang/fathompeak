# 沐仞官网与管理后台前端 · 开发交接

交付日期：2026-10-14。归属：Zixin Wang / 北京沐仞科技有限公司。

本交付是同一个代码库中的 **官网 + 用户管理控制台前端**，可直接编辑和部署为静态网站。**不包含身份认证、支付、密钥签发、模型网关或数据库服务端源码。** 当前控制台为交互预览，不能作为真实鉴权系统部署使用。界面上的本地操作不等于服务端操作成功。

## 1. 在线地址与源码

| 内容 | 地址 |
|---|---|
| 最新官网 | https://xanthiawang.github.io/fathompeak-site/#home |
| 最新后台界面预览 | https://xanthiawang.github.io/fathompeak-site/#console-preview |
| 登录界面 | https://xanthiawang.github.io/fathompeak-site/#login |
| 接入文档 | https://xanthiawang.github.io/fathompeak-site/#docs |
| API 参考文档 | https://xanthiawang.github.io/fathompeak-site/#api |
| 模型目录 | https://xanthiawang.github.io/fathompeak-site/#models |
| 色卡与字体 | https://xanthiawang.github.io/fathompeak-site/design/palette-type.html |
| 当前设计交接（色彩、文字、组件、动效） | https://github.com/xanthiawang/fathompeak-site/blob/main/design/DESIGN_HANDOFF.md |
| 可编辑 Git 仓库 | https://github.com/xanthiawang/fathompeak-site |
| GitHub 在线编辑主文件 | https://github.com/xanthiawang/fathompeak-site/edit/main/index.html |
| 开发交付包 | https://github.com/xanthiawang/fathompeak-site/releases |

`#console-preview` 是直接审阅入口，会改写为 `#console`。新窗口直接打开 `#console` 可能返回登录页；审阅应使用完整的 `#console-preview` 链接。

官网、后台共用 `index.html`，不需要找第二个后台 UI 仓库。正式公司平台的服务端不在此仓库内；本包不推断或承诺其地址、权限及可用性。

## 2. 本地启动（无 npm、无构建步骤）

需要 Python 3.9+，仅使用标准库。

```sh
# 使用 Git 继续开发
 git clone https://github.com/xanthiawang/fathompeak-site.git
 cd fathompeak-site
 python3 tools/serve.py --open home
```

Windows 使用 `python` 或 `py -3` 替代 `python3`。也可以解压交付 ZIP，进入含有 `index.html` 的目录执行同一条启动命令。

- 官网：http://127.0.0.1:8846/#home
- 后台预览：http://127.0.0.1:8846/#console-preview
- API 文档：http://127.0.0.1:8846/#api
- 单独打开后台：`python3 tools/serve.py --port 8847 --open console`
- 结束服务：Ctrl+C。端口被占用时换用 `--port 8847`。
- 请通过 HTTP 服务查看，避免直接双击 `index.html` 造成路径、缓存或浏览器能力差异。

ZIP 为源码快照，不含 `.git` 历史。需要提交、分支、回滚时使用 Git clone；写入原仓库需由仓库所有者添加协作者权限。公开可读取不等于有写权限。

## 3. 编辑位置

| 修改内容 | 文件 / 可搜索定位点 |
|---|---|
| 页面结构、样式、交互 | `index.html`（原生 HTML/CSS/JavaScript，未压缩的可编辑源码） |
| 官网正文 | `<section data-route="home">`、`models`、`enterprise`、`network`、`about` |
| 控制台结构 | `<section data-route="console">`；内部 `.cs-p[data-p]` 为分页 |
| 控制台样式 | `.bt`、`.bt-*`；`--frame`、`--icon`、`--band-x` 为近期品牌调整 |
| 登录与账户流程 | `authUnavailable`、`syncLogin`、`persist`、`btPreview` |
| 控制台交互 | `csTab`、`renderConsole`、`renderKeys`、`LOGS`；表单 `nf` |
| 模型、新闻、指南 | `var M`、`NEWS`、`G`；请对照真实平台资料更新 |
| 中英文 | `I18N`、`setLang`、`syncAuthLocale`；API 文档还有 `apData` 内译文 |
| API 参考文档 | `#apData` 中内嵌 JSON、`apRender`；生成脚本在 `tools/api_ref/` |
| 咨询表单 | `LEAD_TO`、`LEAD_URL`、`sendLead` |
| Logo 与插画 | `art/`；当前文件引用以 `index.html` 为准，旧版本素材保留供追溯 |
| 当前控制台插画 | `art/console/engraved-dark-atlas_2026-10-14.png` / `.webp` |
| API Key 树影背景 | `art/backgrounds/api-key-dapple-blue_2026-10-14.png` / `.webp` |
| 背景动画 | `bt-leaf-sway`、`bt-light-shift`、`<script id="fp-key-ambient">` |
| 字体 | `fonts/fonts.css`、`fonts/*.woff2`；中文另有 Google Fonts 请求 |
| 本地预览工具 | `tools/serve.py` |
| 重打开发包 | `tools/package_handoff.py --output <交付目录>`（需 Git） |

PNG 为可继续修改的图像源稿，WebP 为网页加载素材；不是分层 PSD 或 Figma 文件。`design/handoff-deck.*` 和部分 `qa/` 是早期设计记录，当前视觉以本次源码运行结果为准。历史设计/生成脚本中有原作者本机路径，运行前需配置；启动网站不依赖它们。

## 3A. 控制台内容范围（2026-10-14 最新核对）

已按运行源码 `34297f8e029ad9fdf3c49d6e13a412ad68ab632f` 与线上控制台核对。下表是已包含的前端页面与内容，不表示对应业务服务已上线。

| 页面 / 定位 | 已包含的内容 |
|---|---|
| 概览 / `home` | API Key 引导与筛选、三步开始使用、模型 API 表、订单与产地卡、公告/常见问答空状态、学习入口 |
| 模型 API / `models`、探索 / `explore` | 模型目录、搜索/分类、固定模型、文档与模型详情入口 |
| API Key / `keys` | 列表筛选、创建表单、批量数量、额度/过期时间/可用模型/IP 白名单、客户端导入说明；操作为本地预览 |
| 使用日志 / `usage` | 消费趋势空状态、按模型汇总、请求明细、时间筛选、Token/费用/节点/绿电折扣字段 |
| 订单与产地卡 / `orders` | 进行中/已完成页签与空状态；电站、时段、电量、词元数、单价、减排字段说明 |
| 钱包与账单 / `bill` | 余额、充值金额和支付方式 UI、兑换码、充值记录、账单、推荐计划；支付待接入 |
| 通用设置 / `acct` | 个人资料、账户类型、教育认证入口、成员与角色、邮箱/Webhook 通知与余额预警 |
| 安全与访问 / `sec` | 修改密码、TOTP、Passkey、第三方账号绑定、访问令牌、登录记录和审计日志的界面；真实安全服务待接入 |
| 公共区域 | 组织菜单、可收起侧栏、余额弹层、通知铃铛、账户摘要与动态、右上角中英文切换 |

设计覆盖这些页面共用的 `.bt` 组件体系：深色表头、细边线、半透明卡片、紫/蓝 icon、字号、排线插画、API Key 树影动效及移动端适配。具体参数见 [设计交接](design/DESIGN_HANDOFF.md) 和 [在线色卡](https://xanthiawang.github.io/fathompeak-site/design/palette-type.html)。

最新新增项为通知铃铛旁的 `.lang.bt-lang` 中英文切换，复用 `setLang()`；官网导航在控制台内隐藏，因此必须保留此独立入口。

## 4. 服务端接入清单

以下是现有前端的接入位置及待完成工作，不是已实现的 API 协议。

| 模块 | 当前源码行为 | 开发接入工作 |
|---|---|---|
| 登录 / 验证码 / OAuth | 校验输入后提示服务尚未开通 | 接入真实登录、验证码、会话、退出和权限；替换 `authUnavailable` |
| API Key 管理 | 预览可在内存创建本地字符串，筛选/停用/删除和批量操作仅影响前端状态 | 用服务端签发、列举、撤销接口替换 `genKey` / 本地数组；真实完整 Key 仅在签发时显示 |
| 用量与账单 | `LOGS` 和表格当前无真实请求记录 | 接入真实用量、费用、分页、筛选和汇总，不以占位数字验收 |
| 钱包 / 充值 | 充值按钮提示待接入 | 接入服务端订单、支付、回调、余额与幂等处理 |
| 订单 / 产地卡 | 页面与空状态 | 接入订单、电站、时段、电量、来源与可追溯记录 |
| 个人资料 / 通知 / 安全 | 前端设置和展示状态 | 接入保存、读取、验证、通知、登录与审计记录 |
| 模型调用 | 文档/请求模板；`YOUR_API_HOST` 仍是待替换地址 | 确认正式网关与协议；验证真实鉴权、流式输出、错误返回和计费 |
| 商务表单 | 当前 `sendLead` 会 POST 到 FormSubmit 的公开商务邮箱转发服务 | 确认是否保留或替换为公司线索接口；本交付未提交表单、未验证邮件送达 |

文档内已有 API 描述不代表本仓库运行了这些服务。不要把预览产生的 Key 当作可调用凭证；不要将真实密钥写进 HTML 或提交进仓库。预览入口必须与生产身份/权限边界区分。

## 5. 运行依赖和部署

静态运行文件：`index.html`、`art/`、`fonts/`、`vendor/`、`.nojekyll`。保留相对路径。要展示设计页，另外保留 `design/`。

- GitHub Pages：当前 `main` 分支根目录；推送后等待 Pages 构建成功。
- Nginx / 静态托管：将运行文件放到同一网站根目录，默认文档为 `index.html`。页面使用 hash 路由，不需要服务端逐页路由。
- 不要把 `python http.server` 当作生产 API 服务；本地脚本仅用于开发预览。
- Google Fonts、第三方素材/新闻链接、FormSubmit 等外部地址依网络环境而定；中文字体不可达时使用系统回退字体。
- `fp-fresh` 脚本会检查 HTML 缓存并可能刷新页面；本地服务器发送 `no-store`。调试刷新行为时可定位该脚本。
- 原仓库尚无覆盖全部业务的自动化测试套件；交付校验不等于服务端验收。

## 6. 版本和交付校验

ZIP 内的 `DELIVERY_MANIFEST.json` 记录导出时的完整 Git commit、导出时间、逐文件 SHA-256 与大小。`LINKS.json` 记录线上入口与对应 commit 页面。URL 的版本查询参数只用于刷新缓存，不会冻结 GitHub Pages 内容；代码快照以完整 commit 和 ZIP 为准。

开发验收至少检查：官网中英文、模型目录、API 文档、后台预览、移动端溢出、字体/图片路径；树影播放/暂停/离屏暂停/减少动态效果；真实业务接口接通后另做身份、权限、请求、账单等端到端验证。
