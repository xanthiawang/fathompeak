"""BP-grounded editorial diagrams. Text and arrows remain editable SVG objects."""
from pathlib import Path
import base64
import hashlib
import html
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
ARTICLE = HERE / "article-compute-energy"
OUT = ARTICLE / "architecture-bp-v2"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
BLUE, INK, GRAY = "#2F63B8", "#212021", "#60636A"
fonts = {}
texts = []

def article_source():
    revised = ARTICLE / "正文_用户修订稿_v2_2026-10-20.md"
    return revised if revised.exists() else ARTICLE / "正文_用户原稿_2026-10-20.md"


def revised_anchors():
    return {
        1: "这背后，计算设备、供电条件与网络传输需要共同优化。",
        2: "围绕这一思路，我们推进“前店后厂”方案。",
        3: "在计算侧，Tapestrix 处理模型与设备之间的映射，",
        4: "在这个基础上，我们还构建了以分布式通信为基础的网络调度架构。",
        5: "那么，这种统一调度如何形成新的供给方式？",
        6: "再往后，则是我们希望构建的全球分布式算网。",
    }

def refine_article_typography(root):
    """Reading hierarchy and verified contact footer; article prose stays verbatim."""
    from lxml import html as lh
    article = root.xpath("//article")[0]
    for old in article.xpath('./section[@id="article-resources"]'):
        article.remove(old)
    footer_started = False
    for node in list(article):
        if node.get("data-source") == "heading" and "相关资源获取" in node.text_content():
            footer_started = True
        if footer_started and node.get("data-source"):
            article.remove(node)
    highlights = [
        "用户真正需要的，不只是一次调用，而是以能够接受的成本和速度，持续获得模型服务。",
        "我们的思路是“调算找电”",
        "我们推进“前店后厂”方案",
        "理念上的算电协同，必须在工程上落地为统一调度。",
        "在计算侧，Tapestrix 处理模型与设备之间的映射",
        "NetWeaver 将网络延迟纳入预测与约束",
        "真正的挑战在于：如何让一处能够执行模型任务的计算节点，成为一张可部署、可运营、可结算，并能持续交付模型服务的算网。",
        "从用户需求出发，在能源与网络约束下组织计算",
        "以绿色能源承载全球计算。",
    ]
    for p in article.xpath('./p[@data-source="paragraph"]'):
        value=p.text_content()
        for phrase in highlights:
            if phrase in value:
                for child in list(p):p.remove(child)
                start,end=value.split(phrase,1)
                p.text=start
                strong=lh.Element("strong");strong.text=phrase;strong.tail=end;p.append(strong)
                break
    closing=article.xpath('./img[@src="assets/closing.png"]')[0]
    closing.set("id","brand-follow")
    footer=lh.fromstring('''<section id="article-resources" class="article-resources" aria-label="相关资源与联系信息">
<div class="resource-group"><h2>相关资源获取</h2><nav aria-label="沐仞产品资源"><a href="https://www.fathompeak.cn/#models" target="_blank" rel="noopener">模型与服务</a><a href="https://www.fathompeak.cn/#guides" target="_blank" rel="noopener">API 接入指南</a><a href="https://www.fathompeak.cn/#network" target="_blank" rel="noopener">电站合作</a></nav></div>
<div class="resource-group"><h2>更多信息</h2><dl>
<div><dt>官方网址</dt><dd><a href="https://www.fathompeak.cn/" target="_blank" rel="noopener">www.fathompeak.cn</a></dd></div>
<div><dt>微信咨询</dt><dd><a href="#brand-follow">扫码关注下方「沐仞科技」公众号</a></dd></div>
<div><dt>商务合作</dt><dd><a href="mailto:fathompeak@163.com">fathompeak@163.com</a></dd></div>
</dl></div></section>''')
    closing.addprevious(footer)
    for old in root.xpath('//style[@id="article-reading-refinement"]'):old.getparent().remove(old)
    style=lh.Element("style",id="article-reading-refinement")
    style.text="""
@font-face{font-family:'Noto Sans SC';src:url(assets/fonts/Noto-sans-SC-Semibold.ttf);font-weight:600;font-display:swap}
.article{max-width:760px;padding:36px 38px;color:#303238}
.article h1{font:600 28px/1.5 'DM Sans','Noto Sans SC',sans-serif;margin:16px 0 20px;letter-spacing:0;text-wrap:pretty;color:#212021}
.article .meta{font:400 13px/1.65 'Noto Sans SC',sans-serif;color:#777;margin-bottom:18px}
.article p{font:400 17px/1.95 'DM Sans','Noto Sans SC',sans-serif;margin:23px 0;letter-spacing:0}
.article strong{font-weight:600;color:#212021}
.article>h2[data-source=heading]{font:600 20px/1.6 'Noto Sans SC',sans-serif;color:#212021;margin:38px 0 18px;letter-spacing:0;text-wrap:pretty;scroll-margin-top:24px}
.article figcaption{font:400 12px/1.75 'Noto Sans SC',sans-serif;color:#757575;margin-top:12px}
.article figure{margin:30px 0 34px}
.article .article-resources{margin:40px 0 22px;padding:24px 0 0;border-top:1px solid #e4e4e4}
.article-resources .resource-group+.resource-group{margin-top:22px}
.article .article-resources h2{font:600 15px/1.6 'Noto Sans SC',sans-serif;letter-spacing:0;margin:0 0 10px;color:#212021}
.article-resources nav{display:flex;gap:8px 22px;font:400 14px/1.8 'Noto Sans SC',sans-serif}
.article-resources a{color:#454952;text-decoration:underline;text-decoration-color:#b5bac2;text-underline-offset:4px;overflow-wrap:anywhere}
.article-resources a:hover{color:#2F63B8}
.article-resources a:focus-visible{outline:2px solid #2F63B8;outline-offset:4px}
.article-resources dl{margin:0;font:400 14px/1.8 'Noto Sans SC',sans-serif}
.article-resources dl>div{display:grid;grid-template-columns:72px minmax(0,1fr);column-gap:14px;margin:8px 0}
.article-resources dt{color:#6a6d73}.article-resources dd{margin:0}
#brand-follow{scroll-margin-top:24px;margin-top:24px}
.gallery h2{font:600 20px/1.5 'Noto Sans SC',sans-serif}
@media(max-width:700px){.article>h2[data-source=heading]{font-size:18px;line-height:1.65;margin:32px 0 16px}.article{padding:24px 20px}.article h1{font-size:24px;line-height:1.5}.article p{font-size:16px;line-height:1.9;margin:21px 0}.article figure{margin:28px -4px}.article .article-resources{margin-top:32px;padding-top:22px}.article .article-resources h2{font-size:15px}.article-resources nav,.article-resources dl{font-size:13px}.article-resources dl>div{column-gap:10px;grid-template-columns:64px minmax(0,1fr)}}
"""
    root.xpath("//head")[0].append(style)

