"""Assembly animation of the MakerMods XLeRobot from the URDF.

usage: assemble.py OUT.mp4 [--w 1920 --h 1080 --ss 2 --fps 30 --t0 0 --t1 END --stills a,b,c]
"""
import sys, os, pickle, argparse, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rlib import *
from PIL import ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--ss", type=float, default=2.0); ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--t0", type=float, default=0); ap.add_argument("--t1", type=float, default=None)
ap.add_argument("--stills", default="")
A = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- colours
COL = {"dark": [.10, .10, .11, 1], "grey": [.50, .53, .56, 1], "light": [.88, .88, .86, 1]}
CART = [.70, .72, .74, 1]
def mat(rgba, rough=.6, metal=0.):
    return pyrender.MetallicRoughnessMaterial(baseColorFactor=rgba, roughnessFactor=rough, metallicFactor=metal)
def pmesh(tm, rgba, **k):
    tm = trimesh.Trimesh(tm.vertices, tm.faces, process=False)
    return pyrender.Mesh.from_trimesh(tm, smooth=False, material=mat(rgba, **k))

def ease(u):  # ease-out cubic with clamp
    u = min(max(u, 0.), 1.); return 1 - (1 - u) ** 3
def smooth(u):
    u = min(max(u, 0.), 1.); return u * u * (3 - 2 * u)

R = Robot()
BUILD_Q = {}
for sfx in ("", "_2"):
    BUILD_Q.update({"Pitch" + sfx: 0.8, "Elbow" + sfx: 1.4, "Wrist_Pitch" + sfx: 0.6, "Jaw" + sfx: 0.35})

# ---------------------------------------------------------------- timeline
T_TITLE, T_A, T_E, T_CART, T_D, T_C, T_B, T_FIN, T_END = 0, 4, 9, 22, 29, 41, 51, 73, 87
if A.t1 is None: A.t1 = T_END

parts = []  # dict(nodes=[(node, local)], link or None, t0, dur, off(xyz))
scene = pyrender.Scene(bg_color=[0.955, 0.958, 0.965, 1.0], ambient_light=[.22, .22, .24])

def add_part(meshes, t0, dur, off, link=None, spin=0.0):
    nodes = []
    for tm, rgba, local in meshes:
        n = scene.add(pmesh(tm, rgba), pose=np.eye(4)); nodes.append((n, local))
    parts.append(dict(nodes=nodes, link=link, t0=t0, dur=dur, off=np.array(off, float), spin=spin))

# floor
BG = [0.955, 0.958, 0.965]
floor = trimesh.creation.box([60, 60, 0.01]); floor.apply_translation([0, 0, -0.0055])
scene.add(pyrender.Mesh.from_trimesh(floor, material=pyrender.MetallicRoughnessMaterial(baseColorFactor=[0,0,0,1], emissiveFactor=BG, metallicFactor=0, roughnessFactor=1)))

# soft contact shadow: blurred top-down silhouette of the base footprint
from PIL import ImageFilter
def make_shadow(allm=None):
    ext = 0.6; N = 512
    if allm is None:
        allm = trimesh.util.concatenate([trimesh.load(os.path.join(MESHDIR, "meshes", f"makermods_base_{c}.stl")) for c in ("dark", "grey", "light")])
    img = Image.new("L", (N, N), 0); d = ImageDraw.Draw(img)
    v = allm.vertices; w = np.clip(1.0 - v[:, 2] / 0.9, 0.15, 1.0)  # low parts darker
    px = ((v[:, :2] + ext) / (2 * ext) * N)
    tri = allm.faces
    for f in tri[::3]:
        pts = [(px[i, 0], N - px[i, 1]) for i in f]
        d.polygon(pts, fill=int(255 * w[f].mean()))
    img = img.filter(ImageFilter.GaussianBlur(14))
    a = np.asarray(img).astype(np.float32) / 255 * 0.45
    yy, xx = np.mgrid[0:N, 0:N]; edge = np.clip((np.minimum(np.minimum(xx, N - 1 - xx), np.minimum(yy, N - 1 - yy))) / 40.0, 0, 1)
    a *= edge
    return a  # a[row, col]: row 0 = +y edge
SHADOW_FULL = make_shadow()

