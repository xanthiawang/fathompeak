"""Generate a light dappled-shade texture for the console page header, in the FathomPeak palette.
Mimics Dia's painted hero (soft leaf-shadow mottling over a colour field) without any figurative content.
Procedural (numpy noise + blur); no data involved. Output: art/backgrounds/console-dapple_2026-10-14.webp"""
import numpy as np, sys
from PIL import Image, ImageFilter
W,H=2400,880; rng=np.random.default_rng(20261014)
def field(scale,blur,stretch=1.6):
    small=rng.random((int(H/scale)+2,int(W/(scale*stretch))+2)).astype(np.float32)
    im=Image.fromarray((small*255).astype(np.uint8)).resize((W,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
    a=np.asarray(im,dtype=np.float32)/255.
    return (a-a.min())/(a.max()-a.min()+1e-6)
# base vertical wash: mist blue -> lavender haze -> blush
stops=[(0,(169,195,232)),(.38,(201,214,236)),(.68,(227,220,230)),(1,(232,212,204))]
y=np.linspace(0,1,H)[:,None]
def interp(t):
    out=np.zeros((H,1,3),np.float32)
    for (a,ca),(b,cb) in zip(stops,stops[1:]):
        m=((t>=a)&(t<=b)); k=np.where(m,(t-a)/(b-a),0)
        out+=np.where(m[...,None],np.array(ca)*(1-k[...,None])+np.array(cb)*k[...,None],0)
    return out
base=np.repeat(interp(y),W,axis=1)
# dappled shade: layered noise thresholded softly into leaf-like patches
n=.62*field(120,46)+.28*field(48,18)+.10*field(20,7)
shade=np.clip((n-.53)/.09,0,1)          # 0 light .. 1 shade
shade=np.asarray(Image.fromarray((shade*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9)),np.float32)/255.
light=np.clip((.40-n)/.12,0,1); light=np.asarray(Image.fromarray((light*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(22)),np.float32)/255.
shadow_col=np.array([92,116,170],np.float32)   # deeper morning blue / dusk tint
light_col=np.array([248,240,236],np.float32)   # warm paper light
img=base*(1-.36*shade[...,None])+shadow_col*(.36*shade[...,None])
img=img*(1-.55*light[...,None])+light_col*(.55*light[...,None])
# soft vignette toward the top corners, and paper grain
xx=np.linspace(-1,1,W)[None,:]; yy=np.linspace(0,1,H)[:,None]
vig=np.clip(1-.10*(xx**2)*(1-yy),0,1); img*=vig[...,None]
img+= (rng.random((H,W,1)).astype(np.float32)-.5)*7
img=np.clip(img,0,255).astype(np.uint8)
out=sys.argv[1]; Image.fromarray(img).save(out,'WEBP',quality=80,method=6); print(out)