def select_editorial():
    global OUT
    OUT = ARTICLE / "architecture-editorial-v3"


def editorial_diagrams():
    """Illustrated functional summaries; BP detail stays in the preceding edition."""
    rows = [
        ("01_算电协同整体架构", "01-supply", "把能源与计算，组织成持续供给",
         "前店承接需求，协同安排任务，后厂完成执行。",
         [("前店 · 词元交易平台", "模型目录 · API · 服务等级", "接入、采购与用量结算"),
          ("算电协同调度", "算力管理 · 电力管理 · 协同调度", "共同考虑设备、能源与网络"),
          ("后厂 · 词元工厂", "电站侧设备 · 异构 GPU", "执行任务，交付模型服务")],
         "需求与约束", "任务安排", "运行观测与能源条件 → 更新调度", "14、20–23"),
        ("02_NetWeaver联合调度架构", "02-network", "NetWeaver：让任务找到合适的节点",
         "网络延迟成为调度条件，节点选择围绕交付要求展开。",
         [("理解任务", "服务等级 · 位置 · 通信计算画像", "明确负载与延迟边界"),
          ("TransElect 联合调度", "任务 · 网络 · 算力 · 电力", "结合数据位置与模型缓存"),
          ("分布式节点执行", "按任务条件选择执行节点", "控制面统筹 · 数据面直连")],
         "任务画像", "节点选择", "时延、负载与能耗反馈 → 更新调度", "17"),
        ("03_Tapestrix运行时调度架构", "03-runtime", "Tapestrix：从模型请求到 GPU 执行",
         "依据请求、性能图谱与设备状态，动态安排运行方式。",
         [("识别请求", "文本 · 图像 · 混合批次", "识别规模与服务等级目标"),
          ("运行时控制器", "性能图谱 · 队列 · GPU 状态", "选择执行计划与资源配置"),
          ("选择执行方式", "多 GPU 动态并行", "或单 GPU 空间／时空共享")],
         "负载特征", "执行计划", "GPU 状态与运行信息 → 更新执行计划", "15、21"),
    ]
    result=[]
    for i,(stem,art,title,sub,stages,a,b,feedback,pages) in enumerate(rows,1):
        s=base(i,title,sub,1120)
        raw=(OUT/"assets"/(art+".png")).read_bytes()
        s+=f'<image href="data:image/png;base64,{base64.b64encode(raw).decode()}" x="65" y="235" width="1670" height="557" preserveAspectRatio="xMidYMid meet"/>'
        # Connectors occupy a separate band, away from image details and labels.
        for x,label in [(615,a),(1170,b)]:
            s+=arrow(f"M{x-75} 805 H{x+75}")
            s+=t(x,778,label,24,GRAY,center=True)
        for x,(heading,line1,line2) in zip([345,900,1455],stages):
            s+=t(x,855,heading,37,INK,"Noto Serif SC",True)
            s+=t(x,909,line1,27,GRAY,center=True)
            s+=t(x,952,line2,27,GRAY,center=True)
        s+=arrow("M1455 978 V1010 H900 V978",True)
        s+=t(900,1062,feedback,26,GRAY,center=True)
        s+=t(80,1100,f"BP {pages} 页 · 功能关系示意，非接口拓扑；图中设备为概念插画。",21,GRAY)
        result.append((stem,s+"</svg>"))
    return result


def t(x, y, value, size=36, color=INK, family="Noto Sans SC", center=False):
    texts.append(value)
    anchor = ' text-anchor="middle"' if center else ""
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{color}"{anchor}>{html.escape(value)}</text>'


