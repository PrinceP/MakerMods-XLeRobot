import sys,pickle; import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from rlib import *
SRC={"dark":[.09,.09,.10,1],"grey":[.52,.55,.58,1],"light":[.90,.90,.88,1]}
def classify(c,e,col):
    x,y,z=c; big=e.max()
    if z<0.2:
        if col=="light" and big>0.3: return "cart"            # tubes, bottom basket
        if abs(x)>0.12 and abs(y)>0.15: return "cart"        # casters
        if abs(y)>0.19: return "cart"
        if z>0.125 and col=="light" and big<0.2 and big>0.15: return "clamp_top"
        if z>0.135: return "hub"
        if col!="dark" and (np.hypot(x,y)<0.085 or big>0.2): return "hub"
        a=np.degrees(np.arctan2(y,x))
        if -60<a<60: return "wheel0"
        return "wheel1" if a>=60 else "wheel2"
    if col=="light" and big>0.2 and z<0.75: return "cart"
    if z<0.66: return "cart"
    if x>-0.14 and abs(y)<0.065 and z>0.76: return "neck"
    if abs(y)>0.065 and z>0.70: return "armmount_L" if y>0 else "armmount_R"
    if x<-0.14: return "rear_elec"
    return "top_misc"
groups={}
for col in SRC:
    m=loadmesh(f"meshes/makermods_base_{col}.stl")
    for p in m.split(only_watertight=False):
        g=classify(p.centroid,p.extents,col)
        groups.setdefault(g,{}).setdefault(col,[]).append(p)
out={g:{c:trimesh.util.concatenate(v) for c,v in d.items()} for g,d in groups.items()}
for g,d in out.items():
    b=trimesh.util.concatenate(list(d.values())).bounds
    print(g, {c:len(m.faces) for c,m in d.items()}, np.round(b,3).tolist())
pickle.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"base_groups.pkl"),"wb"))
