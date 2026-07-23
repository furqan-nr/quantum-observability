# -*- coding: utf-8 -*-
"""
Generates the two proposal flowcharts (Figure 3.1 – cart pipeline, Figure 3.2 –
research framework) as native draw.io (.drawio / mxGraph) source AND as matching
SVG + PNG, from a single spec so the editable source and the rendered image stay
in sync.  Open the .drawio files at https://app.diagrams.net to edit, then
File > Export as > PNG to regenerate the images.

Run:  python generate_diagrams.py        (needs cairosvg for PNG; SVG always written)

draw.io palette used:
  blue   fill #DAE8FC stroke #6C8EBF
  green  fill #D5E8D4 stroke #82B366
  orange fill #FFE6CC stroke #D79B00
  gray   fill #F5F5F5 stroke #666666
"""
import os, html as _html

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE=("#DAE8FC","#6C8EBF"); GREEN=("#D5E8D4","#82B366")
ORANGE=("#FFE6CC","#D79B00"); GRAY=("#F5F5F5","#666666")
DARK="#1A2A3A"; SUB="#3B475C"; GREENTX="#2E7D32"; ORANGETX="#B36B00"; BLUETX="#2A5A9E"

# ---------- a node: id, x,y,w,h, fill/stroke, and lines=[(text,size,bold,color)] ----------
# ---------- an edge: (src, dst, exit(x,y), entry(x,y)) fractions ----------

def drawio(name, W, Hh, nodes, edges):
    def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")
    cells=[]
    for n in nodes:
        parts=[]
        for (t,sz,b,col) in n["lines"]:
            if t=="": parts.append("<br>"); continue
            seg=_html.escape(t)
            if b: seg=f"<b>{seg}</b>"
            seg=f'<font color="{col}" style="font-size:{sz}px">{seg}</font>'
            parts.append(seg)
        val=esc("<br>".join(parts))
        style=(f'rounded=1;whiteSpace=wrap;html=1;fillColor={n["fill"]};strokeColor={n["stroke"]};'
               f'align=center;verticalAlign=middle;arcSize=8;fontFamily=Helvetica;spacingLeft=6;spacingRight=6;shadow=0;')
        cells.append(
          f'<mxCell id="{n["id"]}" value="{val}" style="{style}" vertex="1" parent="1">'
          f'<mxGeometry x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" as="geometry"/></mxCell>')
    for i,e in enumerate(edges):
        ex,ey=e["exit"]; nx,ny=e["entry"]
        style=(f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#5B6B86;'
               f'strokeWidth=1.5;exitX={ex};exitY={ey};exitDx=0;exitDy=0;entryX={nx};entryY={ny};entryDx=0;entryDy=0;')
        cells.append(
          f'<mxCell id="e{i}" style="{style}" edge="1" parent="1" source="{e["src"]}" target="{e["dst"]}">'
          f'<mxGeometry relative="1" as="geometry"/></mxCell>')
    body="\n        ".join(cells)
    return (f'<mxfile host="app.diagrams.net" type="device">\n'
            f'  <diagram name="{name}" id="{name.replace(" ","_")}">\n'
            f'    <mxGraphModel dx="1000" dy="700" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
            f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{W}" pageHeight="{Hh}" math="0" shadow="0">\n'
            f'      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n        {body}\n'
            f'      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')

def svg(W, Hh, nodes, edges):
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" font-family="Helvetica, Arial, sans-serif">']
    out.append(f'<rect x="0" y="0" width="{W}" height="{Hh}" fill="#ffffff"/>')
    out.append('<defs><marker id="ar" markerWidth="9" markerHeight="9" refX="6.5" refY="3" orient="auto">'
               '<path d="M0,0 L7,3 L0,6 Z" fill="#5B6B86"/></marker></defs>')
    nd={n["id"]:n for n in nodes}
    # edges first (under boxes)
    for e in edges:
        s=nd[e["src"]]; d=nd[e["dst"]]; ex,ey=e["exit"]; nx,ny=e["entry"]
        x1=s["x"]+ex*s["w"]; y1=s["y"]+ey*s["h"]; x2=d["x"]+nx*d["w"]; y2=d["y"]+ny*d["h"]
        if abs(y1-y2)>abs(x1-x2):           # mostly vertical -> orthogonal down
            ym=(y1+y2)/2
            pts=f"{x1},{y1} {x1},{ym} {x2},{ym} {x2},{y2}" if abs(x1-x2)>1 else f"{x1},{y1} {x2},{y2}"
        else:                                # horizontal
            pts=f"{x1},{y1} {x2},{y2}"
        out.append(f'<polyline points="{pts}" fill="none" stroke="#5B6B86" stroke-width="1.6" marker-end="url(#ar)"/>')
    # boxes + text
    for n in nodes:
        out.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" rx="7" '
                   f'fill="{n["fill"]}" stroke="{n["stroke"]}" stroke-width="1.4"/>')
        lines=n["lines"]; cx=n["x"]+n["w"]/2
        gap=[ (sz+5) for (_,sz,_,_) in lines]
        total=sum(gap); cy=n["y"]+n["h"]/2 - total/2 + gap[0]/2
        y=cy
        for (t,sz,b,col) in lines:
            if t!="":
                out.append(f'<text x="{cx}" y="{y+sz*0.35:.1f}" text-anchor="middle" font-size="{sz}" '
                           f'fill="{col}" font-weight="{"bold" if b else "normal"}">{_html.escape(t)}</text>')
            y+=sz+5
    out.append('</svg>')
    return "\n".join(out)

