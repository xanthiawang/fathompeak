# 沐仞官网与后台 · 色卡、文字与组件设计交接

更新：2026-10-14。设计归属：Zixin Wang。核对基准：运行源码 `34297f8e029ad9fdf3c49d6e13a412ad68ab632f`，已复核最新控制台中英文切换。

## 可分享链接

- [在线色卡与文字规范](https://xanthiawang.github.io/fathompeak-site/design/palette-type.html)：色值、字体样张、后台组件参数、动态背景说明。
- [当前设计交接文档](https://github.com/xanthiawang/fathompeak-site/blob/main/design/DESIGN_HANDOFF.md)：本文件，可在 Git 中编辑。
- [开发交接文档](https://github.com/xanthiawang/fathompeak-site/blob/main/DEVELOPER_HANDOFF.md)：启动、部署、接口接入与源文件位置。
- [官网](https://xanthiawang.github.io/fathompeak-site/) / [后台预览](https://xanthiawang.github.io/fathompeak-site/#console-preview) / [源代码](https://github.com/xanthiawang/fathompeak-site/blob/main/index.html)。
- [历史设计 PDF](https://xanthiawang.github.io/fathompeak-site/design/handoff-deck.pdf) / [历史可编辑 PPT](https://xanthiawang.github.io/fathompeak-site/design/handoff-deck.pptx)：2026-10-13 快照，保留供回溯，未同步最新后台与首页。

## 本次修订解决的差异

旧色卡页标记 2026-10-12，仍写“暮紫只做状态”“深色只出现在首屏与代码块”，与当前后台不符。旧 PDF/PPT 是原型 v36，不含后续排线插画、后台深色表头、icon 配色和动态树影。在线规范现已按当前 CSS 更新；旧文件保留历史版本，不作为最新实现依据。

当前 `#home2` 首页与旧 `.hero .field` 首页不是同一布局；不要照旧 PDF 的首屏绝对坐标复建。CSS 有历史定义及后续覆盖，必须核对作用域、优先级和最终 computed style，不能只复制第一次出现的选择器。

## 控制台内容与设计覆盖

包含概览、模型 API、探索、API Key、使用日志、订单与产地卡、钱包与账单、通用设置、安全与访问，以及组织菜单、通知、账户摘要、动态和独立中英文切换。详细字段与功能清单见 [开发交接第 3A 节](../DEVELOPER_HANDOFF.md#3a-控制台内容范围2026-10-14-最新核对)。

以上页面的前端布局、文案、样式、素材和交互均在 `index.html` 与 `art/` 中，设计文档说明共用视觉体系；不包含单独的可编辑 Figma 文件，也不包含业务后端实现。

右上角语言入口 `.lang.bt-lang` 与通知铃铛并排，复用全站 `setLang()`。本次在线检查已验证中文切至英文后导航、概览和 API Key 引导文案变化。

## 色彩和透明度

| 用途 | 当前值 / 实现位置 |
|---|---|
| 页面基底 | `#F8F8F8`，卡白 `#FFFFFF`；官网墨色 `#000000`，后台 `.bt --ink` 为 `#212021` |
| 品牌强调 | 文字晨蓝 `#2F63B8`；填充晨蓝 `#5284D7` |
| 深色搭配 | 暮紫 `#3D314F`、炭黑 `#212021`；功能紫 `#4E3F66` |
| 浅色辅助 | `#DCE7F7`、`#EEF3FB`、`#EAE4F0`；雾色 `#A9C3E8`、`#E3ECF8`、`#EBCFC4`、`#D6CBDD` |
| 后台表头 | `.bt --band-x`：105° 晨蓝 0% → 暮紫 66% → 炭黑 100%；文字白 94% |
| 后台边线 | `--line` 暮紫 14%；`--line-2` 暮紫 8%；`--frame` 暮紫 22%，卡框 1px |
| 通用筛选条 | 白 86%，blur 12px；`--dia-sh` 为 `0 2px 8px rgba(0,0,0,.06), 0 0 2px rgba(0,0,0,.04)` |
| 普通提示卡 | `.bt-card` 白 60%，悬停白 78%；16px 圆角；细线与轻软阴影 |
| 学习卡 | `.bt-lc` 白 66%，悬停白 94%；图片区为品牌深色低透明度填充 |
| API Key 空状态卡 | `.bt-key-scene .bt-empty`：165° 白 83% → 91%；白 62% 边线，20px 圆角；内高光 + 暮紫软阴影；最终无 backdrop blur |
| API Key 筛选条 | 场景覆盖：白 91%，边框白 58% |
| 功能 icon | 紫 `#4E3F66`；导航当前/悬停蓝 `#2F63B8`；指定 SVG 描边 1.3 |
| 右栏 icon 容器 | 36×36px / 12px 圆角；暮紫 7.5% 背景 + 暮紫 16% 内描边；17px 图标 |
| 动态徽标 | 暮紫 `#3D314F` 底白字；圆点 `#4E3F66`、opacity .8 |

透明填充与文字分开设色，不对整个组件降低 opacity。品牌合作方 logo 保持其原色。当前运行时固定 `setScheme('B')` 与 `data-theme="light"`；后台使用局部深色表头，不是全站深色模式。旧 CSS 中其他 scheme/theme 定义不代表当前发布选择。

## 字体、字号与文字规则

| 用途 | 实现 |
|---|---|
| 标题 | Fraunces；中文 Noto Serif SC；回退 Songti SC / STSong / Georgia；常用 opsz 144 |
| 正文、界面 | DM Sans；中文 Noto Sans SC；回退 PingFang SC / Hiragino Sans GB / system-ui |
| 数字、代码、标签 | DM Mono；全局后备 IBM Plex Mono / Menlo / monospace；首页另补中文回退 |
| 花体首字母 | `HandLatin` → `fonts/hand-pinyonscript-subset.woff2`；1.3em，只修饰拉丁首字母 |
| 首页主标题 | `#home2 .hero h1`：clamp(28px,3.2vw,40px)，400，字距 −.025em |
| 后台一级标题 | `.bt .cs-p h1`：40px / 1.12，400；≤760px 为 30px |
| 后台区块标题 | `.bt-sec h2`：28px / 1.2，400；≤760px 为 24px |
| 空状态标题 | `.bt-empty b`：24px / 1.25，400，字距 −.015em |
| 后台正文 | `.bt`：15px / 1.55，400；说明文字常用墨 70% |
| 后台表头 | `.bt-tbl th`：11px 等宽，400，字距 .08em；白 94% |

拉丁三套主字体已通过 `fonts/fonts.css` 自托管，中文字体通过 Google Fonts 加载，失败时使用系统回退。花体也有本地子集。不是所有字体都完全离线。

英文标题由 `applyLang()` 按名单、首字符、字体和字号选择性添加 `.hand1`；中文标题不使用花体。后台中英文模式中以拉丁字母开头的衬线标题均可能使用花体。首页 `.case b` 和 `.cgh2 b` 的英文首字母明确恢复普通字体；区块大标题仍保留花体。

字号因页面和断点不同而变化，不再将旧 56 / 38 / 28 / 20 梯度作为全站强制规格。中英文文案分别核对正文和 `I18N`，按钮保持动词明确；不要把示例订单、演示请求或本地 Key 当作真实业务结果。型号、报价与事实性文案的维护位置见开发交接文档。

## 插画与动态背景

- 后台排线图集：`art/console/engraved-dark-atlas_2026-10-14.webp`，`.bt-collage` 以 3×2 图集定位。黑白排线主体叠不规则深色色片，边缘透明融入卡片；不新增独立实色方框。
- API Key 树影：`art/backgrounds/api-key-dapple-blue_2026-10-14.png` 为源素材、同名 WebP 用于网页。CSS 在 `.bt-key-light`。
- 树影：blur 7px、10s ease-in-out alternate、−4s 延迟；光层：13s、−5s 延迟。使用 transform 和 opacity；背景裁切留出动画余量。
- 播放条件：场景在视口内、页面可见、未手动暂停且非减少动态效果；依赖 `.bt-key-scene[data-moving="true"]`。静态截图不能验证播放状态。
- 暂停按钮 `.bt-ambient-toggle`；`prefers-reduced-motion: reduce` 关闭背景动画。卡片内容不随背景位移。

Dia 用作背景光影、透明表面与细边线参考；Every 用作排线拼贴插画参考。配色仍为沐仞色卡；不表示逐像素复制参考网站。源图 PNG 可编辑但没有 PSD/Figma 图层。

## 开发核对与版本

修改设计后，检查官网中英文、后台空状态/学习卡/表头/右栏图标、窄屏换行与横向溢出、字体回退、背景播放/暂停及减少动态效果。透明组件需在实际背景上核对文字可读性；固定色值样表不等于全站可访问性验收。

运行源码已含最新控制台语言切换；本轮同步文档并重新导出交付包。[最新交付包](https://github.com/xanthiawang/fathompeak-site/releases/latest) 包含当前控制台与设计文档。`developer-handoff-2026-10-14-b177160` 保留为旧快照，不含之后的语言入口和设计文档更新。main 链接随提交变化，需要冻结版本时使用具体 commit 与包内 manifest。
