#!/usr/bin/env python3
"""Build the distributable knowledge maps from assets/knowledge-tree.json (stdlib only)."""
from __future__ import annotations

import html
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DOCS = ROOT / "docs"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif"
INK, MUTED, BG, TEAL, BLUE = "#183139", "#546c73", "#f5f7f3", "#176d64", "#375f96"


def e(value):
    return html.escape(str(value), quote=True)


def svg_start(width, height, title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{e(title)}</title><desc id="desc">{e(desc)}</desc>',
            f'<rect width="{width}" height="{height}" fill="{BG}"/>',
            f'<g font-family="{FONT}" fill="{INK}">']


def label(x, y, text, size=22, color=INK, weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{e(text)}</text>'


def wrap(text, max_width):
    lines, line, width = [], "", 0
    for char in text:
        advance = 1 if ord(char) > 255 else .56
        if line and width + advance > max_width:
            lines.append(line.strip())
            line, width = "", 0
        line += char
        width += advance
    if line:
        lines.append(line.strip())
    return lines


def full_map(tree):
    width, height = 1900, 2580
    parts = svg_start(width, height, "外贸网站技术选型 · 完整二叉知识树", "8 个选型层面，32 组知识点，63 个节点；每个非叶节点恰有两个子节点。")
    parts += [label(52, 68, "外贸网站技术选型", 42, weight=700),
              label(52, 110, "8 个选型层面 · 32 组知识点 · 每个分支二分", 25, TEAL, 600),
              label(52, 150, "这是知识分类图。一个项目会组合多个分支；具体技术选择请结合业务、预算与维护条件。", 21, MUTED)]
    xs, ws = [45, 304, 568, 833, 1100, 1380], [220, 225, 225, 230, 240, 470]
    ys, depths, module_of = {}, {}, {}
    leaves, modules = [], []

    def place(node, depth, module=None):
        depths[node["id"]] = depth
        if depth == 3:
            modules.append(node)
            module = len(modules)
        module_of[node["id"]] = module
        if "children" in node:
            values = [place(child, depth + 1, module) for child in node["children"]]
            y = sum(values) / 2
        else:
            y = 220 + len(leaves) * 72
            leaves.append(node)
        ys[node["id"]] = y
        return y

    place(tree, 0)

    def edges(node):
        if "children" not in node:
            return
        depth, y = depths[node["id"]], ys[node["id"]]
        for child in node["children"]:
            cy = ys[child["id"]]
            x1, x2 = xs[depth] + ws[depth], xs[depth+1]
            mid = (x1+x2)/2
            parts.append(f'<path d="M{x1} {y} H{mid} V{cy} H{x2}" fill="none" stroke="#b6c7c6" stroke-width="2"/>')
            edges(child)

    edges(tree)

    def boxes(node):
        depth, y = depths[node["id"]], ys[node["id"]]
        x, w = xs[depth], ws[depth]
        module = module_of[node["id"]]
        accent = TEAL if not module or module % 2 else BLUE
        is_leaf = "children" not in node
        title = node["name"]
        if is_leaf:
            title = f'{node["point"]:02d}  {title}'
        lines = wrap(title, 22 if is_leaf else 9)
        size = 20 if is_leaf else 22
        h = max(54, len(lines)*27 + 18)
        fill = "#ffffff"
        stroke = accent if depth == 3 else "#cedbd6"
        href = f'#point-{node["point"]:02d}' if is_leaf else f'#module-{module}' if depth == 3 else "#knowledge"
        parts.append(f'<g data-target="{href}" data-node="{node["id"]}"><title>{e(node["name"])}</title><rect x="{x}" y="{y-h/2}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="{2 if depth == 3 else 1}"/>')
        if is_leaf:
            parts.append(f'<rect x="{x}" y="{y-h/2+10}" width="4" height="{h-20}" rx="2" fill="{accent}"/>')
        for i, line in enumerate(lines):
            parts.append(label(x+15, y-(len(lines)-1)*13.5+7+i*27, line, size, accent if depth == 3 else INK, 600 if depth in (0,3) else 400))
        parts.append('</g>')
        for child in node.get("children", []):
            boxes(child)

    boxes(tree)
    parts += [label(52, 2517, "阅读方法：先看 01—08 模块，再沿分支学习；SSR / SSG / ISR / CSR 可以按页面组合。", 22, MUTED),
              label(52, 2554, "b2b-website-strategy  /  学习图 + 已有站诊断 + 新站访谈选型", 20, TEAL), '</g></svg>']
    return "\n".join(parts)


def overview(modules):
    parts = svg_start(1200, 700, "外贸网站技术选型 · 八层总览", "建设方案与运行获客二分，覆盖八个选型模块。完整 32 组知识点见知识树。")
    parts += [label(56, 67, "外贸网站技术选型", 43, weight=700),
              label(56, 108, "用业务需求选技术，把网站接到询盘与运营。", 24, MUTED)]
    for side, title in enumerate(["A  网站怎么建", "B  网站怎么运行与获客"]):
        x = 56 + side*568
        color = TEAL if not side else BLUE
        parts += [f'<path d="M{x+20} 203 V596" stroke="{color}" stroke-width="2" fill="none"/>',
                  f'<rect x="{x}" y="150" width="520" height="54" rx="8" fill="{color}"/>', label(x+20, 186, title, 26, "#ffffff", 600)]
        for i, module in enumerate(modules[side*4:side*4+4]):
            y = 239 + i*102
            parts += [f'<path d="M{x+20} {y+18} H{x+45}" stroke="{color}" stroke-width="2"/>',
                      label(x+56, y+26, module["name"], 26, weight=600)]
            leaves = [leaf for group in module["children"] for leaf in group["children"]]
            # Short, readable clues; the full map contains exact titles and the HTML carries explanations.
            clues = ["目标 / 平台 / 开发路线", "产品模型 / 编辑 / 系统集成", "页面结构 / 交互 / 开发框架", "SSG / ISR / SSR / CSR", "源站 / CDN / 性能", "索引 / 内容 / 语言 / 站点", "表单 / 邮件 / CRM / 归因", "权限 / 发布 / 备份 / 总成本"]
            parts.append(label(x+56, y+62, clues[side*4+i], 22, MUTED))
    parts += [label(56, 661, "8 个选型层面 × 每层 4 组知识点 = 32 组  ·  完整二叉树与逐点解释另附", 23, TEAL), '</g></svg>']
    return "\n".join(parts)


def hero():
    parts = svg_start(1200, 360, "B2B Website Strategy — 外贸网站选型与诊断 Skill", "输入已有网址做公开网页诊断，或通过业务访谈规划新站；交付技术、SEO、配套服务与 CDN 规则。")
    parts += [label(56, 56, "B2B WEBSITE STRATEGY", 23, TEAL, 600),
              label(56, 119, "先看业务，再选技术。", 52, weight=700),
              label(56, 167, "外贸网站诊断 · 新站选型 · SEO 与询盘规划", 26, MUTED),
              f'<path d="M76 207 V265 M76 229 H120 M76 265 H120" stroke="{TEAL}" stroke-width="2" fill="none"/>',
              label(136, 236, "已有网站 → 实际看站、对标竞品、排改进顺序", 25),
              label(136, 273, "从零建站 → 少量业务问题、主方案与备选", 25),
              label(56, 329, "8 个选型层面  /  32 组知识点  /  2 种使用入口", 23, TEAL, 600), '</g></svg>']
    return "\n".join(parts)


def learning_html(modules):
    result = []
    for i, module in enumerate(modules, 1):
        result.append(f'<section class="module" id="module-{i}"><h3>{e(module["name"])}</h3>')
        for group in module["children"]:
            result.append(f'<div class="pair"><h4>{e(group["name"])}</h4><div class="pair-body">')
            for leaf in group["children"]:
                search = " ".join(str(leaf.get(k, "")) for k in ("name", "meaning", "analogy", "example", "choice"))
                result.append(f'<details class="point" id="point-{leaf["point"]:02d}" data-search="{e(search)}"><summary><span class="point-no">{leaf["point"]:02d}</span>{e(leaf["name"])}</summary><div class="point-body"><dl>')
                for key, title in [("meaning", "是什么"), ("analogy", "打个比方"), ("example", "外贸例子"), ("choice", "选型要点")]:
                    result.append(f'<dt>{title}</dt><dd>{e(leaf[key])}</dd>')
                result.append('</dl>')
                if leaf.get("source"):
                    result.append(f'<a class="source" href="{e(leaf["source"][1])}" target="_blank" rel="noopener noreferrer">官方资料：{e(leaf["source"][0])} ↗</a>')
                result.append('</div></details>')
            result.append('</div></div>')
        result.append('</section>')
    return "\n".join(result)


def web_page(modules, svg):
    outline = "".join(f'<a href="#module-{i}">{e(m["name"])}</a>' for i,m in enumerate(modules,1))
    learning = learning_html(modules)
    return '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="外贸网站技术选型二叉知识树：8 个选型层面、32 组知识点，包含类比、外贸例子与选型要点。"><title>外贸网站技术选型图 · 8 层 32 组知识点</title>
<style>
:root{--ink:#183139;--muted:#546c73;--teal:#176d64;--blue:#375f96;--line:#d5dfd8;--bg:#f5f7f3}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.75}a{color:var(--teal);text-underline-offset:4px}button,input{font:inherit}button{cursor:pointer;border:1px solid var(--line);border-radius:8px;background:white;color:var(--ink);padding:9px 14px}button:hover{border-color:var(--teal)}button:focus-visible,a:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #74b9a4;outline-offset:3px}.wrap{max-width:1280px;margin:auto;padding:0 32px}header{border-bottom:1px solid var(--line)}header .wrap{display:flex;align-items:center;justify-content:space-between;gap:20px;padding-top:17px;padding-bottom:17px}.brand{font-size:14px;font-weight:700;letter-spacing:.12em}header a{font-size:14px}.hero{padding:60px 0 30px;display:flex;justify-content:space-between;gap:30px}.eyebrow{color:var(--teal);font-size:13px;letter-spacing:.12em;font-weight:700}h1{font-size:clamp(30px,4.5vw,54px);letter-spacing:-.035em;line-height:1.25;margin:13px 0 20px}.hero p{max-width:760px;color:var(--muted);font-size:17px;margin:0}.counts{display:flex;gap:25px;align-items:flex-start;padding-top:25px;white-space:nowrap}.counts strong{font-size:44px;display:block;line-height:1.2}.counts span{font-size:13px;color:var(--muted)}.note{border-left:3px solid var(--teal);padding:12px 18px;background:#eaf1e9;margin:10px 0 25px;font-size:14px}.actions{display:flex;gap:12px;flex-wrap:wrap}.actions a{display:inline-block;border:1px solid var(--line);border-radius:8px;padding:8px 15px;background:white;text-decoration:none;font-size:14px}.actions .primary{color:white;background:var(--teal);border-color:var(--teal)}h2{font-size:27px;line-height:1.4;margin:40px 0 10px}.hint{font-size:14px;color:var(--muted);margin:0 0 15px}.tree-top{display:flex;align-items:center;justify-content:space-between;gap:15px}.zoom-controls{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.zoom-controls button{font-size:13px;padding:5px 11px}.zoom-controls output{min-width:42px;text-align:center;font-size:13px}.canvas{border:1px solid var(--line);border-radius:12px;overflow:auto;background:white;max-height:850px;overscroll-behavior:contain}.canvas svg{display:block;max-width:none;height:auto}.canvas a:hover rect{stroke:var(--teal);stroke-width:3}.toolbar{position:sticky;top:0;z-index:3;display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:var(--bg);border-bottom:1px solid var(--line);padding:16px 0;margin-top:10px}.toolbar input{flex:1;min-width:180px;border:1px solid var(--line);border-radius:8px;padding:10px 14px;background:white;color:var(--ink)}.toolbar button{font-size:13px}.toolbar output{color:var(--muted);font-size:13px;min-width:85px}.module-nav{display:flex;gap:7px;flex-wrap:wrap;padding:20px 0}.module-nav a{font-size:13px;text-decoration:none;border-bottom:1px solid var(--line);padding:3px 8px}.module{scroll-margin-top:100px;margin:10px 0 32px}.module h3{font-size:23px;margin:0 0 17px;color:var(--teal)}.pair{margin-bottom:16px}.pair h4{font-size:14px;font-weight:500;color:var(--muted);margin:0 0 8px}.pair-body{display:grid;grid-template-columns:1fr 1fr;gap:14px}.point{border:1px solid var(--line);border-radius:10px;background:white;scroll-margin-top:100px;align-self:start}.point summary{display:flex;gap:11px;align-items:flex-start;padding:18px;cursor:pointer;list-style:none;font-size:16px;font-weight:600;line-height:1.55}.point summary::after{content:'＋';margin-left:auto;color:var(--muted);flex-shrink:0}.point[open] summary::after{content:'−'}.point[open]{border-color:#8eafa0}.point:target{outline:2px solid var(--teal);outline-offset:2px}.point-no{font:12px/24px ui-monospace,monospace;color:var(--teal);flex-shrink:0}.point-body{padding:0 20px 20px}dl{margin:0}dt{font-size:12px;letter-spacing:.08em;color:var(--teal);font-weight:700;margin-top:12px}dd{margin:4px 0 0;font-size:14px;overflow-wrap:anywhere}.source{display:inline-block;margin-top:15px;font-size:13px}.empty{display:none;padding:30px;border:1px dashed var(--line);color:var(--muted)}footer{border-top:1px solid var(--line);padding:30px 0 42px;color:var(--muted);font-size:13px;margin-top:35px}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}[hidden]{display:none!important}@media(max-width:700px){.wrap{padding:0 18px}.hero{padding-top:32px;display:block}.hero p{font-size:15px}.counts{padding-top:20px;gap:28px}.counts strong{font-size:32px}.pair-body{grid-template-columns:1fr}.tree-top{display:block}.zoom-controls{margin:10px 0}.canvas{max-height:550px}.toolbar{gap:7px}.toolbar input{flex-basis:100%}.toolbar button{padding:8px 10px}header .wrap{padding-top:12px;padding-bottom:12px}.brand{font-size:11px;letter-spacing:.05em}h2{font-size:24px}.point summary{font-size:15px;padding:15px}.module-nav{gap:4px}.module-nav a{font-size:12px}footer{overflow-wrap:anywhere}}@media print{header,.actions,.toolbar,.zoom-controls,.module-nav,.source,footer{display:none}.canvas{max-height:none;overflow:visible;border:0}.canvas svg{width:100%!important}.pair-body{grid-template-columns:1fr}.point{break-inside:avoid}.hero{padding-top:0}.counts{display:none}body{background:white}.wrap{padding:0}h2{break-before:page}.point-body{display:block}}
</style></head><body>
<header><div class="wrap"><span class="brand">B2B WEBSITE STRATEGY</span><a href="https://github.com/Miraclemin/b2b-website-strategy" target="_blank" rel="noopener noreferrer">获取 Skill ↗</a></div></header>
<main class="wrap"><section class="hero"><div><div class="eyebrow">业务 → 技术 → 询盘 → 持续运营</div><h1>先看业务，<br>再选网站技术。</h1><p>外贸网站技术选型二叉知识树。点击知识点，学习它是什么、像什么、怎么用，以及什么时候值得选。</p></div><div class="counts"><div><strong>08</strong><span>选型层面</span></div><div><strong>32</strong><span>知识点组</span></div></div></section>
<div class="note"><strong>怎么理解“8 层”？</strong>指 8 个业务选型层面。图采用二叉分组，共 63 个节点、32 个末端知识点组；从根到叶有 5 次分叉。分支是知识分类，实际建站可以组合使用，不能机械地沿一条路二选一。</div>
<nav class="actions" aria-label="主要操作"><a class="primary" href="#knowledge">逐点学习 ↓</a><a href="../assets/technology-map.svg" download>下载完整 SVG</a><a href="../assets/technology-map.png" download>下载高清 PNG</a><a href="https://github.com/Miraclemin/b2b-website-strategy#快速开始" target="_blank" rel="noopener noreferrer">安装与用法 ↗</a></nav>
<section aria-labelledby="map-heading"><div class="tree-top"><h2 id="map-heading">完整二叉知识树</h2><div class="zoom-controls"><button id="zoom-out" aria-label="缩小知识树">−</button><output id="zoom-label">100%</output><button id="zoom-in" aria-label="放大知识树">＋</button><button id="fit">适应宽度</button><button id="actual">原尺寸</button></div></div><p class="hint">在图内横向 / 纵向滚动；点击末端知识点即可跳到详细解释。手机上建议直接使用下方“逐点学习”。</p><div class="canvas" id="canvas" tabindex="0" aria-label="可滚动和缩放的二叉知识树">''' + svg.replace('id="title"', 'id="tree-title"').replace('id="desc"', 'id="tree-desc"').replace('aria-labelledby="title desc"','aria-labelledby="tree-title tree-desc"') + '''</div></section>
<section id="knowledge"><h2>逐点学习</h2><p class="hint">每个模块包含 4 组知识点；搜索支持 SSR、WordPress、邮箱、CDN 等名称和说明内容。</p><div class="toolbar"><label class="sr-only" for="search">搜索知识点</label><input type="search" id="search" placeholder="搜索知识点、术语或业务场景…" autocomplete="off"><output id="match-count" aria-live="polite">32 / 32 组</output><button id="expand">展开当前结果</button><button id="collapse">收起解释</button><button id="print">打印 / 保存 PDF</button></div><nav class="module-nav" aria-label="八个选型模块">''' + outline + '''</nav><div class="empty" id="empty" role="status">没有找到匹配内容，试试“缓存”“产品”或“邮件”。</div>''' + learning + '''</section></main>
<footer><div class="wrap">这张图帮助理解与讨论方案，不保证排名、询盘或特定技术效果。具体插件、价格、部署支持与服务规则，请在使用时核对当前官方资料。<br><a href="https://github.com/Miraclemin/b2b-website-strategy">b2b-website-strategy</a> · 免费获取与使用说明 · 本文件可离线打开</div></footer>
<script>
(()=>{const canvas=document.getElementById('canvas'),svg=canvas.querySelector('svg'),output=document.getElementById('zoom-label');svg.querySelectorAll('g[data-target]').forEach(g=>{const a=document.createElementNS('http://www.w3.org/2000/svg','a');a.setAttribute('href',g.dataset.target);g.parentNode.insertBefore(a,g);a.append(g)});let zoom=1;function scale(v){zoom=Math.max(.18,Math.min(1.6,v));svg.style.width=(1900*zoom)+'px';output.value=Math.round(zoom*100)+'%'}function fit(){scale(canvas.clientWidth/1900)}document.getElementById('zoom-out').onclick=()=>scale(zoom-.15);document.getElementById('zoom-in').onclick=()=>scale(zoom+.15);document.getElementById('actual').onclick=()=>scale(1);document.getElementById('fit').onclick=fit;fit();
const search=document.getElementById('search'),points=[...document.querySelectorAll('.point')],modules=[...document.querySelectorAll('.module')];function filter(){const q=search.value.trim().toLocaleLowerCase();let n=0;points.forEach(p=>{p.hidden=q&&!p.dataset.search.toLocaleLowerCase().includes(q);if(!p.hidden){n++;if(q)p.open=true}});document.querySelectorAll('.pair').forEach(p=>p.hidden=![...p.querySelectorAll('.point')].some(x=>!x.hidden));modules.forEach(m=>m.hidden=![...m.querySelectorAll('.point')].some(p=>!p.hidden));document.getElementById('match-count').value=n+' / 32 组';document.getElementById('empty').style.display=n?'none':'block'}search.addEventListener('input',filter);document.getElementById('expand').onclick=()=>points.forEach(p=>{if(!p.hidden)p.open=true});document.getElementById('collapse').onclick=()=>points.forEach(p=>p.open=false);document.getElementById('print').onclick=()=>window.print();let beforePrint=[];window.addEventListener('beforeprint',()=>{beforePrint=points.map(p=>p.open);points.forEach(p=>{if(!p.hidden)p.open=true})});window.addEventListener('afterprint',()=>points.forEach((p,i)=>p.open=beforePrint[i]));
function reveal(hash){if(!/^#(?:point-\d\d|module-\d+)$/.test(hash))return;search.value='';filter();const target=document.querySelector(hash);if(target){if(target.matches('details'))target.open=true;requestAnimationFrame(()=>target.scrollIntoView({behavior:'smooth',block:'start'}))}}canvas.addEventListener('click',event=>{const a=event.target.closest('a');if(a){const hash=a.getAttribute('href');if(hash&&hash.startsWith('#')){event.preventDefault();history.replaceState(null,'',hash);reveal(hash)}}});window.addEventListener('hashchange',()=>reveal(location.hash));reveal(location.hash);
})();
</script></body></html>'''


def markdown(tree, modules):
    out = ['# 外贸网站技术选型 · 8 层 32 组知识点', '',
           '> “8 层”指八个业务选型层面。图是知识分类二叉树，不是只能沿一个分支走的互斥决策树。', '',
           '共 63 个节点，32 个末端知识点组，每个非叶节点恰有两个子节点；从根到叶有 5 次分叉。', '',
           '[交互学习图](technology-map.html) · [完整 SVG](../assets/technology-map.svg) · [高清 PNG](../assets/technology-map.png)', '',
           '## 完整二叉树', '', '```mermaid', 'flowchart LR']

    def branch(node):
        title = node["name"].replace('"', "'")
        if "point" in node:
            title = f'{node["point"]:02d} {title}'
        out.append(f'  {node["id"]}["{title}"]')
        for child in node.get("children", []):
            out.append(f'  {node["id"]} --> {child["id"]}')
            branch(child)

    branch(tree)
    out.extend(['```', '', '## 32 组知识点详解', ''])
    for module in modules:
        out.extend([f'### {module["name"]}', ''])
        for group in module["children"]:
            for leaf in group["children"]:
                out.extend([f'#### {leaf["point"]:02d} · {leaf["name"]}', ''])
                for key, title in [("meaning", "是什么"), ("analogy", "类比"), ("example", "外贸例子"), ("choice", "选型要点")]:
                    out.append(f'- **{title}**：{leaf[key]}')
                if leaf.get("source"):
                    out.append(f'- **资料入口**：[{leaf["source"][0]}]({leaf["source"][1]})；具体能力以使用时的官方资料为准。')
                out.append('')
    return '\n'.join(out)


def main():
    data = json.loads((ASSETS / 'knowledge-tree.json').read_text())
    tree = data['tree']
    modules, leaves = [], []
    def verify(node, depth=0):
        if depth == 3:
            modules.append(node)
        if 'children' in node:
            assert len(node['children']) == 2, node['name']
            for child in node['children']:
                verify(child, depth+1)
        else:
            leaves.append(node)
    verify(tree)
    assert len(modules) == 8 and len(leaves) == 32
    assert sorted(p['point'] for p in leaves) == list(range(1,33))
    DOCS.mkdir(exist_ok=True)
    (ASSETS / 'readme').mkdir(exist_ok=True)
    svg = full_map(tree)
    (ASSETS / 'technology-map.svg').write_text(svg)
    (ASSETS / 'readme' / 'overview.svg').write_text(overview(modules))
    (ASSETS / 'readme' / 'hero.svg').write_text(hero())
    (DOCS / 'technology-map.html').write_text(web_page(modules, svg))
    (DOCS / 'technology-map.md').write_text(markdown(tree, modules))
    (DOCS / 'index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=technology-map.html"><title>外贸网站技术选型图</title><a href="technology-map.html">打开外贸网站技术选型图</a></html>\n')
    print('Built: 8 modules / 32 knowledge groups / 63 binary-tree nodes')


if __name__ == '__main__':
    main()