# ============================ FIGURE 3.1 — cart pipeline ============================
def fig_pipeline():
    W,Hh=1240,320
    stages=[
      ("Manifest & Instrument","Builds a static manifest and","instruments transpilation, so","pass stages are observed."),
      ("Events & Cohorts","Constructs change-events,","assigns non-pooled cohorts,","and a mutation engine."),
      ("Tiered Oracles","Applies width-tiered oracles","to produce write-once","ground-truth labels."),
      ("Selection & Baselines","Runs the transparent","risk_score selector against","five baselines under a budget."),
      ("Metrics & Gates","Computes the metric suite","and enforces six validity","gates before any result."),
    ]
    nodes=[]; x=20; w=210; step=247.5
    for i,(title,*body) in enumerate(stages):
        lines=[(f"{i+1}.  {title}",13,True,DARK),("",5,False,DARK)]+[(b,10.5,False,SUB) for b in body]
        nodes.append(dict(id=f"s{i}",x=x,y=30,w=w,h=120,fill=BLUE[0],stroke=BLUE[1],lines=lines)); x+=step
    nodes.append(dict(id="sub",x=20,y=210,w=1200,h=80,fill=GRAY[0],stroke=GRAY[1],lines=[
        ("Shared reproducibility substrate",13,True,DARK),
        ("two-layer execution environment  ·  write-once artifacts  ·  CPU-time cost calibration",10.5,False,SUB),
        ("frozen change-stage map  ·  group-level temporal split  ·  strict claim-scope rule",10.5,False,SUB)]))
    edges=[]
    for i in range(4):
        edges.append(dict(src=f"s{i}",dst=f"s{i+1}",exit=(1,0.5),entry=(0,0.5)))
    for i in range(5):
        cx=nodes[i]["x"]+nodes[i]["w"]/2; entryx=(cx-20)/1200
        edges.append(dict(src=f"s{i}",dst="sub",exit=(0.5,1),entry=(round(entryx,3),0)))
    return "Figure 3.1 - cart pipeline",W,Hh,nodes,edges

# ============================ FIGURE 3.2 — research framework ============================
def fig_framework():
    W,Hh=1000,620
    nodes=[
      dict(id="prob",x=290,y=20,w=420,h=66,fill=BLUE[0],stroke=BLUE[1],lines=[
        ("ONE PROBLEM",14,True,BLUETX),
        ("Regression-test the Qiskit transpiler — effectively and within budget",11.5,False,DARK)]),
      dict(id="eff",x=60,y=150,w=390,h=228,fill=GREEN[0],stroke=GREEN[1],lines=[
        ("EFFECTIVENESS",14,True,DARK),("Observability-aware fault detection",11,False,SUB),("",6,False,SUB),
        ("RQ1  prevalence of the gap",12,True,GREENTX),("RQ2  gap is real and closable",12,True,GREENTX),("",6,False,SUB),
        ("Method: mine merged transpiler fixes,",11,False,SUB),
        ("fault-class-matched (contract / isolated-pass) oracles",11,False,SUB),("",6,False,SUB),
        ("Feasibility: demonstrated",12,True,GREENTX)]),
      dict(id="cost",x=550,y=150,w=390,h=228,fill=ORANGE[0],stroke=ORANGE[1],lines=[
        ("COST",14,True,DARK),("Budgeted, cost-aware test selection",11,False,SUB),("",6,False,SUB),
        ("RQ4  selector vs. baselines",12,True,ORANGETX),("(including random ordering)",11,False,SUB),("",6,False,SUB),
        ("Method: transparent risk_score,",11,False,SUB),
        ("leakage-safe temporal evaluation",11,False,SUB),("",6,False,SUB),
        ("Scale-up: powered comparison",12,True,ORANGETX)]),
      dict(id="found",x=140,y=418,w=720,h=70,fill=GREEN[0],stroke=GREEN[1],lines=[
        ("FOUNDATION — Leakage-safe validity (RQ3)",13,True,DARK),
        ("cohort separation · provenance control · six executable validity gates · operational soundness",10.5,False,SUB)]),
      dict(id="conc",x=260,y=524,w=480,h=68,fill=BLUE[0],stroke=BLUE[1],lines=[
        ("CONCLUSION",13,True,BLUETX),
        ("The observability gap is real, common, and closable, and the",11,False,DARK),
        ("methodology is realisable and evaluated honestly.",11,False,DARK)]),
    ]
    edges=[
      dict(src="prob",dst="eff",exit=(0.5,1),entry=(0.5,0)),
      dict(src="prob",dst="cost",exit=(0.5,1),entry=(0.5,0)),
      dict(src="eff",dst="found",exit=(0.5,1),entry=(0.28,0)),
      dict(src="cost",dst="found",exit=(0.5,1),entry=(0.72,0)),
      dict(src="found",dst="conc",exit=(0.5,1),entry=(0.5,0)),
    ]
    return "Figure 3.2 - research framework",W,Hh,nodes,edges

def build(spec, stem):
    name,W,Hh,nodes,edges=spec
    open(os.path.join(HERE,stem+".drawio"),"w",encoding="utf-8").write(drawio(name,W,Hh,nodes,edges))
    s=svg(W,Hh,nodes,edges)
    open(os.path.join(HERE,stem+".svg"),"w",encoding="utf-8").write(s)
    try:
        import cairosvg
        cairosvg.svg2png(bytestring=s.encode(),write_to=os.path.join(HERE,stem+".png"),output_width=W*2)
        print("wrote",stem,".drawio/.svg/.png")
    except Exception as ex:
        print("wrote",stem,".drawio/.svg (PNG skipped:",ex,")")

if __name__=="__main__":
    build(fig_pipeline(),"figure_3_1_pipeline")
    build(fig_framework(),"figure_3_2_framework")
