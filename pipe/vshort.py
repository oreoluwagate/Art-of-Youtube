# Vertical 1080x1920 short renderer.  run from the short-pack dir (e.g. eps/sh1):  python3 ../pipe/vshort.py N [N...]
import json, math, sys, os, re, subprocess, time, wave, textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, '.')
from shorts import SH
W, H, FPS, SR = 1080, 1920, 30, 44100
INFO = json.load(open('spr/info.json')); LM = json.load(open('linemap.json'))
FB = '/home/user/Poppins-Bold.ttf'
os.makedirs('vout', exist_ok=True); os.makedirs('vtmp', exist_ok=True)

# ---------- audio helpers (sfx lifted from pipe/audio.py) ----------
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio.py')).read()
src = src[src.index('def rd('):src.index('GAIN = ')]
from scipy.signal import butter, sosfilt
rng = np.random.default_rng(7)
exec(src)
GAIN = {'crunch': 1.0, 'clang': .9}

def wavlen(n):
    w = wave.open(f'wav/a{n}.wav'); return w.getnframes() / w.getframerate()

def menv(x):
    hop = SR // 30; n = int(np.ceil(len(x) / hop))
    r = np.array([np.sqrt(np.mean(x[j * hop:(j + 1) * hop + hop // 2] ** 2)) if len(x[j * hop:]) else 0 for j in range(n)])
    ref = np.percentile(r[r > .003], 85) if (r > .003).any() else 1
    lv = r / ref; op = []; st = 0; run = 0
    for v in lv:
        if st == 0 and v > .45: st = 1
        elif st == 1 and v < .28: st = 0
        run = run + 1 if st else 0
        if run > 5 and v < .8: st = 0; run = 0
        op.append(st)
    return op

def clean(t): return re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]', '', t)).strip()

# ---------- timeline ----------
def build(s):
    lines = LM[str(s['n'])]; li = 0
    cast = [c for c, _ in s['cast']]; pose = {c: p for c, p in s['cast']}
    t = 0.12; segs = []; L = []; fx = []; last = None
    for b in s['beats']:
        k = b[0]
        if k == 'S': fx.append((b[1], t + b[2]))
        elif k == 'P': pose[b[1]] = b[2]
        elif k == 'H':
            segs.append(dict(t0=t, t1=t + b[1], shot=b[2], pose=dict(pose))); last = b[2]; t += b[1]
        elif k == 'L':
            who, text, o = b[1], b[2], b[3]; n = lines[li]; li += 1
            if 'pose' in o and who in pose: pose[who] = o['pose']
            d = wavlen(n)
            shot = o.get('shot') or (('ms', who) if who in cast else (last or ('wide',)))
            hold = o.get('hold', 0); gap = 0.16
            # merge consecutive identical ms shots of the same speaker? no: each line its own seg (cheap)
            segs.append(dict(t0=t, t1=t + d + gap + hold, shot=shot, pose=dict(pose)))
            L.append(dict(n=n, who=who, t0=t, t1=t + d, text=clean(text), phone=bool(o.get('phone'))))
            last = shot; t += d + gap + hold
    assert li == len(lines), (s['n'], li, len(lines))
    total = t + 0.45; segs[-1]['t1'] = total
    return dict(segs=segs, lines=L, sfx=fx, total=total, cast=cast)

# ---------- audio mix ----------
CH = ('highpass=f=90,afftdn=nf=-32:nr=14,agate=threshold=0.008:ratio=6:attack=3:release=120,'
      'equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1.5:g=2.5,treble=g=3:f=9000,'
      'acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2')
def wr(p, x):
    w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
def mix(tl, tag):
    N = int((tl['total'] + 1) * SR); vo = np.zeros(N, np.float32); fxa = np.zeros(N, np.float32); ENV = {}
    for l in tl['lines']:
        x = rd(f"wav/a{l['n']}.wav"); ENV[l['n']] = menv(x)
        if l['phone']: x = np.tanh(bp(x, 350, 3200) * 2.2) * .55
        s0 = int(l['t0'] * SR); vo[s0:s0 + len(x)] += x[:N - s0]
    for name, t in tl['sfx']:
        x = sfx(name).astype(np.float32) * GAIN.get(name, 1.0); s0 = int(t * SR); e = min(N, s0 + len(x)); fxa[s0:e] += x[:e - s0]
    wr(f'vtmp/{tag}_vo.wav', vo); wr(f'vtmp/{tag}_fx.wav', fxa * .8)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'vtmp/{tag}_vo.wav', '-af', CH, f'vtmp/{tag}_voc.wav'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'vtmp/{tag}_voc.wav', '-i', f'vtmp/{tag}_fx.wav', '-filter_complex',
                    '[1:a]volume=0.55[f];[0:a][f]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[o]',
                    '-map', '[o]', '-ac', '2', '-t', f"{tl['total']:.3f}", f'vtmp/{tag}_mix.wav'], check=True)
    return ENV

# ---------- images ----------
_c = {}
def cover(path):
    if path not in _c:
        im = Image.open(path).convert('RGB'); iw, ih = im.size; z = max(W / iw, H / ih)
        im = im.resize((math.ceil(iw * z), math.ceil(ih * z)), Image.LANCZOS); x0 = (im.size[0] - W) // 2; y0 = (im.size[1] - H) // 2
        _c[path] = im.crop((x0, y0, x0 + W, y0 + H))
    return _c[path]
def nm(c, p):
    n = f'{c}_{p}'
    if n in INFO: return n
    if f'{c}_extra' in INFO and p not in ('neutral',) and c not in ('max', 'ben', 'kevin'): return f'{c}_extra'
    if f'{c}_neutral' in INFO: return f'{c}_neutral'
    for k in INFO:
        if k.startswith(c + '_'): return k
    raise KeyError(c)
_s = {}
def spr(name, st, h):
    k = (name, st, h)
    if k not in _s:
        bb = INFO[name][4]; im = Image.open(f'spr/{name}_{st}.png').convert('RGBA').crop(bb)
        z = h / im.size[1]; _s[k] = im.resize((max(1, round(im.size[0] * z)), h), Image.LANCZOS)
    return _s[k]
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)

# shot layouts: list of (char, center_x, feet_y, height)
def layout(sh, cast):
    k = sh[0]
    if k in ('ms', 'stare'):
        return [(sh[1], 540, 2060, 1760)] if sh[1] in cast else layout(('wide',), cast)
    if k == 'two':
        a, b = sh[1], sh[2]; return [(a, 285, 1840, 1180), (b, 795, 1840, 1180)]
    n = len(cast); h = {1: 1500, 2: 1180, 3: 1020, 4: 900}.get(n, 850)
    xs = {1: [540], 2: [285, 795], 3: [190, 540, 890], 4: [150, 410, 670, 930]}.get(n) or [int(W * (i + .5) / n) for i in range(n)]
    return [(c, x, 1830, h) for c, x in zip(cast, xs)]
BGZ = {'ms': 1.22, 'stare': 1.22, 'two': 1.08, 'wide': 1.0}

_sh = {}
def shadow(w):
    w = max(40, int(w * .75) // 4 * 4)
    if w not in _sh:
        s = Image.new('L', (w + 60, 90), 0); ImageDraw.Draw(s).ellipse((30, 28, w + 30, 62), fill=100)
        _sh[w] = s.filter(ImageFilter.GaussianBlur(10))
    return _sh[w]

def font(sz): return ImageFont.truetype(FB, sz)
_card = {}
def card(sh, setname):
    key = repr(sh)
    if key in _card: return _card[key]
    _, kind, title, lines = sh
    bg = cover(f'assets/vset_{setname}.png').filter(ImageFilter.GaussianBlur(18))
    bg = Image.blend(bg, Image.new('RGB', (W, H), (0, 0, 0)), .45); d = ImageDraw.Draw(bg)
    sty = {'screen': ((20, 34, 52), (120, 230, 255), (230, 245, 255)), 'clipboard': ((250, 246, 230), (30, 30, 30), (40, 40, 40)),
           'nameplate': ((214, 172, 70), (25, 20, 10), (40, 30, 10)), 'review': ((255, 255, 255), (230, 160, 0), (40, 40, 40)),
           'title': ((0, 0, 0), (255, 255, 255), (255, 255, 255))}[kind]
    box = (90, 560, 990, 1360) if kind != 'nameplate' else (80, 760, 1000, 1160)
    if kind == 'title': box = (0, 0, W, H)
    d.rounded_rectangle(box, 40 if kind != 'title' else 0, fill=sty[0], outline=(0, 0, 0), width=10 if kind != 'title' else 0)
    if kind == 'clipboard': d.rounded_rectangle((390, 520, 690, 610), 20, fill=(150, 150, 150), outline=(0, 0, 0), width=8)
    f1 = font(84 if kind != 'title' else 190); y = box[1] + 90 if kind != 'title' else 820
    if kind == 'nameplate': y = box[1] + 70
    for ln in textwrap.wrap(title, 16):
        tw = d.textlength(ln, font=f1); d.text(((W - tw) / 2, y), ln, font=f1, fill=sty[1]); y += f1.size + 18
    f2 = font(58 if kind != 'nameplate' else 64); y += 30
    for ln in lines:
        ln = ln.replace('😊', ':)')
        for sub in textwrap.wrap(ln, 26):
            tw = d.textlength(sub, font=f2); x = (W - tw) / 2 if kind != 'clipboard' else box[0] + 70
            d.text((x, y), sub, font=f2, fill=sty[2]); y += f2.size + 16
    _card[key] = bg; return bg

# ---------- captions / title ----------
def chunks(l):
    ws = l['text'].upper().split(); out = []; cur = []
    for w in ws:
        cur.append(w)
        if len(cur) >= 3 or len(' '.join(cur)) >= 14 or w[-1] in '.?!,': out.append(' '.join(cur)); cur = []
    if cur: out.append(' '.join(cur))
    tot = sum(len(c) + 3 for c in out); d = l['t1'] - l['t0']; t = l['t0']; res = []
    for c in out:
        dt = d * (len(c) + 3) / tot; res.append((t, t + dt, c)); t += dt
    return res
_cap = {}
def capimg(txt):
    if txt not in _cap:
        sz = 96
        while True:
            f = font(sz); tw = ImageDraw.Draw(Image.new('L', (1, 1))).textlength(txt, font=f)
            if tw <= 980 or sz <= 56: break
            sz -= 6
        im = Image.new('RGBA', (int(tw) + 60, sz + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((30, 20), txt, font=f, fill=(255, 255, 255), stroke_width=11, stroke_fill=(0, 0, 0))
        _cap[txt] = im
    return _cap[txt]
def titleimg(title):
    f = font(70); ls = textwrap.wrap(title, 20); lh = 88
    w = int(max(ImageDraw.Draw(Image.new('L', (1, 1))).textlength(x, font=f) for x in ls)) + 90; h = lh * len(ls) + 60
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(255, 214, 0, 255), outline=(0, 0, 0, 255), width=7)
    for i, x in enumerate(ls):
        tw = d.textlength(x, font=f); d.text(((w - tw) / 2, 22 + i * lh), x, font=f, fill=(0, 0, 0))
    return im

# ---------- frame ----------
def render(s):
    tag = f"s{s['n']:02d}"; tl = build(s); ENV = mix(tl, tag); segs = tl['segs']; LS = tl['lines']
    caps = [c for l in LS for c in chunks(l)]; T0 = titleimg(s['title']); setn = s['set']
    bgp = f'assets/vset_{setn}.png'; gagp = f"assets/{s['gag']['id']}.png"
    nf = int(round(tl['total'] * FPS))
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', f'vtmp/{tag}_mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'animation', '-threads', '2',
           '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', f'vout/{tag}.mp4']
    import shutil; FD = f'vtmp/fr_{tag}'; shutil.rmtree(FD, ignore_errors=True); os.makedirs(FD); t_0 = time.time()
    for f in range(nf):
        T = f / FPS; sg = next((x for x in segs if x['t0'] <= T < x['t1']), segs[-1]); sh = sg['shot']; k = sh[0]
        u = (T - sg['t0']) / max(.01, sg['t1'] - sg['t0']); el = T - sg['t0']
        if k == 'gag':
            fr = cover(gagp).copy(); z = 1 + .10 * ease(u); cx, cy = 540, 960
        elif k == 'card':
            fr = card(sh, setn).copy(); z = 1 + .03 * ease(u); cx, cy = 540, 960
        else:
            bz = BGZ.get(k, 1.0); bg = cover(bgp)
            if bz > 1: bw, bh = W / bz, H / bz; fr = bg.transform((W, H), Image.EXTENT, ((W - bw) / 2, H - bh - 40 / bz, (W + bw) / 2, H - 40 / bz), Image.BILINEAR)
            else: fr = bg.copy()
            lay = layout(sh, tl['cast']); pos = []
            for c, x, fy, h in lay:
                p = sg['pose'].get(c, 'neutral'); name = nm(c, p)
                spk = next((l for l in LS if l['who'] == c and l['t0'] <= T < l['t1'] and not l['phone']), None)
                op = False; dy = 4 * math.sin(2 * math.pi * T / 3.1 + hash(c) % 7); dx = 2 * math.sin(2 * math.pi * T / 5.3 + hash(c) % 5)
                if spk:
                    e = ENV[spk['n']]; j = int((T - spk['t0']) * 30); op = j < len(e) and bool(e[j]); ts = T - spk['t0']
                    dy += -7 * abs(math.sin(math.pi * ts / .36)) * h / 1760
                if p == 'panicked': dx += 5 * math.sin(T * 41); dy += 3 * math.sin(T * 53)
                im = spr(name, 'o' if op else 'c', h); pos.append((im, int(x - im.size[0] / 2 + dx), int(fy - h + dy), x, fy, im.size[0]))
            for im, px, py, x, fy, w in pos:
                if fy < H + 40:
                    sd = shadow(w); fr.paste((0, 0, 0), (int(x - sd.size[0] / 2), int(fy - 45)), sd)
            for im, px, py, x, fy, w in pos: fr.paste(im, (px, py), im)
            if k == 'stare': z = 1 + .22 * ease(u); cx, cy = 540, 2060 - 1760 * .86
            elif k in ('ms',): z = 1 + .035 * ease(u); cx, cy = 540, 900
            else: z = 1 + .03 * ease(u); cx, cy = 540, 1100
            if el < .18 and k in ('ms', 'two', 'wide'): z *= 1.0 + .05 * (1 - el / .18)   # punch-in on cut
        if z > 1.001:
            bw, bh = W / z, H / z; x0 = min(max(cx - bw / 2, 0), W - bw); y0 = min(max(cy - bh / 2, 0), H - bh)
            fr = fr.transform((W, H), Image.EXTENT, (x0, y0, x0 + bw, y0 + bh), Image.BILINEAR)
        # captions
        c = next((c for c in caps if c[0] <= T < c[1]), None)
        if c:
            ci = capimg(c[2]); pop = min(1, (T - c[0]) / .08);
            if pop < 1: ci = ci.resize((max(1, int(ci.size[0] * (.85 + .15 * pop))), max(1, int(ci.size[1] * (.85 + .15 * pop)))), Image.BILINEAR)
            fr.paste(ci, (int((W - ci.size[0]) / 2), int(1330 - ci.size[1] / 2)), ci)
        if T < 3.2:
            a = 1 if T < 2.8 else 1 - (T - 2.8) / .4; ti = T0
            if T < .2: s2 = .8 + .2 * T / .2; ti = T0.resize((int(T0.size[0] * s2), int(T0.size[1] * s2)), Image.BILINEAR)
            if a < 1: ti = ti.copy(); ti.putalpha(ti.getchannel('A').point(lambda v: int(v * a)))
            fr.paste(ti, (int((W - ti.size[0]) / 2), int(250 - ti.size[1] / 2)), ti)
        fr.save(f'{FD}/{f:05d}.jpg', quality=93)
    _s.clear(); _card.clear()
    i = cmd.index('-f'); cmd[i:i + 10] = ['-framerate', str(FPS), '-i', f'{FD}/%05d.jpg']
    subprocess.run(cmd, check=True); shutil.rmtree(FD)
    open('vout/log.txt', 'a').write(f'{tag} {nf} frames {tl["total"]:.1f}s rendered in {time.time() - t_0:.0f}s\n')

if __name__ == '__main__':
    BY = {s['n']: s for s in SH}
    if sys.argv[1] == 'tl':
        for n in map(int, sys.argv[2:]): tl = build(BY[n]); print(n, round(tl['total'], 1), len(tl['segs']))
    else:
        for n in map(int, sys.argv[1:]): render(BY[n])