# base_link groups (segmented in seg.py)
G = pickle.load(open(os.path.join(HERE, "base_groups.pkl"), "rb"))
def gmeshes(g, override=None):
    return [(m, override or COL[c], np.eye(4)) for c, m in G[g].items()]

# Phase E: omni base
add_part(gmeshes("hub"), T_E + 1.2, 1.8, [0, 0, -0.5])
for i, g in enumerate(["wheel0", "wheel1", "wheel2"]):
    b = trimesh.util.concatenate(list(G[g].values())).centroid
    d = np.array([b[0], b[1], 0]); d /= np.linalg.norm(d)
    add_part(gmeshes(g), T_E + 4.5 + i * 2.6, 2.0, d * 0.75 + [0, 0, -0.05])
add_part([(m, CART if c == "light" else COL[c], np.eye(4)) for c, m in G["cart"].items()], T_CART + .4, 2.4, [0, 0, 1.4])
add_part(gmeshes("clamp_top"), T_CART + 3.4, 1.5, [0, 0, 0.6])
SHADOW_BASE = make_shadow(trimesh.util.concatenate([m for g in ('hub', 'wheel0', 'wheel1', 'wheel2') for m in G[g].values()]))
# Phase D: top deck
add_part(gmeshes("rear_elec"), T_D + 1.0, 1.8, [-0.6, 0, 0.25])
add_part(gmeshes("top_misc"), T_D + 2.8, 1.6, [0, 0, 0.5])
add_part(gmeshes("armmount_L"), T_D + 4.6, 1.8, [0, 0.6, 0.25])
add_part(gmeshes("armmount_R"), T_D + 6.4, 1.8, [0, -0.6, 0.25])
# Phase C: neck + head
add_part(gmeshes("neck"), T_C + 0.6, 2.2, [0, 0, 0.8])
def link_meshes(l):
    return [(loadmesh(v["file"], v["scale"]), v["rgba"], v["origin"]) for v in R.vis[l]]
add_part(link_meshes("head_pan_link"), T_C + 4.0, 1.6, [0, 0, 0.45], link="head_pan_link")
add_part(link_meshes("head_tilt_link"), T_C + 5.8, 1.6, [0.0, 0, 0.45], link="head_tilt_link")
# Phase B: arms, link by link, both sides in parallel
CHAIN = ["Base", "Rotation_Pitch", "Upper_Arm", "Lower_Arm", "Wrist_Pitch_Roll", "Fixed_Jaw", "Moving_Jaw"]
for k, l in enumerate(CHAIN + ["CAM"]):
    for sfx, side in (("", -1), ("_2", 1)):
        name = ("Right_Arm_Camera" if sfx == "" else "Left_Arm_Camera") if l == "CAM" else l + sfx
        t = T_B + 0.8 + k * 2.3 + (0.25 if sfx else 0)
        add_part(link_meshes(name), t, 1.5, [0.05, side * 0.45, 0.35], link=name)

