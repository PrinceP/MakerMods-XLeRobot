import os; os.environ.setdefault("PYOPENGL_PLATFORM","egl")
import numpy as np, trimesh, pyrender, xml.etree.ElementTree as ET
from PIL import Image
URDF=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","urdf","xlerobot.urdf")
MESHDIR=os.path.dirname(URDF)
def rpy2m(r,p,y):
    cr,sr,cp,sp,cy,sy=np.cos(r),np.sin(r),np.cos(p),np.sin(p),np.cos(y),np.sin(y)
    return np.array([[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr],[sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr],[-sp,cp*sr,cp*cr]])
def T(xyz=(0,0,0),rpy=(0,0,0)):
    M=np.eye(4);M[:3,:3]=rpy2m(*rpy);M[:3,3]=xyz;return M
def axang(ax,a):
    ax=np.asarray(ax,float);ax/=np.linalg.norm(ax);M=np.eye(4)
    M[:3,:3]=trimesh.transformations.rotation_matrix(a,ax)[:3,:3];return M
def parse(s,d): return [float(v) for v in s.split()] if s else d
class Robot:
    def __init__(s):
        r=ET.parse(URDF).getroot()
        s.mat={m.get("name"):parse(m.find("color").get("rgba"),None) for m in r.findall("material") if m.find("color") is not None}
        s.vis={}
        for l in r.findall("link"):
            vs=[]
            for v in l.findall("visual"):
                g=v.find("geometry/mesh")
                if g is None or not g.get("filename").endswith(".stl"): continue
                o=v.find("origin"); mo=T(parse(o.get("xyz") if o is not None else None,[0,0,0]),parse(o.get("rpy") if o is not None else None,[0,0,0]))
                m=v.find("material"); c=m.find("color") if m is not None else None
                rgba=parse(c.get("rgba"),None) if c is not None else s.mat.get(m.get("name"),[.7,.7,.7,1])
                vs.append(dict(file=g.get("filename"),origin=mo,scale=parse(g.get("scale"),[1,1,1]),rgba=rgba))
            s.vis[l.get("name")]=vs
        s.joints={}
        for j in r.findall("joint"):
            o=j.find("origin");a=j.find("axis")
            s.joints[j.find("child").get("link")]=dict(name=j.get("name"),type=j.get("type"),parent=j.find("parent").get("link"),
              origin=T(parse(o.get("xyz") if o is not None else None,[0,0,0]),parse(o.get("rpy") if o is not None else None,[0,0,0])),
              axis=parse(a.get("xyz") if a is not None else None,[1,0,0]))
    def fk(s,q={}):
        X={}
        def get(l):
            if l in X: return X[l]
            if l not in s.joints: X[l]=np.eye(4); return X[l]
            j=s.joints[l]; M=get(j["parent"])@j["origin"]
            v=q.get(j["name"],0.0)
            if j["type"] in("revolute","continuous"): M=M@axang(j["axis"],v)
            elif j["type"]=="prismatic": M=M.copy(); M[:3,3]+= M[:3,:3]@(np.array(j["axis"])*v)
            X[l]=M;return M
        for l in s.vis: get(l)
        return X
_cache={}
def loadmesh(f,scale=(1,1,1)):
    k=(f,tuple(scale))
    if k not in _cache:
        m=trimesh.load(os.path.join(MESHDIR,f)); m.apply_scale(scale); _cache[k]=m
    return _cache[k]
def look_at(eye,target,up=(0,0,1)):
    eye,target,up=map(lambda v:np.asarray(v,float),(eye,target,up))
    f=target-eye;f/=np.linalg.norm(f);r=np.cross(f,up);r/=np.linalg.norm(r);u=np.cross(r,f)
    M=np.eye(4);M[:3,0]=r;M[:3,1]=u;M[:3,2]=-f;M[:3,3]=eye;return M
