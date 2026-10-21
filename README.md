# 沐仞科技 · FathomPeak

公司唯一现用 GitHub 仓库。

统一在线入口：**[项目与素材](https://xanthiawang.github.io/fathompeak/)**。

官网、视觉素材、开发交付与历史方案的实际文件都放在这里，便于统一查找和下载。

## 现用项目

| 项目 | 文件夹 | 现有在线入口 |
| --- | --- | --- |
| 官网源码与原型 | [projects/website](projects/website/) | [官网原型](https://xanthiawang.github.io/fathompeak/site/) |
| 品牌、Logo、字体、插画与公众号素材 | [projects/visual-materials](projects/visual-materials/) | [视觉素材站](https://xanthiawang.github.io/fathompeak/materials/) |
| 开发交付文档与页面 | [projects/developer-handoff](projects/developer-handoff/) | [开发交付站](https://xanthiawang.github.io/fathompeak/handoff/) |

公司官网：[www.fathompeak.cn](https://www.fathompeak.cn/)

## 常用素材

- [现用 Logo 与字标](projects/visual-materials/05_品牌标识/现用/官方logo_2026-10-18/)
- [公众号视觉素材](projects/visual-materials/09_公众号视觉/)
- [公司介绍图文](https://xanthiawang.github.io/fathompeak/materials/09_公众号视觉/2026-10-20/article-compute-energy/)
- [招聘图文与配图](https://xanthiawang.github.io/fathompeak/materials/recruitment/)
- [央视报道图文与配图](https://xanthiawang.github.io/fathompeak/materials/cctv/)

## 历史归档

以下目录只保留历史方案，不代表现行品牌或官网版本。

| 内容 | 文件夹 |
| --- | --- |
| 最早的品牌与产品整站初稿 | [archive/early-website](archive/early-website/) |
| 能源青与暖金版 | [archive/energy-draft](archive/energy-draft/) |
| 松绿油画版 | [archive/pine-draft](archive/pine-draft/) |
| 紫与青版 | [archive/purple-draft](archive/purple-draft/) |
| 官网历史 Logo 探索分支 | [archive/branches/website-logo-exploration](archive/branches/website-logo-exploration/) |
| 已发布的开发交付压缩包 | [archive/releases](archive/releases/) |

## 目录结构

```text
fathompeak/
├── projects/
│   ├── website/
│   ├── visual-materials/
│   └── developer-handoff/
├── archive/
│   ├── early-website/
│   ├── energy-draft/
│   ├── pine-draft/
│   ├── purple-draft/
│   ├── branches/website-logo-exploration/
│   └── releases/
├── metadata/            # 来源仓库、分支、提交与文件清单
└── tools/               # 导入和核对工具
```

## 来源与更新方式

本次整理日期：**2026-10-21**。只导入原本已公开的 GitHub 内容。各目录保留来源版本的文件内容、文件名、可执行权限、许可证和署名。

用户已确认移除七个旧仓库，仅保留本仓库。七个旧仓库已于 2026-10-21 在统一入口部署验证后删除；旧仓库网址与原 GitHub Pages 地址已停用。删除前已在本地完成七个仓库的全部分支、标签、Git bundle 和 Release 附件备份。

后续维护从本仓库开始。`projects/` 保留导入时的公开源文件；部署脚本只在构建输出中改写旧链接，原始来源文件哈希仍可核对。

迁移完成记录见 [旧仓库移除记录](metadata/repository-retirement.json)。来源清单中的旧仓库 URL 仅表示导入时的来源，不再作为现用链接。

逐项来源与版本见 [来源清单](metadata/source-repositories.json)，逐文件版本见 [文件清单](metadata/source-files.json)，核对结果见 [整理验收](metadata/verification.json)。

GitHub Pages 统一发布三个现用项目及必要的历史交付下载；历史设计目录不混入现用入口。发布流程见 `.github/workflows/pages.yml`。部署时的链接映射记录在站点的 `migration-links.json`。

预览单个源项目时，以其文件夹作为服务器根目录，例如：

```bash
python3 -m http.server 8000 --directory projects/website
```

可在克隆后核对快照完整性：

```bash
python3 tools/consolidate_20261021.py --verify
```

各项目的使用许可仍以项目目录内原有许可文件为准；统一整理不新增对第三方素材的授权。
