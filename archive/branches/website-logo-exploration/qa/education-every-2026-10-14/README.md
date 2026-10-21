# 教育价背景调整 · 2026-10-14

- 用户要求：参考 https://every.to/agent?utm_cta_source=everywebsite#home 重做教育价卡片背景。
- 起点：已发布 origin/main，3ddb3aa；修改前检查点 1825f80。
- 参考已在 Chrome 实际查看：首页浅纸色与细网格、价格区平面色块与深浅分栏、纸张标签。
- 范围：仅 index.html 中 .ed-offer 相关 CSS。保留文字、字体家族、链接、表单和其他页面。
- 设计：晨蓝浅色 #DCE7F7、强调蓝 #5284D7 / #2F63B8、近黑 #212021、紫灰文字 #3D314F；76px 细网格，8px 圆角，纸张标签，独立深色权益区。
- 检查：桌面中文与英文、390px 手机版无横向溢出；已查看截图，文字无遮挡。git diff --check 通过。
- 预览：http://127.0.0.1:4207/#edu 。当前为本地修改，未推送发布。
- 截图：desktop.png、desktop-en.png、mobile.png，均为实际浏览器捕获。
