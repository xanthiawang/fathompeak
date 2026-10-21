"""Hand-drawn single-line doodles for the console (key, solar panel + sun, book, signpost, boxes, price tag).
Shapes are plain geometry; each stroke is densified, wobbled along its normal with smooth noise,
given small end overshoots, and written as a Catmull-Rom cubic path. Output: doodle/<name>.svg + doodles.json"""
import math, json, random, sys
R=random.Random(20261014)
def dens(pts,step=3.0):
    out=[pts[0]]
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        d=math.hypot(x1-x0,y1-y0); n=max(1,int(d/step))
        for i in range(1,n+1): out.append((x0+(x1-x0)*i/n,y0+(y1-y0)*i/n))
    return out
def wobble(pts,amp=1.1,over=2.2):
    pts=dens(pts); L=len(pts)
    ph=[R.random()*6.28 for _ in range(3)]; fr=[R.uniform(.9,1.6),R.uniform(2.5,4),R.uniform(6,9)]
    out=[]
    for i,(x,y) in enumerate(pts):
        a=pts[max(0,i-1)]; b=pts[min(L-1,i+1)]; dx,dy=b[0]-a[0],b[1]-a[1]; d=math.hypot(dx,dy) or 1
        nx,ny=-dy/d,dx/d; t=i/max(1,L-1)
        o=amp*(.6*math.sin(fr[0]*t*6.28+ph[0])+.3*math.sin(fr[1]*t*6.28+ph[1])+.1*math.sin(fr[2]*t*6.28+ph[2]))
        out.append((x+nx*o,y+ny*o))
    def ext(p,q,k):
        dx,dy=p[0]-q[0],p[1]-q[1]; d=math.hypot(dx,dy) or 1; return (p[0]+dx/d*k,p[1]+dy/d*k)
    if over and L>3: out=[ext(out[0],out[3],R.uniform(0,over))]+out+[ext(out[-1],out[-4],R.uniform(0,over))]
    return out
def path(pts):
    p=pts[::2] if len(pts)>8 else pts
    if p[-1]!=pts[-1]: p.append(pts[-1])
    s=f"M{p[0][0]:.1f} {p[0][1]:.1f}"
    for i in range(len(p)-1):
        p0=p[max(0,i-1)];p1=p[i];p2=p[i+1];p3=p[min(len(p)-1,i+2)]
        c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6); c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
        s+=f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return s
def circle(cx,cy,r,a0=0,sweep=2*math.pi+.35,n=40):
    return [(cx+r*math.cos(a0+sweep*i/n),cy+r*math.sin(a0+sweep*i/n)) for i in range(n+1)]
def ell(cx,cy,rx,ry,a0=0,sweep=2*math.pi+.3,n=40):
    return [(cx+rx*math.cos(a0+sweep*i/n),cy+ry*math.sin(a0+sweep*i/n)) for i in range(n+1)]
def rect(x,y,w,h): return [(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y+1.5)]
def strokes_to_svg(strokes,vb,amp=1.1):
    d=' '.join(path(wobble(s,amp)) for s in strokes)
    return d
D={}
# key (empty state) 120x120
key=[circle(38,60,21,a0=-.7),circle(38,60,7,a0=1),[(58,52),(106,38)],[(61,64),(108,50)],[(106,38),(108,50)],[(80,57),(83,72),(91,70),(88,55)],[(95,53),(97,63),(102,62),(101,51)]]
spark=[[(98,14),(98,26)],[(92,20),(104,20)],[(20,98),(20,106)],[(16,102),(24,102)]]
D['key']=('0 0 120 120',key+spark)
# solar panel + sun (orders) 120x120
sun=[circle(84,30,11,a0=.3)]+[[(84+16*math.cos(a),30+16*math.sin(a)),(84+22*math.cos(a),30+22*math.sin(a))] for a in [i*math.pi/4+.2 for i in range(8)]]
panel=[[(16,80),(60,66),(86,84),(42,100),(16,80)],[(30,75),(56,92)],[(45,70),(71,88)],[(29,90),(73,75)],[(42,98),(42,112)],[(58,92),(60,110)],[(30,114),(72,108)]]
D['solar']=('0 0 120 120',sun+panel)
# book (docs) 240x120
book=[[(70,40),(118,32),(120,98),(72,104),(70,40)],[(120,32),(170,40),(168,104),(120,98)],[(80,52),(110,47)],[(80,62),(110,57)],[(80,72),(104,68)],[(130,48),(160,53)],[(130,58),(160,63)],[(130,68),(152,72)],[(60,108),(178,110)]]
D['book']=('0 0 240 120',book)
# signpost (guides)
sign=[[(118,26),(120,112)],[(80,34),(150,30),(162,40),(150,50),(80,52),(80,34)],[(158,62),(92,60),(80,70),(92,80),(158,80),(158,62)],[(92,112),(150,110)]]
D['sign']=('0 0 240 120',sign)
# boxes (model catalog)
def box(x,y,w,h,dz):
    return [[(x,y),(x+w,y-dz*.45),(x+w+dz,y),(x+dz,y+dz*.45),(x,y)],[(x,y),(x,y+h)],[(x+dz,y+dz*.45),(x+dz,y+dz*.45+h)],[(x+w+dz,y),(x+w+dz,y+h)],[(x,y+h),(x+dz,y+dz*.45+h),(x+w+dz,y+h)]]
D['boxes']=('0 0 240 120',box(56,62,40,26,34)+box(116,52,44,30,36)+box(90,26,34,20,28))
# price tag (pricing)
tag=[[(96,36),(150,30),(178,60),(150,96),(96,92),(96,36)],circle(112,50,5,a0=.5),[(112,45),(92,20),(70,16)],[(124,66),(150,64)],[(124,76),(142,75)]]
D['tag']=('0 0 240 120',tag)
out={}
for k,(vb,st) in D.items():
    d=strokes_to_svg(st,vb,amp=1.0 if vb.endswith('120 120') else 1.2)
    out[k]={'vb':vb,'d':d}
    open(f'doodle/{k}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}"><rect width="100%" height="100%" fill="#E3ECF8"/><path d="{d}" fill="none" stroke="#141416" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
json.dump(out,open('doodle/doodles.json','w'))
print({k:len(v['d']) for k,v in out.items()})
