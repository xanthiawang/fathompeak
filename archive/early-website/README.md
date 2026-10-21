# 废弃初稿

沐仞最早的品牌与产品整站原型（2026-10-12），保留供设计讨论与编辑。

- **打开网页**：https://xanthiawang.github.io/fathompeak-discarded-draft/
- **浏览器编辑源码**：https://github.dev/xanthiawang/fathompeak-discarded-draft
- **当前正式官网**：https://xanthiawang.github.io/fathompeak-site/

## 编辑与发布

这是 React + Vite 的可编辑项目，不只是网页截图。

- 页面、导航与交互：`src/App.jsx`
- 样式与字体：`src/styles.css`
- 品牌故事：`src/brand-story.json`
- 历史目录展示记录及来源：`src/catalog.json`
- 图片、字体与许可：`public/`
- 浏览器标题：`index.html`

登录 GitHub 后可按 `.` 打开网页编辑器，或点击上面的浏览器编辑链接。有仓库写入权限的协作者可以提交修改；其他人可以 Fork 后通过 Pull Request 提交。公开仓库不会自动授予所有人写入权限。

合并到 `main` 后，GitHub Actions 自动构建并更新网页。网页采用原项目的自包含构建方式，避免 GitHub Pages 子目录导致字体、图片和下载链接失效。

```sh
npm ci
npm run dev
npm run build:pages
npm run test:sites
```

`pages/index.html` 为发布产物，请编辑源码，不要手动修改产物。

## 归档说明

此版本名为「废弃初稿」，不代表当前官网、服务能力或最新价格。历史内容保留；认证、支付和真实订单未接入。品牌素材及字体许可证保留在 `public/licenses/`，本仓库未额外授予品牌素材使用许可。

2026-10-14：按用户要求从原项目复制运行所需源码和资源，建立独立仓库。原项目和已选定的新官网不受影响。本地归档位置：`品牌与视觉重启_2026-10-12/废弃初稿_2026-10-14/`；来源：同级 `fathompeak-design-system/`。

## 恢复的历史完整网站（2026-10-14）

从 2026-10-12 至 2026-10-13 的文件历史恢复，不是重新设计的配色方案板。`public/history/provenance.json` 记录原文件摘要，各目录 `original.html` 保留逐字相同的原始快照。发布入口仅补充 UTF-8 编码声明、按截图默认打开原有浅色模式，并增加 `?scheme=` 参数选择原有配色。

- 能源青与暖金（渐变首屏阶段最后留存版本）：[打开](https://xanthiawang.github.io/fathompeak-discarded-draft/history/v5/?scheme=A#home)
- 紫＋青（渐变首屏阶段最后留存版本）：[打开](https://xanthiawang.github.io/fathompeak-discarded-draft/history/v5/?scheme=B#home)
- 松绿油画（截图中的原版）：[打开](https://xanthiawang.github.io/fathompeak-discarded-draft/history/v6/?scheme=A#home)
- 松绿油画后续完整版（保留「谷时发电，峰时平价」首屏阶段的最后留存版本）：[打开](https://xanthiawang.github.io/fathompeak-discarded-draft/history/v17/?scheme=C#home)
- 晨昏蓝（三配色切换阶段最后留存版本）：[打开](https://xanthiawang.github.io/fathompeak-discarded-draft/history/v23/?scheme=B#home)

v17 与 v23 均保留 A 能源青、B 晨昏蓝、C 松绿油画，可通过页脚切换。目录下保留历史文案与演示行为，未对其中的业务状态及演示数字作新的验证。