# ---------------------------------------------------------------- captions
CAPS = [  # (t0, t1, kicker, title, lines)
    (T_A, T_E, "PHASE A", "Motor IDs and calibration prep",
     ["Label all 29 Feetech STS3215 motors (L1–L8, R1–R9, TL1–6, TR1–6)",
      "Set both jumpers on each Waveshare driver board to Channel B (USB)",
      "Connect one motor at a time: unique ID, 1,000,000 baud"]),
    (T_E, T_E + 4.3, "PHASE E", "Omni-wheel base: mounting hub",
     ["Hexagonal hub that holds the three wheel modules",
      "Load M3 / M5 square nuts into the side-sliding nut traps first"]),
    (T_E + 4.3, T_CART, "PHASE E", "Three bearing-supported wheel modules",
     ["Omni-wheel clamped between hub adapters: 3× SHCS M5×45 + M5 square nuts",
      "C018 servo (IDs 7, 8, 9) drives the hub: 1× FHCS M3×20 on the spline",
      "Idle side: 1× SHCS M5×20 through the bearing into the idle hub",
      "Daisy-chain ID 9 → 8 → 7 to the Right Control Board"]),
    (T_CART, T_D, "PHASE E", "Clamp the base under the IKEA RÅSKOG cart",
     ["Stock three-tier cart: snip single “X” openings in the mesh for cables",
      "Modules clamp under the bottom mesh: 21× FHCS M3×16 + square nuts",
      "Securing plate on top of the mesh closes the clamp"]),
    (T_D, T_D + 4.4, "PHASE D", "Top base: electronics enclosures",
     ["Driver boards + USB hubs on printed standoffs: 8× M2.5×6",
      "Enclosures to the top base frame: 8× FHCS M3×12 + square nuts"]),
    (T_D + 4.4, T_C, "PHASE D", "Arm corner mounts",
     ["Lock to the cart: FHCS M3×25 through the mesh",
      "4× FHCS M3×45 clamp jaws over the cart’s steel top rim",
      "Route USB / 12 V / 5264 cables down before clamping"]),
    (T_C, T_C + 3.8, "PHASE C", "Two-part neck",
     ["Join neck halves: 4× FHCS M3×30 + square nuts",
      "Neck pedestal to top base: 4× FHCS M3×30"]),
    (T_C + 3.8, T_B, "PHASE C", "Pan / tilt head",
     ["Pan servo ID 7, tilt servo ID 8 (C018): M2×6 + M3×6",
      "Head camera bracket on ID 8: FHCS M3×8 (+ 2× hex nut M3)",
      "Route the 3-pin cable inside the neck channel"]),
    (T_B, T_B + 11.8, "PHASE B", "SO-101 follower arms, joint by joint",
     ["Joints 1–4 & 6: both horns (top horn M3×6), motor 4× M2×6",
      "Attach each link with 4× M3×6 per side",
      "Joint 5 (wrist roll): one horn, 2× M2×6 front screws",
      "Right arm IDs 1–6 (right board) · left arm IDs 1–6 (left board)"]),
    (T_B + 11.8, T_FIN, "PHASE B", "Wrist cameras",
     ["Camera PCB to faceplate: 4× M2×6",
      "Bracket clamps on the wrist: 2× FHCS M3×10 + hex nuts per arm",
      "Leave a 4–5 cm cable loop for wrist roll"]),
    (T_FIN + 1, T_END - 0.5, "DONE", "MakerMods XLeRobot",
     ["29 STS3215 servos · keep 12 V (C018) and 7.4 V leader buses separate",
      "Next: run the auto-calibration script, then LeRobot / XLeRobot setup"]),
]
FD = "/usr/share/fonts/truetype/dejavu/"
F_K = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", int(A.h * 0.019))
F_T = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", int(A.h * 0.034))
F_L = ImageFont.truetype(FD + "DejaVuSans.ttf", int(A.h * 0.021))
F_BIG = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", int(A.h * 0.062))
F_SUB = ImageFont.truetype(FD + "DejaVuSans.ttf", int(A.h * 0.026))
ACC = (232, 93, 36)

