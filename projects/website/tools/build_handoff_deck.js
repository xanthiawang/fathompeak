// 沐仞官网设计交付文档（pptxgenjs）。2026-10-13 v2：色卡页补齐内页色雾 4 色 + 暖纸 / 卡白（规范页十五色四组齐全），
// 按钮页补代码块色，规则加墨 50% 的限制。运行：cd 品牌竞品调研_2026-10-12/交付 && NODE_PATH=/opt/homebrew/lib/node_modules node ../data/build_handoff_deck_2026-10-13.js
// 截图素材在 交付/crops/（由上一会话的 shoot_handoff 流程从原型 v26 截取）；PDF 用 Keynote 导出（osascript export … as PDF）。
// 2026-10-13 v3（晚）：截图改从 GitHub 仓库 site/index.html 拍（另一会话已在仓库内改文案，仓库为唯一源）；链接改为仓库与 Pages。
// 2026-10-13 v3：按原型 v36 更新（产品与服务页、页脚五栏 + 周报整行、导航透明度、问答折叠、新闻只放可查证报道、线上地址、字体自托管），
// 删去「开发：待定」等空话；截图改由 data/shoot_handoff_crops_2026-10-13.py 生成到 交付/crops_v3/，每张按放置比例裁切（v2 的色雾与首页分段图被拉伸）。
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; pres.author = "Zixin Wang"; pres.title = "沐仞官网 设计交付文档";
const C = { paper:"F8F8F8", card:"FFFFFF", ink:"000000", ink70:"4A4A4A", ink50:"6B6B6B", line:"E2E2E2", accent:"2F63B8", char:"212021" };
const SERIF="Georgia", SANS="PingFang SC", MONO="Menlo";
const TOTAL=10; let n=0;
const ASP=JSON.parse(require("fs").readFileSync("crops_v3/aspects.json","utf8")); const FA=ASP["footer_only.jpg"]; const FW=Math.min(9.0,2.75*FA);
function base(title){ n++; const s=pres.addSlide(); s.background={color:C.paper};
  s.addText("沐仞科技 · 官网设计交付 · 2026-10-13",{x:0.5,y:0.2,w:6,h:0.25,fontFace:MONO,fontSize:9,color:C.ink50,margin:0});
  s.addText(String(n).padStart(2,"0")+" / "+TOTAL,{x:8.5,y:0.2,w:1,h:0.25,fontFace:MONO,fontSize:9,color:C.ink50,align:"right",margin:0});
  if(title) s.addText(title,{x:0.5,y:0.48,w:9,h:0.55,fontFace:SERIF,fontSize:26,color:C.ink,margin:0});
  return s; }
function h(s,t,x,y,w){ s.addText(t,{x,y,w,h:0.3,fontFace:SANS,fontSize:11,bold:true,color:C.ink,margin:0}); }
function p(s,lines,x,y,w,hh,size=10.5,color=C.ink70){ s.addText(lines.map((t,i)=>({text:t,options:{breakLine:i<lines.length-1}})),{x,y,w,h:hh,fontFace:SANS,fontSize:size,color,valign:"top",margin:0,paraSpaceAfter:4}); }
function bullets(s,items,x,y,w,hh,size=10.5){ s.addText(items.map((t,i)=>({text:t,options:{bullet:{indent:11},breakLine:i<items.length-1}})),{x,y,w,h:hh,fontFace:SANS,fontSize:size,color:C.ink70,valign:"top",margin:0,paraSpaceAfter:4}); }
function mono(s,t,x,y,w,hh,size=9,color=C.ink50){ s.addText(t,{x,y,w,h:hh,fontFace:MONO,fontSize:size,color,valign:"top",margin:0}); }
function frame(s,path,x,y,w,hh){ s.addShape(pres.shapes.RECTANGLE,{x:x-0.03,y:y-0.03,w:w+0.06,h:hh+0.06,fill:{color:C.card},line:{color:C.line,width:0.75},shadow:{type:"outer",color:"000000",blur:6,offset:2,angle:135,opacity:0.10}}); s.addImage({path,x,y,w,h:hh}); }
function swatch(s,x,y,hex,name,sub,border){ s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:1.05,h:0.5,fill:{color:hex},line:{color:border?"CFCFCF":hex,width:0.75},rectRadius:0.06}); s.addText(name,{x,y:y+0.53,w:1.1,h:0.2,fontFace:SANS,fontSize:8.5,color:C.ink,margin:0}); s.addText(sub,{x,y:y+0.72,w:1.1,h:0.18,fontFace:MONO,fontSize:8,color:C.ink50,margin:0}); }

