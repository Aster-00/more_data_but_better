"""Self-contained HTML view of a topic list: 2D map, similarity heatmap with the cluster tree, unnamed-cluster table.

Input: results/quality/topics/<name>/analysis.json and layout.json (scripts/topics/analyze_topic_clusters.py).
Output: results/quality/topics/<name>/clusters.html (open locally in a browser; no tweets, cluster-level data only).

Usage:
  python scripts/topics/plot_topic_clusters.py --dir results/quality/topics/universal_clean_k50_seed0
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# Topics whose clusters are mostly reviews (colour group 1); the rest are tweets and comments (group 2).
REVIEW_TOPICS = {"Books and novels", "Hotels and stays", "Restaurants and food", "Products and shopping",
                 "Places, malls and attractions", "Apps, phones and technology", "Films, TV, music and celebrities"}

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Topic Cluster Map</title>
<style>
:root{color-scheme:light;--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--grid:#e6e5e1;
--s1:#2a78d6;--s2:#eb6834;--neutral:#a3a29c;--lo:#eef4fc;--hi:#0d3b7a;--ring:#0b0b0b}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--bg:#1a1a19;--ink:#f0efec;
--ink2:#c3c2b7;--muted:#8f8e86;--grid:#33332f;--s1:#3987e5;--s2:#d95926;--neutral:#6c6b65;--lo:#1f2a38;--hi:#9cc3f5;--ring:#f0efec}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#8f8e86;--grid:#33332f;
--s1:#3987e5;--s2:#d95926;--neutral:#6c6b65;--lo:#1f2a38;--hi:#9cc3f5;--ring:#f0efec}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,sans-serif}
main{max-width:1180px;margin:0 auto;padding:16px}
h1{font-size:20px;margin:4px 0 2px}h2{font-size:16px;margin:28px 0 4px}p.sub{color:var(--ink2);margin:0 0 10px;max-width:880px}
.legend{display:flex;gap:16px;flex-wrap:wrap;color:var(--ink2);font-size:13px;margin:6px 0}
.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px}
.card{border:1px solid var(--grid);border-radius:8px;padding:8px;overflow:auto}
svg text{fill:var(--ink2);font-size:10px}
#tip{position:fixed;pointer-events:none;background:var(--bg);color:var(--ink);border:1px solid var(--grid);border-radius:6px;
padding:6px 8px;font-size:12px;box-shadow:0 2px 8px #0003;display:none;max-width:320px;z-index:9}
table{border-collapse:collapse;font-size:13px;width:100%}th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{color:var(--ink2);font-weight:600}td.n{text-align:right;font-variant-numeric:tabular-nums}
ul.k{max-width:880px;padding-left:18px}ul.k li{margin:3px 0}
</style></head><body><main>
<h1>Topic Cluster Map</h1>
<p class="sub">__SUBTITLE__</p>
<h2>Key findings</h2><ul class="k">__FINDINGS__</ul>

<h2>Map of texts (t-SNE)</h2>
<p class="sub">__PER__ texts per cluster, placed by t-SNE on their E5 embeddings (cosine). Labels sit at each cluster's mean position. Nearby points mean similar texts; distances between far-apart groups are not meaningful in t-SNE. Hover a point for its cluster.</p>
<div class="legend"><span><i style="background:var(--s1)"></i>Review topics</span><span><i style="background:var(--s2)"></i>Tweet and comment topics</span><span><i style="background:var(--neutral)"></i>Not named</span></div>
<div class="card"><svg id="map" viewBox="0 0 1100 760" width="100%" role="img" aria-label="t-SNE map of cluster samples"></svg></div>

<h2>Centroid similarity, ordered by the cluster tree</h2>
<p class="sub">Cosine similarity between the 50 cluster centres (darker = closer), rows and columns in the order of an average-linkage tree (drawn on top). E5 similarities are all high (the off-diagonal range is __RANGE__), so read the shades as relative. A dot marks a pair of clusters with the same topic. Hover a cell for the pair.</p>
<div class="card"><svg id="heat" viewBox="0 0 1100 1180" width="100%" role="img" aria-label="similarity heatmap"></svg></div>

<h2>Unnamed clusters: nearest named topics</h2>
<p class="sub">"Texts closer to a named centre" = share of the cluster's texts whose best named centre is closer than their own centre. "Texts would go to" = where its texts land if each is moved to the nearest named centre.</p>
<div class="card"><table id="un"><thead><tr><th>Cluster</th><th>What it is</th><th class="n">Texts</th><th>Nearest named clusters (centroid similarity)</th><th class="n">Texts closer to a named centre</th><th>Texts would go to</th></tr></thead><tbody></tbody></table></div>
<div id="tip"></div>
</main>
<script>
const A=__ANALYSIS__, L=__LAYOUT__, REV=new Set(__REVIEW__);
const cl={};A.clusters.forEach(c=>cl[c.cluster]=c);
const grp=c=>cl[c].topic==="Not named"?"var(--neutral)":(REV.has(cl[c].topic)?"var(--s1)":"var(--s2)");
const NS="http://www.w3.org/2000/svg",el=(t,a,p)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);p&&p.appendChild(e);return e};
const tip=document.getElementById("tip");
function show(ev,html){tip.innerHTML=html;tip.style.display="block";const x=Math.min(ev.clientX+14,innerWidth-330);tip.style.left=x+"px";tip.style.top=(ev.clientY+14)+"px"}
function hide(){tip.style.display="none"}
const pct=v=>(v*100).toFixed(0)+"%";
function info(c){const x=cl[c];return `<b>C${c} · ${x.topic}</b><br>${x.size.toLocaleString()} texts<br>Top datasets: ${x.top_datasets.map(d=>d[0]+" "+pct(d[1])).join(", ")}<br>Nearest: ${x.nearest.map(n=>"C"+n[0]+" "+cl[n[0]].topic+" ("+n[1].toFixed(3)+")").join("; ")}`}
// Map
(()=>{const s=document.getElementById("map"),W=1100,H=760,m=20;const xs=L.points.map(p=>p.x),ys=L.points.map(p=>p.y);
const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
const X=v=>m+(v-x0)/(x1-x0)*(W-2*m),Y=v=>H-m-(v-y0)/(y1-y0)*(H-2*m);
const g=el("g",{},s);L.points.forEach(p=>{const d=el("circle",{cx:X(p.x),cy:Y(p.y),r:2.2,fill:grp(p.c),"fill-opacity":.55},g);
d.addEventListener("mousemove",e=>show(e,info(p.c)));d.addEventListener("mouseleave",hide)});
const cen={};L.points.forEach(p=>{(cen[p.c]=cen[p.c]||[0,0,0]);cen[p.c][0]+=p.x;cen[p.c][1]+=p.y;cen[p.c][2]++});
for(const c in cen){const [sx,sy,n]=cen[c];const t=el("text",{x:X(sx/n),y:Y(sy/n),"text-anchor":"middle","font-size":11,
style:"fill:var(--ink);paint-order:stroke;stroke:var(--bg);stroke-width:3px;font-weight:600"},s);t.textContent="C"+c+(cl[c].topic==="Not named"?"":" "+cl[c].topic.split(/[ ,]/)[0]);
t.addEventListener("mousemove",e=>show(e,info(+c)));t.addEventListener("mouseleave",hide)}})();
// Heatmap + dendrogram
(()=>{const s=document.getElementById("heat"),o=A.order,k=o.length,lab=230,top=150,cell=(1100-lab-10)/k;
const off=[];A.similarity.forEach((r,i)=>r.forEach((v,j)=>{if(i!==j)off.push(v)}));const lo=Math.min(...off),hi=Math.max(...off);
const cs=getComputedStyle(document.documentElement);const hex=h=>{h=h.trim().replace("#","");return [0,2,4].map(i=>parseInt(h.slice(i,i+2),16))};
function col(v){const a=hex(cs.getPropertyValue("--lo")),b=hex(cs.getPropertyValue("--hi"));const t=Math.max(0,Math.min(1,(v-lo)/(hi-lo)));return `rgb(${a.map((x,i)=>Math.round(x+(b[i]-x)*t)).join(",")})`}
// dendrogram: scipy leaf positions are 5,15,25,...; heights are 1 - cosine
const dmax=Math.max(...A.dendrogram.dcoord.flat());const DX=v=>lab+(v-5)/10*cell+cell/2,DY=v=>top-8-v/dmax*(top-20);
A.dendrogram.icoord.forEach((ic,i)=>{const dc=A.dendrogram.dcoord[i];el("path",{d:`M${DX(ic[0])},${DY(dc[0])}V${DY(dc[1])}H${DX(ic[2])}V${DY(dc[3])}`,fill:"none",stroke:"var(--muted)","stroke-width":1},s)});
const rects=[];o.forEach((ci,i)=>{const t=el("text",{x:lab-6,y:top+i*cell+cell*.72,"text-anchor":"end"},s);t.textContent=`C${ci} ${cl[ci].topic}`;
t.style.fill=cl[ci].topic==="Not named"?"var(--muted)":"var(--ink2)";
o.forEach((cj,j)=>{const v=A.similarity[ci][cj];const r=el("rect",{x:lab+j*cell,y:top+i*cell,width:cell-.5,height:cell-.5,fill:i===j?"var(--grid)":col(v)},s);
if(i!==j&&cl[ci].topic===cl[cj].topic&&cl[ci].topic!=="Not named")el("circle",{cx:lab+j*cell+cell/2,cy:top+i*cell+cell/2,r:1.6,fill:"var(--bg)"},s);
r.addEventListener("mousemove",e=>show(e,`<b>C${ci} ${cl[ci].topic}</b><br><b>C${cj} ${cl[cj].topic}</b><br>similarity ${v.toFixed(3)}`));r.addEventListener("mouseleave",hide)})});
const lg=el("g",{},s),ly=top+k*cell+18;for(let i=0;i<=20;i++)el("rect",{x:lab+i*12,y:ly,width:12,height:10,fill:col(lo+(hi-lo)*i/20)},lg);
el("text",{x:lab,y:ly+24},lg).textContent=lo.toFixed(3);el("text",{x:lab+252,y:ly+24,"text-anchor":"end"},lg).textContent=hi.toFixed(3);
el("text",{x:lab+262,y:ly+9},lg).textContent="cosine similarity of cluster centres"})();
// Table
(()=>{const tb=document.querySelector("#un tbody");Object.entries(A.unnamed).forEach(([c,u])=>{const tr=document.createElement("tr");
tr.innerHTML=`<td>C${c}</td><td>${u.why}</td><td class="n">${u.size.toLocaleString()}</td><td>${u.nearest_named.map(n=>"C"+n.cluster+" "+n.topic+" ("+n.sim.toFixed(3)+")").join("<br>")}</td><td class="n">${pct(u.share_closer_to_named_than_own)}</td><td>${Object.entries(u.texts_to_topic).map(([t,v])=>t+" "+pct(v)).join("<br>")}</td>`;tb.appendChild(tr)})})();
</script></body></html>
"""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--dir", required=True)
    args = p.parse_args()
    d = Path(args.dir)
    a = json.loads((d / "analysis.json").read_text(encoding="utf-8"))
    lay = json.loads((d / "layout.json").read_text(encoding="utf-8"))
    off = [v for i, r in enumerate(a["similarity"]) for j, v in enumerate(r) if i != j]
    ranks = a["nearest_same_topic_rank"]
    findings = [
        f"Clusters of the same topic are closer than clusters of different topics: mean centroid similarity "
        f"{a['same_topic_sim']['mean']:.3f} vs {a['different_topic_sim']['mean']:.3f}.",
        f"For {sum(r == 1 for r in ranks.values())} of {len(ranks)} clusters in a multi-cluster topic, the nearest cluster "
        f"overall has the same topic. The exceptions are mostly tweet topics (politics, love, films and TV, greetings).",
        f"Closeness follows the source as well as the subject: centroid similarity correlates with dataset-mix similarity "
        f"(r = {a['corr_centroid_sim_vs_dataset_mix_sim']:.2f}). Reviews and COVID tweets form separate blocks; tweets and "
        f"comments form one dense block where topics sit close together.",
        "No unnamed cluster has its texts closer to a named centre than to its own centre (0–1% each), so moving unnamed "
        "clusters into named topics is not supported by the embeddings; their nearest named neighbours are tweet topics "
        "of the same style (short, emoji, decorated).",
    ]
    html = (PAGE.replace("__SUBTITLE__", f"Frozen E5 topic list <code>{a['topic_list']}</code>: {a['k']} clusters, names from "
                         f"<code>{a['names_config']}</code>. Generated by <code>scripts/topics/plot_topic_clusters.py</code>.")
            .replace("__FINDINGS__", "".join(f"<li>{f}</li>" for f in findings))
            .replace("__PER__", str(lay["per_cluster"]))
            .replace("__RANGE__", f"{min(off):.3f} to {max(off):.3f}")
            .replace("__ANALYSIS__", json.dumps(a, ensure_ascii=False))
            .replace("__LAYOUT__", json.dumps(lay))
            .replace("__REVIEW__", json.dumps(sorted(REVIEW_TOPICS))))
    (d / "clusters.html").write_text(html, encoding="utf-8")
    print(f"written to {d / 'clusters.html'}")


if __name__ == "__main__":
    main()