def overlay(img, t):
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    if t < T_A:  # title
        a = int(255 * min(smooth(t / 0.8), smooth((T_A - t) / 0.8)))
        d.text((W / 2, H * .40), "MakerMods XLeRobot", font=F_BIG, fill=(25, 27, 30, a), anchor="mm")
        d.text((W / 2, H * .48), "Assembly overview · 3D animation from the URDF", font=F_SUB, fill=(80, 84, 90, a), anchor="mm")
        return
    for t0, t1, kick, title, lines in CAPS:
        if not (t0 <= t < t1): continue
        a = min(smooth((t - t0) / 0.4), smooth((t1 - t) / 0.4))
        pad = int(H * .022); x0 = int(W * .035); lh = int(H * .033)
        bw = int(max([d.textlength(title, font=F_T)] + [d.textlength("•  " + s, font=F_L) for s in lines])) + 2 * pad
        bh = pad * 2 + int(H * .03) + int(H * .045) + lh * len(lines)
        y0 = int(H * .045)
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=int(H * .012), fill=(255, 255, 255, int(225 * a)))
        d.rectangle([x0, y0 + pad, x0 + 5, y0 + bh - pad], fill=ACC + (int(255 * a),))
        y = y0 + pad
        d.text((x0 + pad, y), kick, font=F_K, fill=ACC + (int(255 * a),)); y += int(H * .03)
        d.text((x0 + pad, y), title, font=F_T, fill=(20, 22, 25, int(255 * a))); y += int(H * .048)
        for s in lines:
            d.text((x0 + pad, y), "•  " + s, font=F_L, fill=(55, 58, 64, int(255 * a))); y += lh
    # footer
    d.text((W - int(W * .02), H - int(H * .025)), "Subsystem-level animation from MakerMods’ URDF (Apache-2.0) · fasteners from the repo guide · not to scale",
           font=ImageFont.truetype(FD + "DejaVuSans.ttf", int(H * .014)), fill=(120, 124, 130, 200), anchor="rs")
    # phase progress strip
    phases = [("A", T_A, T_E), ("E", T_E, T_D), ("D", T_D, T_C), ("C", T_C, T_B), ("B", T_B, T_FIN)]
    xs = W - int(W * .035); y = int(H * .05); r = int(H * .022)
    for i, (p, a0, a1) in enumerate(reversed(phases)):
        cx = xs - i * int(r * 2.8)
        done = t >= a1; cur = a0 <= t < a1
        fill = ACC + (255,) if cur else ((60, 64, 70, 255) if done else (255, 255, 255, 230))
        d.ellipse([cx - r, y - r, cx + r, y + r], fill=fill, outline=(60, 64, 70, 255) if not cur else None, width=2)
        d.text((cx, y), p, font=F_K, fill=(255, 255, 255, 255) if (cur or done) else (60, 64, 70, 255), anchor="mm")

# ---------------------------------------------------------------- camera
KEYS = [  # t, azimuth deg, elevation deg, distance, target
    (0, 30, 16, 3.4, (0, 0, .55)),
    (T_E - 1.5, 40, 25, 2.4, (0, 0, .35)),
    (T_E + 1.0, 50, 32, 0.95, (0, 0, .06)),
    (T_CART - 0.5, 190, 30, 0.95, (0, 0, .06)),
    (T_CART + 1.5, 215, 16, 2.6, (0, 0, .5)),
    (T_D - 1.0, 200, 22, 2.3, (0, 0, .5)),
    (T_D + 0.5, 200, 38, 1.55, (-.05, 0, .74)),
    (T_C - 1, 140, 34, 1.55, (-.05, 0, .74)),
    (T_C + 0.5, 120, 18, 1.45, (-.06, 0, .93)),
    (T_B - 1, 60, 18, 1.35, (-.06, 0, .98)),
    (T_B + 0.5, 35, 28, 1.75, (-.05, 0, .82)),
    (T_FIN - 2, -40, 28, 1.75, (-.05, 0, .82)),
    (T_FIN + 1, -30, 16, 2.45, (0, 0, .64)),
    (T_END, 330, 16, 2.45, (0, 0, .64)),
]
def camera(t):
    for (ta, *a), (tb, *b) in zip(KEYS, KEYS[1:]):
        if ta <= t <= tb: break
    u = smooth((t - ta) / max(tb - ta, 1e-6))
    az = a[0] + (b[0] - a[0]) * u; el = a[1] + (b[1] - a[1]) * u; ds = a[2] + (b[2] - a[2]) * u
    tg = np.array(a[3]) + (np.array(b[3]) - np.array(a[3])) * u
    az, el = np.radians(az), np.radians(el)
    eye = tg + ds * np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    M = look_at(eye, tg)
    k = 0.0 if t < T_A else 0.13 * smooth((t - T_A) / 1.5)
    M[:3, 3] -= M[:3, 0] * k * ds
    return M

# ---------------------------------------------------------------- joints over time
def qpose(t):
    q = dict(BUILD_Q)
    if t > T_FIN + 1.5:
        s = t - (T_FIN + 1.5); g = smooth(s / 1.5)
        for sfx, ph in (("", 0), ("_2", np.pi)):
            q["Rotation" + sfx] = g * 0.45 * np.sin(0.9 * s + ph)
            q["Pitch" + sfx] = 0.8 + g * 0.35 * np.sin(1.1 * s + ph)
            q["Elbow" + sfx] = 1.4 - g * 0.4 * np.sin(1.1 * s + ph + .5)
            q["Wrist_Roll" + sfx] = g * 0.8 * np.sin(1.3 * s + ph)
            q["Jaw" + sfx] = 0.35 + g * 0.35 * np.sin(2.0 * s + ph)
        q["head_pan_joint"] = g * 0.5 * np.sin(0.7 * s)
        q["head_tilt_joint"] = g * 0.2 * np.sin(0.9 * s)
    return q