// 01 封面
{ n++; const s=pres.addSlide(); s.background={color:C.char};
  s.addImage({path:"crops_v3/cover_sq.jpg",x:0,y:0,w:5.7,h:5.625});
  s.addShape(pres.shapes.RECTANGLE,{x:5.68,y:0,w:4.32,h:5.625,fill:{color:C.char},line:{color:C.char,width:0}});
  s.addText("设计交付文档",{x:6.1,y:1.5,w:3.6,h:0.7,fontFace:SERIF,fontSize:30,color:"FFFFFF",margin:0});
  s.addText("沐仞官网 · 定稿方案「晨昏蓝」",{x:6.1,y:2.25,w:3.6,h:0.4,fontFace:SANS,fontSize:13,color:"E6E6E6",margin:0});
  s.addText([{text:"设计：Zixin Wang",options:{breakLine:true}},{text:"日期：2026-10-13（v3）",options:{breakLine:true}},{text:"状态：原型 v36，已上线",options:{breakLine:true}},{text:"xanthiawang.github.io/fathompeak-site",options:{color:"FFFFFF"}}],{x:6.1,y:3.1,w:3.6,h:1.3,fontFace:MONO,fontSize:10,color:"D0D0D0",margin:0,paraSpaceAfter:5});
  s.addText("01 / "+TOTAL,{x:8.5,y:5.1,w:1.1,h:0.25,fontFace:MONO,fontSize:9,color:"A0A0A0",align:"right",margin:0});
}
// 02 目录与工具
{ const s=base("目录与工具");
  h(s,"目录",0.5,1.3,4);
  const toc=[["03","情绪板与色卡"],["04","字体"],["05","按钮与胶囊"],["06","导航（桌面与手机）"],["07","页脚"],["08","首页设计"],["09","其他页面与用户流程"],["10","资产与备注"]];
  toc.forEach((r,i)=>{ const y=1.7+i*0.42; s.addText(r[0],{x:0.5,y,w:0.5,h:0.3,fontFace:MONO,fontSize:12,color:C.ink50,margin:0,valign:"middle"}); s.addText(r[1],{x:1.0,y,w:3.6,h:0.3,fontFace:SANS,fontSize:13,color:C.ink,margin:0,valign:"middle"}); });
  h(s,"工具与链接",5.2,1.3,4.3);
  s.addText([
    {text:"线上网站（GitHub Pages，可直接分享）",options:{breakLine:true}},
    {text:"https://xanthiawang.github.io/fathompeak-site/",options:{hyperlink:{url:"https://xanthiawang.github.io/fathompeak-site/"},color:C.accent,fontFace:MONO,fontSize:9.5,breakLine:true}},
    {text:" ",options:{breakLine:true}},
    {text:"GitHub 仓库（源文件，可编辑；推送约 1 分钟后自动上线）",options:{breakLine:true}},
    {text:"https://github.com/xanthiawang/fathompeak-site",options:{hyperlink:{url:"https://github.com/xanthiawang/fathompeak-site"},color:C.accent,fontFace:MONO,fontSize:9.5,breakLine:true}},
    {text:" ",options:{breakLine:true}},
    {text:"色卡与字体规范页（对比度表、字号梯度、CSS token）",options:{breakLine:true}},
    {text:"https://xanthiawang.github.io/fathompeak-site/design/palette-type.html",options:{hyperlink:{url:"https://xanthiawang.github.io/fathompeak-site/design/palette-type.html"},color:C.accent,fontFace:MONO,fontSize:9.5,breakLine:true}},
    {text:" ",options:{breakLine:true}},
    {text:"整站    index.html（文字、数据、英文都在这一个文件）",options:{fontFace:MONO,fontSize:9,breakLine:true}},
    {text:"素材    art/logos/ · fonts/",options:{fontFace:MONO,fontSize:9,breakLine:true}},
    {text:"设计    design/（本文档、色卡与字体页）",options:{fontFace:MONO,fontSize:9,breakLine:true}},
    {text:"编辑权限：仓库 Settings → Collaborators 邀请",options:{fontFace:SANS,fontSize:9.5}}
  ],{x:5.2,y:1.7,w:4.3,h:3.6,fontFace:SANS,fontSize:11,color:C.ink70,margin:0,valign:"top",paraSpaceAfter:3});
}
// 03 情绪板与色卡
{ const s=base("情绪板与色卡");
  const moods=[["crops_v3/mood_home.jpg","首页 · 地平线"],["crops_v3/mood_enterprise.jpg","企业合作 · 色雾"],["crops_v3/mood_network.jpg","电站合作 · 地平线"]];
  moods.forEach((m,i)=>{ const y=1.15+i*1.3; frame(s,m[0],0.5,y,3.3,1.063); mono(s,m[1],0.5,y+1.1,3.3,0.18,8); });
  const sw=[["2F63B8","晨蓝 · 文字","#2F63B8",false],["5284D7","晨蓝 · 填充 / 天空","#5284D7",false],["DCE7F7","晨蓝 · 软","#DCE7F7",true],["EEF3FB","晨蓝 · 淡","#EEF3FB",true],
            ["4E3F66","暮紫 · 状态","#4E3F66",false],["EAE4F0","暮紫 · 软","#EAE4F0",true],["B7A8A3","霞","#B7A8A3",false],["3D314F","暮","#3D314F",false],
            ["212021","炭","#212021",false],["E8D4CC","霞光","#E8D4CC",true],["F8F8F8","纸白","#F8F8F8",true],["000000","墨 · 文字","#000 · 85–30%",false]];
  sw.forEach((w,i)=>{ const col=i%4, row=Math.floor(i/4); swatch(s,4.6+col*1.22,1.15+row*1.0,w[0],w[1],w[2],w[3]); });
  // 第四行：内页色雾（企业页等浅色首屏）与基底的另外两色，规范页「十五色四组」至此齐全
  const sw2=[["A9C3E8","雾 1","#A9C3E8",false],["E3ECF8","雾 2","#E3ECF8",true],["EBCFC4","雾 3","#EBCFC4",true],["D6CBDD","雾 4","#D6CBDD",true],["F3F1EA","暖纸","#F3F1EA",true],["FFFFFF","卡白","#FFFFFF",true]];
  sw2.forEach((w,i)=>{ const x=4.6+i*0.79; s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:4.2,w:0.74,h:0.32,fill:{color:w[0]},line:{color:w[3]?"CFCFCF":w[0],width:0.75},rectRadius:0.05}); s.addText(w[1],{x,y:4.54,w:0.75,h:0.17,fontFace:SANS,fontSize:8,color:C.ink,margin:0}); s.addText(w[2],{x,y:4.7,w:0.75,h:0.16,fontFace:MONO,fontSize:7,color:C.ink50,margin:0}); });
  p(s,["白底为主，晨蓝唯一强调色，暮紫只做状态标签，色雾只做内页首屏，颜色之间用渐变衔接。无深色模式。",
       "对比度：晨蓝文字 5.84；填充上白字 3.72，只做大字；暮紫 7.57；炭上白字 16.24；墨 50% 3.93，只做标签。"],0.5,5.0-0.02,9.0,0.4,8);
}
// 04 字体
{ const s=base("字体");
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.15,w:4.6,h:3.95,fill:{color:C.card},line:{color:C.line,width:0.75}});
  s.addText("模型服务与算电协同产品",{x:0.75,y:1.38,w:4.2,h:0.4,fontFace:SERIF,fontSize:17,color:C.ink,margin:0});
  mono(s,"Display 56 · 衬线 400 · 字距 −.03em · 行高 1.08",0.75,1.8,4.2,0.2,8.5);
  s.addText("主流模型 × 绿电算力，一站式 AI 推理服务。",{x:0.75,y:2.12,w:4.2,h:0.35,fontFace:SERIF,fontSize:13,color:C.ink,margin:0});
  mono(s,"H1 38 · 衬线 400 · 行高 1.15（首屏反白）",0.75,2.5,4.2,0.2,8.5);
  s.addText("为什么是沐仞",{x:0.75,y:2.82,w:4.2,h:0.32,fontFace:SERIF,fontSize:14,color:C.ink,margin:0});
  mono(s,"H2 28 · H3 20（卡片标题，字重 500）",0.75,3.16,4.2,0.2,8.5);
  s.addText("统一接入 GLM、DeepSeek、Qwen、MiniMax 等模型，按词元用量计费。",{x:0.75,y:3.46,w:4.2,h:0.45,fontFace:SANS,fontSize:10,color:C.ink70,margin:0});
  mono(s,"Body 17 / 16 / 15 / 14 · 无衬线 400 · 行高 1.6",0.75,3.94,4.2,0.2,8.5);
  s.addText("¥16.00 / M · 上下文 1M · 2026-09-25",{x:0.75,y:4.22,w:4.2,h:0.26,fontFace:MONO,fontSize:9.5,color:C.ink,margin:0});
  mono(s,"Number 15 / 12 · 等宽　Label 11 · 等宽大写 · 字距 .08em",0.75,4.5,4.2,0.2,8.5);
  mono(s,"样张为系统字体代显",0.75,4.78,4.2,0.2,8);
  h(s,"三组字体",5.4,1.2,4.1);
  s.addTable([
    [{text:"用途",options:{bold:true}},{text:"拉丁",options:{bold:true}},{text:"中文回退",options:{bold:true}}],
    ["标题 / 展示","Fraunces","思源宋体"],
    ["正文 / 界面","DM Sans","思源黑体"],
    ["数字 / 标签","DM Mono","思源黑体"]
  ],{x:5.4,y:1.5,w:4.1,colW:[1.4,1.35,1.35],fontFace:SANS,fontSize:9.5,color:C.ink70,border:{pt:0.5,color:C.line},fill:{color:C.card},rowH:0.32,margin:0.05});
  h(s,"字号梯度（px）",5.4,3.0,4.1);
  bullets(s,["56 / 38 / 28 / 20 衬线：展示、首屏、区块、卡片标题。","17 / 16 / 15 / 14 / 13 无衬线：导语、正文、卡片、表格、脚注。","15 / 12 / 11 等宽：数字、代码与大写标签。","五款均为 OFL；拉丁三款自托管，中文两款经 Google Fonts 非阻塞加载。"],5.4,3.3,4.1,2.0,10);
}
// 05 按钮与胶囊
{ const s=base("按钮与胶囊");
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.15,w:4.6,h:3.95,fill:{color:C.card},line:{color:C.line,width:0.75}});
  mono(s,"主按钮 · 默认",0.8,1.4,2,0.2); s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.8,y:1.65,w:2.1,h:0.47,fill:{color:"000000"},line:{color:"000000",width:0},rectRadius:0.235}); s.addText("获取 API Key ↓",{x:0.8,y:1.65,w:2.1,h:0.47,fontFace:SANS,fontSize:11,bold:true,color:"FFFFFF",align:"center",valign:"middle",margin:0});
  mono(s,"主按钮 · 悬停",3.0,1.4,2,0.2); s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:3.0,y:1.65,w:1.9,h:0.47,fill:{color:"424242"},line:{color:"424242",width:0},rectRadius:0.235}); s.addText("获取 API Key ↓",{x:3.0,y:1.65,w:1.9,h:0.47,fontFace:SANS,fontSize:11,bold:true,color:"FFFFFF",align:"center",valign:"middle",margin:0});
  mono(s,"次按钮",0.8,2.45,2,0.2); s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.8,y:2.7,w:1.7,h:0.47,fill:{color:"EBEBEB"},line:{color:"EBEBEB",width:0},rectRadius:0.235}); s.addText("先自助试用",{x:0.8,y:2.7,w:1.7,h:0.47,fontFace:SANS,fontSize:11,bold:true,color:C.ink,align:"center",valign:"middle",margin:0});
  mono(s,"首屏主按钮（56 高）",3.0,2.45,2,0.2); s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:3.0,y:2.7,w:1.9,h:0.58,fill:{color:"000000"},line:{color:"000000",width:0},rectRadius:0.29}); s.addText("获取 API Key ↓",{x:3.0,y:2.7,w:1.9,h:0.58,fontFace:SANS,fontSize:12.5,bold:true,color:"FFFFFF",align:"center",valign:"middle",margin:0});
  mono(s,"筛选胶囊 · 选中 / 未选",0.8,3.6,3,0.2);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.8,y:3.85,w:0.7,h:0.32,fill:{color:"000000"},line:{color:"000000",width:0},rectRadius:0.16}); s.addText("全部",{x:0.8,y:3.85,w:0.7,h:0.32,fontFace:SANS,fontSize:9,color:"FFFFFF",align:"center",valign:"middle",margin:0});
  ["对话","推理"].forEach((t,i)=>{ s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:1.6+i*0.8,y:3.85,w:0.7,h:0.32,fill:{color:"FFFFFF"},line:{color:"D5D5D5",width:0.75},rectRadius:0.16}); s.addText(t,{x:1.6+i*0.8,y:3.85,w:0.7,h:0.32,fontFace:SANS,fontSize:9,color:C.ink,align:"center",valign:"middle",margin:0}); });
  mono(s,"文字链接（下划线偏移 6px，线色墨 30%）",0.8,4.45,3.6,0.2); s.addText("浏览模型市场 →",{x:0.8,y:4.7,w:2,h:0.3,fontFace:SANS,fontSize:11,color:C.ink,underline:{color:"B3B3B3"},margin:0});
  h(s,"规格",5.4,1.2,4.1);
  bullets(s,["主按钮：纯黑胶囊，高 45，左右内距 32，字 16 / 500 白；首屏版高 56，字 18，左右内距 40。",
             "悬停：底色变 #424242，0.2 秒缓动；不抬升，不加影。",
             "次按钮：浅灰 rgba(235,235,235,.7)，字黑；悬停为墨 5%。",
             "筛选胶囊：高 32，选中黑底白字，未选白底细线，单选。",
             "文字链接：黑字加淡下划线，箭头收尾；悬停字色为墨 50%。",
             "键盘焦点：2px 晨蓝描边，外扩 2px，所有可点元素统一。",
             "代码块：底 #141416、字 #E8E6DF，只在文档页。",
             "折叠问答：12px 细加号 40% 透明，展开转 45° 成叉，答案 0.4 秒展开；分割线悬停加深。"],5.4,1.5,4.1,3.9,9.5);
}
// 06 导航
{ const s=base("导航");
  frame(s,"crops_v3/pill.jpg",0.5,1.2,6.0,0.65);
  h(s,"桌面 · 固定胶囊",0.5,2.05,6);
  bullets(s,["固定在页面顶部 28px，高 52，圆角 16，纸白底加 12px 磨砂，1px 墨 8% 细线，阴影 0 2px 8px 墨 6%。",
             "左侧 40×40 山形 logo；五个内容链接（产品与服务、企业合作、电站合作、新闻动态、文档）16px，间距 34；默认 30% 透明，悬停与当前页 100%，0.2 秒。",
             "右端次级入口：细分隔线后是「登录」，登录后变「控制台」；再右是「EN」，就地翻译当前页。",
             "胶囊里不放按钮；首页的行动按钮只在首屏。"],0.5,2.35,6,1.75,10);
  h(s,"手机 · 整宽胶囊与展开菜单",0.5,4.2,6);
  p(s,["距顶 14，整宽，圆角 30；右侧「+」点开后胶囊长到接近全屏，菜单为 56px 细字灰色大字（比桌面多一项「指南」），当前页黑；底部一黑一灰两个按钮：获取 API Key、登录。"],0.5,4.5,6,0.85,10);
  frame(s,"crops_v3/m_home.jpg",6.75,1.2,1.3,2.81); mono(s,"手机首页",6.75,4.08,1.3,0.2,8);
  frame(s,"crops_v3/m_menu.jpg",8.15,1.2,1.3,2.81); mono(s,"菜单展开",8.15,4.08,1.3,0.2,8);
}
// 07 页脚
{ const s=base("页脚");
  frame(s,"crops_v3/footer_only.jpg",0.5,1.15,FW,FW/FA);
  h(s,"结构",0.5,1.3+FW/FA,9);
  bullets(s,["五栏：联系我们 · 产品 · 资源 · 公司 · 关注；下方一整行周报订阅，最后一行版权与备案号。",
             "栏标题 13px 等宽黑字；链接 13px 等宽、墨 50%，悬停变黑；880px 以下两栏，手机单栏。"],0.5,1.6+FW/FA,9,0.6,10);
}
// 08 首页设计
{ const s=base("首页设计");
  frame(s,"crops_v3/home_full.jpg",0.5,1.2,4.6,2.875);
  h(s,"首屏构图（桌面 1440 × 900）",5.4,1.2,4.1);
  s.addTable([
    ["首屏高度","一屏（100svh），最小 640"],["导航到标题","36px；标题 38 距顶 116，副标 20，说明 15"],["大字标「沐仞」","宽约 52% 屏宽，白 12%，距顶 270"],["产品窗","宽 68%（最宽 980），距顶 46% 屏高，白 82% 加 22px 模糊，底部渐隐"],["地平线","弧顶约 235，圆半径一个屏宽，霞光带约 130"],["白弧与按钮","弧高 200；黑按钮 56 高，距底 22"]
  ],{x:5.4,y:1.5,w:4.1,colW:[1.2,2.9],fontFace:SANS,fontSize:9,color:C.ink70,border:{pt:0.5,color:C.line},fill:{color:C.card},rowH:0.3,margin:0.05});
  h(s,"区块顺序",0.5,4.25,4.6);
  p(s,["首屏 → 合作滚动带 → 三个核心能力 → 行业与场景 → 项目案例 → 为什么是沐仞 → 新闻动态 → 常见问题 → 行动区。"],0.5,4.55,4.6,0.55,9.5);
  h(s,"动效",5.4,3.6,4.1);
  p(s,["区块进入视口 1 秒渐显；切换页面 0.4 秒淡入；滚动带悬停暂停；支持减少动效偏好。"],5.4,3.9,4.1,0.6,10);
}
// 09 其他页面与用户流程
{ const s=base("其他页面与用户流程");
  const imgs=[["crops_v3/d_models.jpg","产品与服务"],["crops_v3/d_enterprise.jpg","企业采购与海外服务"],["crops_v3/d_network.jpg","电站合作"],["crops_v3/d_start.jpg","账户开通流程（预览）"]];
  imgs.forEach((im,i)=>{ const x=0.5+(i%2)*3.1, y=1.15+Math.floor(i/2)*2.05; frame(s,im[0],x,y,2.9,1.81); mono(s,im[1],x,y+1.84,2.9,0.18,8); });
  h(s,"页面与流程",6.75,1.15,2.75);
  bullets(s,["产品与服务：三类产品加节点合作，一张闭环图，四段详情。",
             "开发者：首屏按钮 → 正式平台创建账户与 Key → 按文档接入。",
             "企业与机构：企业合作页 → 测试、报价 → 联系销售。",
             "电站与资产方：电站合作页 → 留表。",
             "登录只有一个入口，未登录进控制台会落到登录页。",
             "新闻只放可查证的报道，附出处链接。"],6.75,1.45,2.75,3.6,9);
}
// 10 资产与备注
{ const s=base("资产与备注");
  h(s,"资产",0.5,1.2,4.6);
  frame(s,"crops_v3/logos.jpg",0.5,1.6,4.6,0.86);
  bullets(s,["合作与生态 logo：8 个 PNG，去色，80px 高（2 倍），取自公司商业计划书；清华、北大用文字词标。",
             "品牌标志：山形 logo 为内联 SVG；页面图形（曲线、窗口）均为 CSS 与 SVG，无位图。",
             "字体：拉丁三款自托管，中文两款 Google Fonts；无图标库。"],0.5,2.65,4.6,1.5,10);
  h(s,"上线前要替换的演示内容",0.5,4.25,4.6);
  p(s,["节点定价与评价、实时成交看板（测试站演示数据）；控制台数字、订单号与 Key；企业账号对比表；文档里的接口细节；指南正文。"],0.5,4.55,4.6,0.85,9.5);
  h(s,"待公司确认",5.4,1.2,4.1);
  bullets(s,["一体机：混插机型叫 S2 还是 S4；形态按 S1–S3 还是风冷 / 液冷 / 集装箱。","平台名称：绿色词元交易平台或低碳词元直销平台；养老 App 是否上网站。","正式 API 地址与接口文档（测试环境地址为 test.api.fathom.cn）。","企业账号权益（对公、月结、专票、子账号）；合作伙伴各家关系；对外邮箱是否改域名邮箱。"],5.4,1.6,4.1,2.5,10);
  h(s,"备注",5.4,4.25,4.1);
  p(s,["无深色模式；单文件，按 token 实现。境内稳定访问需放到公司备案域名：把仓库内容放到网站根目录即可。"],5.4,4.55,4.1,0.6,9.5);
}
pres.writeFile({ fileName: "沐仞官网设计交付_2026-10-13_v3.pptx" }).then(f=>console.log("written",f));