def box(x, y, w, h, fill="#FFFFFF", stroke="#D4DAE2"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def arrow(d, feedback=False):
    dash = ' stroke-dasharray="9 8"' if feedback else ""
    color = GRAY if feedback else BLUE
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3"{dash} marker-end="url(#{("feedback" if feedback else "flow")})"/>'


def connector(d):
    return f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="3"/>'


def base(num, title, subtitle, height):
    s = f'<svg xmlns="{NS}" width="1800" height="{height}" viewBox="0 0 1800 {height}"><rect width="1800" height="{height}" fill="white"/><defs>'
    for name, color in [("flow", BLUE), ("feedback", GRAY)]:
        s += f'<marker id="{name}" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8Z" fill="{color}"/></marker>'
    s += '</defs>'
    s += t(80, 65, f"FATHOMPEAK / ARCHITECTURE {num:02}", 25, BLUE, "DM Mono")
    s += t(80, 150, title, 58, INK, "Noto Serif SC")
    s += t(80, 208, subtitle, 31, GRAY)
    return s


def foot(y, source):
    return t(80, y, source, 25, GRAY) + t(80, y+42, "依 BP 重绘的逻辑架构 · 保留模块关系，省略实现细节与性能指标", 25, GRAY)


def diagrams():
    out = []
    s = base(1, "从词元交易，到电站侧执行", "前店后厂的功能架构，以及贯穿其中的算电协同能力", 1740)
    s += box(80, 260, 1640, 180, "#F0F5FC")
    s += t(120, 320, "前店 · 沐仞词元交易平台", 44, BLUE)
    s += t(120, 385, "模型目录  /  API 接入  /  SLA 分级  /  按量结算  /  能碳账单", 35)
    s += arrow("M900 440 V510") + t(940, 486, "服务需求与交付约束", 28, GRAY)
    s += box(80, 525, 1640, 365, "#F8F8F8")
    s += t(120, 588, "绿色词元算电协同基座", 42)
    agents = [
        ("算力集群管理智能体", "单卡级、进程级观测", "GPU 能耗预测与调控", "Tapestrix 模型—设备映射"),
        ("电力资源管理智能体", "电站群观测与调控", "发电量与电价预测", "电量、电价条件"),
        ("算电协同调度智能体", "计算任务跨空间调度", "容错与并发控制", "服务质量与网络保障"),
    ]
    for i, lines in enumerate(agents):
        x = 110+i*540
        s += box(x, 625, 500, 230)
        s += t(x+24, 680, lines[0], 36, BLUE)
        for j, line in enumerate(lines[1:]):
            s += t(x+24, 734+j*45, line, 29, GRAY)
    s += arrow("M900 890 V955") + t(940, 934, "任务安排与运行调控", 28, GRAY)
    s += box(80, 970, 1640, 225)
    s += t(120, 1027, "后厂 · 电站侧词元工厂", 44)
    s += t(120, 1090, "物理部署", 32, BLUE)
    s += t(120, 1144, "词元一体机 · 异构 GPU 混插", 32)
    s += t(715, 1090, "分布式通信", 32, BLUE)
    s += t(715, 1144, "NetWeaver · 延迟约束", 32)
    s += t(1260, 1090, "能碳计量", 32, BLUE)
    s += t(1260, 1144, "订单级可追溯", 32)
    s += arrow("M1725 1155 H1760 V565 H1723", True)
    s += t(900, 1250, "运行观测与能源条件持续反馈至调度", 30, GRAY, center=True)
    raw = (OUT/"assets/infrastructure-strip.png").read_bytes()
    s += f'<image href="data:image/png;base64,{base64.b64encode(raw).decode()}" x="150" y="1280" width="1500" height="330" preserveAspectRatio="xMidYMid meet"/>'
    s += foot(1640, "来源：FathomPeak_BP_9.15 · 第 14、20–23 页")
    out.append(("01_算电协同整体架构", s+"</svg>"))

    s = base(2, "NetWeaver：把延迟纳入联合调度", "任务要求、网络状态、数据位置、算力与电力条件，共同决定执行节点", 1880)
    s += box(100, 255, 1530, 125, "#F0F5FC")
    s += t(140, 309, "01  全局任务网关", 39, BLUE)
    s += t(140, 355, "企业 API、实时与批量任务等入口  →  SLA 识别、位置识别、准入控制", 29)
    s += arrow("M865 380 V420")
    s += box(100, 435, 1530, 130)
    s += t(140, 490, "02  任务通信—计算画像", 39)
    s += t(140, 535, "数据量 · 计算强度 · 通信频率 · GPU／显存需求 · 截止时间 · 数据位置", 29, GRAY)
    s += connector("M865 565 V585 H470 M865 585 H1255")
    s += arrow("M470 585 V610") + arrow("M1255 585 V610")
    for x, title, line in [(100, "实时网络状态", "时延、丢包、抖动、带宽、稳定性"), (885, "数据局部性与模型缓存", "模型预分发、热点缓存、数据所在位置")]:
        s += box(x, 620, 745, 130, "#F8F8F8")
        s += t(x+30, 675, title, 36)
        s += t(x+30, 720, line, 29, GRAY)
    s += connector("M470 750 V785 H1255 V750") + arrow("M865 785 V810")
    s += box(100, 820, 1530, 255, "#F0F5FC", "#A5BFE6")
    s += t(140, 879, "03  TransElect 网络感知型联合调度核心", 40, BLUE)
    for i, (a,b,c) in enumerate([
        ("任务图", "任务类型、SLA", "计算与通信强度"),
        ("网络图", "时延、丢包、带宽", "抖动与稳定性"),
        ("算力图", "GPU 空闲、显存", "队列、模型预热"),
        ("电力图", "出力、电价、绿电", "节点负荷、功耗"),
    ]):
        x=140+i*370
        s += t(x, 945, a, 36) + t(x, 997, b, 29, GRAY) + t(x, 1040, c, 29, GRAY)
    s += arrow("M865 1075 V1115")
    s += box(100, 1130, 1530, 165)
    s += t(140, 1183, "04  选择节点与执行策略", 39)
    for i,(a,b) in enumerate([("强同步任务","本地高速集群"),("在线低延迟","用户近端节点"),("非实时高算力","绿电富余节点"),("数据本地性","数据所在节点")]):
        x=140+i*370
        s += t(x, 1235, a, 30, BLUE) + t(x, 1275, b, 29, GRAY)
    s += connector("M865 1295 V1315 H470 M865 1315 H1255")
    s += arrow("M470 1315 V1340") + arrow("M1255 1315 V1340")
    for x, title, line1, line2 in [
        (100,"05A  控制面 · 集中优化","全局调度、SLA 策略、健康检查","故障切换与网络状态采集"),
        (885,"05B  数据面 · 去中心化直连","节点直连、多路径传输、缓存同步","数据分片、结果回传与 QoS 控制"),
    ]:
        s += box(x,1350,745,185,"#F8F8F8")
        s += t(x+30,1405,title,34) + t(x+30,1460,line1,28,GRAY)+t(x+30,1505,line2,28,GRAY)
    s += connector("M470 1535 V1555 H1255 V1535") + arrow("M865 1555 V1580")
    s += box(100,1590,1530,125,"#F0F5FC")
    s += t(140,1643,"06  闭环反馈与调度策略更新",38,BLUE)
    s += t(140,1688,"网络与排队时延、计算耗时、能耗、电费、绿电占比、SLA 状态、重试与体验",28)
    s += arrow("M1630 1655 H1690 V940 H1633",True)
    s += foot(1780,"来源：FathomPeak_BP_9.15 · 第 17 页；按原图流程压缩重绘")
    out.append(("02_NetWeaver联合调度架构",s+"</svg>"))

    s = base(3, "Tapestrix：从模型请求到 GPU 执行", "以性能画像和运行状态，驱动多卡并行与单卡资源共享", 1670)
    s += box(100,260,1530,130,"#F0F5FC")
    s += t(140,315,"01  异构多模态请求输入",40,BLUE)
    s += t(140,362,"文本、图像、混合动态批次  /  分辨率、批次组成、队列长度、SLO 与 GPU 预算",29)
    s += arrow("M865 390 V425")
    s += box(100,440,1530,165)
    s += t(140,492,"02  按阶段拆解推理流水线",39)
    stages=["预处理","视觉编码","模态融合","LLM 预填充","LLM 解码"]
    for i,label in enumerate(stages):
        x=140+i*296
        s += t(x,562,label,33)
        if i<4: s += arrow(f"M{x+206} 552 H{x+268}")
    s += arrow("M865 605 V642")
    s += box(100,655,1530,165,"#F8F8F8")
    s += t(140,708,"03  性能图谱与运行状态",39)
    s += t(140,761,"编码器性能模型、LLM 分块模型、Kernel 画像、并行集合与通信开销",30,GRAY)
    s += t(140,802,"离线 Profiling ＋ 运行时查询；结合请求队列、GPU 状态与 SLO 约束",28,GRAY)
    s += arrow("M865 820 V857")
    s += box(100,870,1530,125,"#F0F5FC","#A5BFE6")
    s += t(140,924,"04  运行时调度控制器",40,BLUE)
    s += t(140,969,"查询性能图谱  →  识别负载类型  →  选择执行计划",32)
    s += arrow("M865 995 V1030 H470 V1050") + arrow("M865 1030 H1255 V1050")
    for x,title,l1,l2,l3 in [
        (100,"05A  多卡动态并行","RESONATOR 动态调度","PRISM 多选择背包优化","DP／TP 并行切换 · 逻辑分片"),
        (885,"05B  单卡细粒度共享","互补负载：SM 空间共享","竞争负载：时空共享","按 Kernel 绑定执行流"),
    ]:
        s += box(x,1065,745,245)
        s += t(x+30,1126,title,37)
        for j,line in enumerate([l1,l2,l3]):s += t(x+30,1185+j*47,line,30,GRAY)
    s += connector("M470 1310 V1345 H1255 V1310") + arrow("M865 1345 V1370")
    s += box(100,1380,1530,145,"#F8F8F8")
    s += t(140,1436,"06  GPU 执行底座",40)
    s += t(140,1490,"GPU SM  /  HBM  /  CUDA Stream  /  cuBLAS、CUTLASS  /  NCCL、NVLink、PCIe",28,GRAY)
    s += arrow("M1630 1450 H1690 V931 H1633",True)
    s += foot(1570,"来源：FathomPeak_BP_9.15 · 第 15 页；管理智能体关联见第 21 页")
    out.append(("03_Tapestrix运行时调度架构",s+"</svg>"))
    return out


def prepare_fonts():
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    from fontTools import subset
    import uharfbuzz as hb
    d=OUT/"assets/fonts"; d.mkdir(parents=True,exist_ok=True)
    chars="".join(texts)
    for family, stem, full in [
        ("Noto Sans SC","Noto-sans-SC","/tmp/fathompeak-article-noto-sans-full.ttf"),
        ("Noto Serif SC","Noto-serif-SC","/tmp/fathompeak-article-noto-serif-full.ttf"),
    ]:
        font=TTFont(full)
        if "fvar" in font:font=instantiateVariableFont(font,{"wght":400},inplace=True)
        sub=subset.Subsetter();sub.populate(text=chars);sub.subset(font);font.save(d/(stem+".ttf"))
    for stem in ["DM-Sans","DM-Mono","Fraunces"]:
        shutil.copy2(ARTICLE/"assets/fonts"/(stem+".ttf"),d/(stem+".ttf"))
    for p in (ARTICLE/"assets/fonts").glob("*OFL.txt"):shutil.copy2(p,d/p.name)
    for family,stem in [("Noto Sans SC","Noto-sans-SC"),("Noto Serif SC","Noto-serif-SC"),("DM Sans","DM-Sans"),("DM Mono","DM-Mono"),("Fraunces","Fraunces")]:
        p=d/(stem+".ttf");tt=TTFont(p);fonts[family]=(tt,hb.Font(hb.Face(p.read_bytes())),tt.getBestCmap(),p)


def save(name,svg):
    import uharfbuzz as hb
    from fontTools.pens.svgPathPen import SVGPathPen
    faces="".join(f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{base64.b64encode(items[3].read_bytes()).decode()})}}" for family,items in fonts.items())
    svg=svg.replace("<defs>",f"<style>{faces}</style><defs>",1)
    p=OUT/(name+".svg");p.write_text(svg)
    root=ET.fromstring(svg)
    for parent in list(root.iter()):
        for node in list(parent):
            if node.tag!=f"{{{NS}}}text":continue
            value=node.text or "";family=node.get("font-family");tt,hbf,cmap,_=fonts[family]
            assert all(ord(c) in cmap for c in value), f"Missing glyph in {value}"
            scale=float(node.get("font-size"))/tt["head"].unitsPerEm
            buf=hb.Buffer();buf.add_str(value);buf.guess_segment_properties();hb.shape(hbf,buf)
            g=ET.Element(f"{{{NS}}}g",{"fill":node.get("fill"),"aria-label":value})
            cursor=0; glyphs=tt.getGlyphSet();order=tt.getGlyphOrder()
            for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
                pen=SVGPathPen(glyphs);glyphs[order[info.codepoint]].draw(pen)
                if pen.getCommands():ET.SubElement(g,f"{{{NS}}}path",{"d":pen.getCommands(),"transform":f"translate({cursor+pos.x_offset*scale} {-pos.y_offset*scale}) scale({scale} {-scale})"})
                cursor+=pos.x_advance*scale
            x=float(node.get("x"));y=float(node.get("y"))
            if node.get("text-anchor")=="middle":x-=cursor/2
            # Guard every label against the canvas edge.
            assert x>=60 and x+cursor<=1740, (value,x,cursor)
            g.set("transform",f"translate({x} {y})")
            pos=list(parent).index(node);parent.remove(node);parent.insert(pos,g)
    op=OUT/(name+"_outlined.svg");ET.ElementTree(root).write(op,encoding="unicode")
    subprocess.run(["rsvg-convert",str(op),"-o",str(OUT/(name+".png"))],check=True)