# ---------------------------------------------------------------- lights
key = pyrender.DirectionalLight(color=[1, .98, .95], intensity=2.2)
scene.add(key, pose=look_at((1.5, 1.0, 3.0), (0, 0, 0)))
fill = pyrender.DirectionalLight(color=[.9, .93, 1], intensity=0.9)
fill_node = scene.add(fill, pose=np.eye(4))
cam = pyrender.PerspectiveCamera(yfov=np.radians(36), aspectRatio=A.w / A.h, znear=0.02, zfar=20)
cam_node = scene.add(cam, pose=np.eye(4))
RW, RH = int(A.w * A.ss), int(A.h * A.ss)
rend = pyrender.OffscreenRenderer(RW, RH)
FLAGS = pyrender.RenderFlags.NONE

_rays = None
def apply_shadow(col, dep, P, k, SHADOW_A):
    global _rays
    if _rays is None:
        ys, xs = np.mgrid[0:RH, 0:RW].astype(np.float32)
        th = np.tan(cam.yfov / 2)
        _rays = np.stack([(2 * (xs + .5) / RW - 1) * th * (RW / RH), (1 - 2 * (ys + .5) / RH) * th, -np.ones_like(xs)], -1)
    m = dep > 0
    pc = _rays * dep[..., None]
    w = pc @ P[:3, :3].T + P[:3, 3]
    fl = m & (np.abs(w[..., 2]) < 0.003)
    N = SHADOW_A.shape[0]; ext = 0.6
    ci = ((w[..., 0] + ext) / (2 * ext) * N).astype(int); ri = (N - (w[..., 1] + ext) / (2 * ext) * N).astype(int)
    ok = fl & (ci >= 0) & (ci < N) & (ri >= 0) & (ri < N)
    out = col.astype(np.float32)
    out[ok] *= (1 - k * SHADOW_A[ri[ok], ci[ok]])[:, None]
    return out.astype(np.uint8)

def frame(t):
    X = R.fk(qpose(t))
    for p in parts:
        u = (t - p["t0"]) / p["dur"]
        vis = u >= 0
        e = ease(u)
        base = X[p["link"]] if p["link"] else np.eye(4)
        Tm = np.eye(4); Tm[:3, 3] = p["off"] * (1 - e)
        for n, local in p["nodes"]:
            n.mesh.is_visible = vis
            if vis: scene.set_pose(n, Tm @ base @ local)
    P = camera(t)
    scene.set_pose(cam_node, P); scene.set_pose(fill_node, P)
    col, dep = rend.render(scene, flags=FLAGS)
    sh = 0.0
    if t >= T_CART + 0.4:
        sh = smooth((t - (T_CART + 1.6)) / 1.2) if t < T_CART + 2.8 else 1.0
        if sh > 0: col = apply_shadow(col, dep, P, sh, SHADOW_FULL)
        if sh < 1: col = apply_shadow(col, dep, P, 1 - sh, SHADOW_BASE)
    else:
        sh = smooth((t - (T_E + 1.5)) / 1.0)   # base footprint before the cart lands
        if sh > 0: col = apply_shadow(col, dep, P, sh, SHADOW_BASE)
    img = Image.fromarray(col)
    if A.ss != 1: img = img.resize((A.w, A.h), Image.LANCZOS)
    overlay(img, t)
    return img

if A.stills:
    for s in A.stills.split(","):
        frame(float(s)).save(os.path.splitext(A.out)[0] + f"_{float(s):05.1f}.png")
    sys.exit()

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{A.w}x{A.h}",
                       "-r", str(A.fps), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", A.out], stdin=subprocess.PIPE)
n = int(round((A.t1 - A.t0) * A.fps))
for i in range(n):
    t = A.t0 + i / A.fps
    ff.stdin.write(frame(t).tobytes())
    if i % 150 == 0: print(f"{i}/{n}", flush=True)
ff.stdin.close(); ff.wait(); print("wrote", A.out)