def publish_page(items):
    source=Path("/Users/zixin/Desktop/沐仞科技/01_公司原始资料/FathomPeak_BP_9.15.pptx")
    manifest={"source":source.name,"sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
              "reviewed_on":"2026-10-20","reviewed_pages":[14,15,17,20,21,22,23],
              "read_method":"PPTX text extraction plus rendered inspection of architecture pages",
              "figures":[{"file":n,"pages":p} for (n,_),p in zip(items,[[14,20,21,22,23],[17],[15,21]])],
              "reference_articles":{"qLRAsPGzhPaNVx1oL-FHGQ":"unreadable","MDZm5cMzwxGJpHU38Racag":"unreadable"},
              "imagegen":{"mode":"built-in","asset":"assets/infrastructure-strip.png","prompt":"White editorial engraving strip: solar and offshore wind, modular server facility, globe. Three isolated vignettes; black, gray, restrained #5284D7. No text, arrows, data, logos or inter-vignette connectors."}}
    if OUT.name=="architecture-editorial-v3":
        manifest["edition"]="Every-inspired editorial functional summaries"
        manifest["imagegen"]={"mode":"built-in", "prompts":"generation-prompts.json", "assets":["assets/01-supply.png","assets/02-network.png","assets/03-runtime.png","assets/00-hero.png"], "direct_text_alternative":"assets/direct-text-comparison.png", "review":"Primary labels typeset deterministically. Direct-text alternative has correct main English labels but includes tiny pseudo UI text and is retained only for visual comparison."}
    (OUT/"sources.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    notes="""# BP 架构重绘依据 · 2026-10-20

依据公司原始资料 `FathomPeak_BP_9.15.pptx`。已读取全部可提取文字，并逐页检查第 14、15、17、20、21、22、23 页的渲染图。版本哈希见 sources.json。

| 配图 | BP 页码 | 保留的信息 | 编辑归纳 |
|---|---|---|---|
| 整体架构 | 14、20–23 | 前店后厂、三个智能体、物理部署、通信、计量 | 将功能整理成需求—调度—执行三组；箭头表示逻辑关系，不代表已核实的接口调用拓扑 |
| NetWeaver | 17 | 网关、任务画像、网络与数据局部性、TransElect 四图联合调度、节点选择、控制面／数据面、反馈 | 按文章阅读顺序压缩为六步；未复制具体地域节点及性能倍数 |
| Tapestrix | 15、21 | 请求、推理流水线、性能图谱、运行时控制器、多卡并行与单卡共享、GPU 执行底座 | 合并原图 5A／5B；保留 RESONATOR 与 PRISM；GPU 状态反馈归纳自控制器输入 |

## 文章中的位置

1. 整体架构：第一节解释“前店后厂”之后，替换旧图 2。
2. NetWeaver：第二节介绍 NetWeaver 的段落之后，替换旧图 3 并移动到对应段落。
3. Tapestrix：第二节介绍 Tapestrix 的段落之后，替换旧图 4。

原稿标题、段落和次序保持不变。全文仍为六张正文图，加主视觉、开头横幅和结尾卡共九张。

## 参考案例的读取边界

本轮再次尝试打开用户提供的两篇微信文章，仍无法读取。因此无法确认这两篇文章是否有技术架构图、具体张数或插图位置。此前可见的 BioTender 分子递送画面是机制示意，不能据此推断新文章的系统架构。

## 设计与文件

白底、黑灰文字、品牌晨蓝强调；Noto Serif SC 标题、Noto Sans SC 正文、DM Mono 编号。延续网站字体体系。PNG 宽 1800 像素；SVG 文字、容器、箭头可编辑，另附文字转曲 SVG。总体图底部的 ImageGen 线稿是嵌入位图；两张技术流程图为矢量绘制。

BP 中的性能数字、竞品排名与“全球领先”等表述没有放入重绘图。BP 是此处的架构来源，不等同于代码或现场部署的独立验证。
"""
    if OUT.name=="architecture-editorial-v3":
        notes="""# 版画流程图 · 2026-10-20

基于 FathomPeak_BP_9.15.pptx 第 14、15、17、20–23 页。来源哈希见 sources.json；逐模块详情见 ../architecture-bp-v2/。

三张文章配图采用 Every 启发的版画线稿与蓝紫拼贴，把复杂架构归纳为三个阅读步骤。整体图保留前店、协同调度与后厂；NetWeaver 保留任务画像、四类联合约束与节点执行；Tapestrix 保留请求、运行时控制器及多 GPU 并行／单 GPU 共享两种执行方式。灰色虚线表示运行信息反馈。箭头表示功能关系，不表示实测接口拓扑，设备插画不代表真实产品外形或数量。

网站字体：中文标题 Noto Serif SC、正文 Noto Sans SC；英文标识 DM Mono。白底、黑灰文字和少量品牌蓝紫。图形底图为 ImageGen 位图，中文字、流程箭头为可编辑 SVG；同时交付转曲 SVG 与 PNG。文本可编辑不等于插画全矢量。

直接生成文字的英文对照图仅用于观察风格；其主要标签正确，但电脑内部含细小伪 UI 字符，因此不用于正式正文。正式版使用确定性字体排版。提示词保存在 generation-prompts.json。

开头只保留横幅中的品牌信息；独立主视觉采用无字场景。原文与六张正文图顺序保持不变。两篇微信案例未成功读取，未声称确认其配图数量。技术来源是 BP，未据此宣称部署或性能验证。
"""
    (OUT/"BP架构阅读与配图依据.md").write_text(notes)
    labels=["整体架构：前店后厂与三个智能体","NetWeaver：跨节点联合调度","Tapestrix：模型请求到 GPU 执行"]
    cards=""
    for i,((name,_),label) in enumerate(zip(items,labels),1):
        cards+=f'<section id="figure-{i}"><h2>{label}</h2><a href="{name}.png"><img src="{name}.png" alt="{label}" width="1800"></a><p><a href="{name}.png" download>高清 PNG</a> · <a href="{name}.svg" download>可编辑 SVG</a> · <a href="{name}_outlined.svg" download>转曲 SVG</a></p></section>'
    page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>沐仞科技 · BP 技术架构图</title><style>
@font-face{{font-family:NotoSans;src:url(assets/fonts/Noto-sans-SC.ttf)}}@font-face{{font-family:NotoSerif;src:url(assets/fonts/Noto-serif-SC.ttf)}}body{{margin:0;color:#212021;background:#fff;font:16px/1.85 NotoSans,sans-serif}}main{{max-width:1080px;margin:auto;padding:42px 24px}}h1,h2{{font-family:NotoSerif,serif;font-weight:400;line-height:1.5}}h1{{font-size:34px}}h2{{font-size:26px}}a{{color:#2F63B8;text-underline-offset:4px}}nav{{display:flex;flex-wrap:wrap;gap:24px}}section{{margin:60px 0}}img{{display:block;width:100%;height:auto;border:1px solid #e4e6e9}}.note{{color:#60636a;font-size:14px}}@media(max-width:600px){{main{{padding:24px 16px}}h1{{font-size:28px}}h2{{font-size:23px}}}}
</style></head><body><main><p>FATHOMPEAK / BP ARCHITECTURE / 2026.10.20</p><h1>把 BP 中的技术，画进文章。</h1><p>从整体架构，到跨节点调度，再到 GPU 执行。三张图均依据公司 BP 重绘。</p><nav><a href="../#reading">查看更新后的完整文章</a><a href="fathompeak-bp-architecture-20261020.zip" download>下载三张架构图</a><a href="BP架构阅读与配图依据.md">BP 页码与重绘说明</a></nav><p class="note">两篇微信参考文章仍读取受限，未确认其配图数量。架构依据来自 BP 第 14、15、17、20–23 页；蓝色箭头表示流程或功能关系，灰色虚线表示反馈。</p>{cards}<p class="note">SVG 保留可编辑文字和箭头；整体图底部线稿为 ImageGen 位图。性能数字与排名未纳入本次图稿。</p></main></body></html>'''
    if OUT.name=="architecture-editorial-v3":
        page=page.replace("把 BP 中的技术，画进文章。","让技术关系，融入文章的视觉语言。")
        page=page.replace("两篇微信参考文章仍读取受限，未确认其配图数量。架构依据来自 BP 第 14、15、17、20–23 页；蓝色箭头表示流程或功能关系，灰色虚线表示反馈。","版画线稿与品牌蓝紫拼贴；依据 BP 归纳为三个步骤。蓝色箭头表示功能关系，灰色虚线表示运行反馈。")
        page=page.replace("SVG 保留可编辑文字和箭头；整体图底部线稿为 ImageGen 位图。性能数字与排名未纳入本次图稿。","SVG 的中文标注与箭头可编辑，版画插图是嵌入位图。中文沿用网站 Noto Serif SC 与 Noto Sans SC。")
        page=page.replace("</main>",'<p><a href="../architecture-bp-v2/">查看 BP 详细架构版</a> · <a href="assets/direct-text-comparison.png">英文直出风格对照（非正文用图）</a></p></main>')
    (OUT/"index.html").write_text(page)
    with zipfile.ZipFile(OUT/"fathompeak-bp-architecture-20261020.zip","w",zipfile.ZIP_DEFLATED) as z:
        for p in OUT.rglob("*"):
            if p.is_file() and p.suffix!=".zip":z.write(p,p.relative_to(OUT))


def integrate_article():
    """Replace three explanatory illustrations; keep all original prose exact."""
    from lxml import html as lh
    import re
    manifest=json.loads((ARTICLE/"配图清单.json").read_text())
    new=[
        (2,"算电协同整体架构","01_算电协同整体架构","围绕这一方向，我们推进算电协同的“前店后厂”方案，","图 2｜依据 BP 第 14、20–23 页重绘：前店后厂、三个智能体与运行反馈。箭头表示功能关系。"),
        (3,"NetWeaver联合调度架构","02_NetWeaver联合调度架构","在这个基础上，我们还构建了一套以分布式通信为基础的网络调度架构。","图 3｜依据 BP 第 17 页重绘：NetWeaver 的任务画像、TransElect 联合调度、执行与反馈。"),
        (4,"Tapestrix运行时调度架构","03_Tapestrix运行时调度架构","在计算侧，Tapestrix 首先处理模型与设备之间的映射。","图 4｜依据 BP 第 15 页重绘：Tapestrix 从请求、性能图谱与运行时控制器，到多卡并行和单卡共享。"),
    ]
    if article_source().name.startswith("正文_用户修订稿"):
        # The revised manuscript introduces Tapestrix before NetWeaver.
        new=[new[0],(3,new[2][1],new[2][2],new[2][3],new[2][4].replace("图 4","图 3")),
             (4,new[1][1],new[1][2],new[1][3],new[1][4].replace("图 3","图 4"))]
        anchors=revised_anchors()
        new=[(i,title,stem,anchors[i],caption) for i,title,stem,_,caption in new]
        for f in manifest["figures"]:f["after_paragraph_start"]=anchors[f["index"]]
    for index,title,stem,anchor,caption in new:
        manifest["figures"][index-1]={"index":index,"title":title,"file":OUT.name+"/"+stem,"after_paragraph_start":anchor,"caption":caption}
    manifest["architecture_source"]=OUT.name+"/sources.json"
    root=lh.fromstring((ARTICLE/"index.html").read_text())
    article=root.xpath('//article')[0]
    before=[e.text_content() for e in root.xpath('//*[@data-source]')]
    for f in article.xpath('./figure'):article.remove(f)
    def figure(f,gallery=False):
        stem=f["file"];caption=f["caption"] if not gallery else f'{f["index"]:02} {f["title"]}'
        tail=f'<p class="downloads"><a href="{stem}.png" download>PNG</a> · <a href="{stem}.svg" download>可编辑 SVG</a> · <a href="{stem}_outlined.svg" download>转曲 SVG</a></p>' if gallery else ''
        return lh.fromstring(f'<figure><a href="{stem}.png" target="_blank"><img src="{stem}.png" alt="{f["title"]}" loading="lazy"></a><figcaption>{caption}</figcaption>{tail}</figure>')
    for f in manifest["figures"]:
        matches=[p for p in article.xpath('./p[@data-source]') if p.text_content().startswith(f["after_paragraph_start"])]
        assert len(matches)==1,(f["title"],len(matches))
        matches[0].addnext(figure(f))
    grid=root.xpath('//div[@class="grid"]')[0]
    for e in list(grid):grid.remove(e)
    for f in manifest["figures"]:grid.append(figure(f,True))
    nav=root.xpath('//header/nav')[0]
    for old in nav.xpath('./a[contains(@href,"architecture-")]'):nav.remove(old)
    nav.append(lh.fromstring(f'<a href="{OUT.name}/">版画流程图与 BP 来源</a>'))
    root.xpath('//header/h1')[0].text="从主视觉，到文章里的技术叙事。"
    root.xpath('//header/p[@class="status"]')[0].text="正文按用户提供版本保留。开头横幅承载品牌信息，独立主视觉呈现场景；三张技术图使用版画线稿、蓝紫拼贴与可编辑中文标注。全文共六张正文图，加主视觉、横幅和结尾卡共九张。"
    after=[e.text_content() for e in root.xpath('//*[@data-source]')]
    assert before==after,"Article prose changed"
    refine_article_typography(root)
    (ARTICLE/"index.html").write_text('<!doctype html>\n'+lh.tostring(root,encoding="unicode",method="html"))
    original=article_source().read_text()
    manifest["source_file"]=article_source().name
    assert hashlib.sha256(original.encode()).hexdigest()==manifest["original_sha256"]
    blocks=original.strip().split("\n\n");md=[blocks[0],"![品牌横幅](assets/masthead.png)","![文章主视觉](00_文章主视觉_从绿电到词元供给.png)"];order=[]
    for block in blocks[1:]:
        if block.startswith("## | 相关资源获取"):break
        for p in root.xpath('//article/p[@data-source="paragraph"]'):
            if p.text_content()==block and p.find("strong") is not None:
                strong=p.find("strong")
                block=(p.text or "")+"**"+strong.text+"**"+(strong.tail or "")
                break
        md.append(block)
        for f in manifest["figures"]:
            if block.replace("**","").startswith(f["after_paragraph_start"]):
                md.append(f'![{f["caption"]}]({f["file"]}.png)');order.append(f["index"])
    assert order==[1,2,3,4,5,6],order
    md.append("**相关资源获取**\n\n[模型与服务](https://www.fathompeak.cn/#models) · [API 接入指南](https://www.fathompeak.cn/#guides) · [电站合作](https://www.fathompeak.cn/#network)")
    md.append("**更多信息**\n\n官方网址｜[www.fathompeak.cn](https://www.fathompeak.cn/)\n\n微信咨询｜扫码关注下方「沐仞科技」公众号\n\n商务合作｜[fathompeak@163.com](mailto:fathompeak@163.com)")
    md.append("![品牌结尾卡](assets/closing.png)")
    (ARTICLE/"正文_含配图位置.md").write_text("\n\n".join(md)+"\n")
    (ARTICLE/"配图清单.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    guide=ARTICLE/"配图方案与参考阅读.md"
    content=guide.read_text(); marker="\n## BP 架构更新 · 2026-10-20\n"
    content=content.split(marker)[0]+marker+f"\n现用图 2、3、4 已分别替换为整体架构、NetWeaver 和 Tapestrix；具体页码与关系解释见 [BP 架构依据]({OUT.name}/BP架构阅读与配图依据.md)。此前的概念图方案保留作设计过程记录，现用顺序以配图清单.json 为准。\n"
    guide.write_text(content)
    # Package only active article assets and the architecture set, preserving old files in Git.
    active={"00_文章主视觉_从绿电到词元供给"}|{f["file"] for f in manifest["figures"]}
    with zipfile.ZipFile(ARTICLE/"fathompeak-article-20261020.zip","w",zipfile.ZIP_DEFLATED) as z:
        for p in ARTICLE.rglob("*"):
            if not p.is_file() or p.suffix==".zip":continue
            rel=p.relative_to(ARTICLE)
            if rel.parts[0].startswith("architecture-") and rel.parts[0]!=OUT.name:continue
            if rel.parts[0] in {"assets",OUT.name} or p.suffix in {".html",".md",".json"} or str(rel.with_suffix("")).removesuffix("_outlined") in active:
                z.write(p,rel)
    print("Article updated: six inline figures, exact prose preserved.")


def main():
    try:
        OUT.mkdir(parents=True,exist_ok=True)
        import sys
        if "--editorial" in sys.argv:select_editorial()
        items=editorial_diagrams() if OUT.name=="architecture-editorial-v3" else diagrams()
        prepare_fonts()
        for name,svg in items:save(name,svg)
        publish_page(items)
        integrate_article()
        print("Rendered three BP-grounded architecture diagrams.")
    except Exception as exc:
        raise SystemExit(f"Architecture build failed: {exc}") from exc


if __name__=="__main__":main()
